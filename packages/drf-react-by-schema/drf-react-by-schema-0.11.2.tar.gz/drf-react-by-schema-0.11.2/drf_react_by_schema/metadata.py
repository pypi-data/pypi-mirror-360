from rest_framework.metadata import BaseMetadata, SimpleMetadata
from datetime import date, datetime
import inspect
from django.forms.models import model_to_dict

from .utils import get_model


class Metadata(SimpleMetadata):
    """Overrides the standard DRF MetaData schema."""

    def determine_metadata(self, request, view):
        meta = super().determine_metadata(request, view)

        if not "actions" in meta or not "POST" in meta["actions"]:
            return meta

        serializer_fields = view.get_serializer().fields
        model = view.get_serializer().Meta.model
        verbose_name = getattr(model._meta, "verbose_name", None)
        meta["verbose_name"] = verbose_name
        verbose_name_plural = getattr(model._meta, "verbose_name_plural", None)
        meta["verbose_name_plural"] = verbose_name_plural

        # Assign "serializermethodfield" type as text and "typedserializermethodfield" as return_type
        for serializer_field_name in serializer_fields:
            serializer_field = serializer_fields.get(serializer_field_name)
            serializer_field_class_name = serializer_field.__class__.__name__
            if (
                serializer_field_name in meta["actions"]["POST"]
                and "SerializerMethodField" in serializer_field_class_name
            ):
                meta["actions"]["POST"][serializer_field_name]["type"] = (
                    serializer_field.return_type
                    if serializer_field_class_name == "TypedSerializerMethodField"
                    else "string"
                )

        for field in model._meta.get_fields():
            field_name = getattr(field, "name", None)
            serializer_field = serializer_fields.get(field_name, None)
            if field_name in meta["actions"]["POST"]:
                # Print default value in OPTIONS:
                if getattr(field, "get_default", None) and field.get_default():
                    if field.related_model and serializer_field:
                        meta["actions"]["POST"][field_name]["model_default"] = (
                            serializer_field.__class__(
                                field.related_model.objects.get(pk=field.get_default())
                            ).data
                        )
                    else:
                        meta["actions"]["POST"][field_name][
                            "model_default"
                        ] = field.get_default()
                elif getattr(field, "auto_now_add", None):
                    meta["actions"]["POST"][field_name]["model_default"] = (
                        date.today()
                        if field.__class__.__name__ == "DateField"
                        else datetime.now()
                    )
                elif getattr(field, "auto_now", None):
                    meta["actions"]["POST"][field_name]["model_default"] = (
                        date.today()
                        if field.__class__.__name__ == "DateField"
                        else datetime.now()
                    )
                elif serializer_field and serializer_field.default:
                    class_name = serializer_field.default.__class__.__name__
                    if class_name in ["int", "string"]:
                        meta["actions"]["POST"][field_name][
                            "model_default"
                        ] = serializer_field.default
                    elif class_name == "CurrentUserDefault":
                        meta["actions"]["POST"][field_name][
                            "model_default"
                        ] = "currentUser"

                # Custom regex Validators:
                validators = getattr(field, "validators", [])
                validators_regex = []
                for validator in validators:
                    regex = getattr(validator, "regex", None)
                    if regex:
                        validators_regex.append(
                            {
                                "regex": validator.regex.pattern,
                                "message": validator.message,
                            }
                        )
                if len(validators_regex) > 0:
                    meta["actions"]["POST"][field_name][
                        "validators_regex"
                    ] = validators_regex

                # Print if required in OPTIONS:
                is_required = not getattr(field, "blank", False) and not getattr(
                    serializer_field, "read_only", False
                )
                meta["actions"]["POST"][field_name]["model_required"] = is_required

                # Add related model is editable in OPTIONS:
                related_editable = getattr(field, "related_editable", None)
                if related_editable is not None:
                    meta["actions"]["POST"][field_name][
                        "related_editable"
                    ] = related_editable

                # Add DecimalField decimal_places in OPTIONS:
                decimal_places = getattr(field, "decimal_places", None)
                if decimal_places is not None:
                    meta["actions"]["POST"][field_name][
                        "decimal_places"
                    ] = decimal_places

                # Add DecimalField max_digits in OPTIONS:
                max_digits = getattr(field, "max_digits", None)
                if max_digits is not None:
                    meta["actions"]["POST"][field_name]["max_digits"] = max_digits

                # Add DecimalField is_currency in OPTIONS:
                is_currency = getattr(field, "is_currency", None)
                if is_currency is not None:
                    meta["actions"]["POST"][field_name]["is_currency"] = is_currency

                # Add DecimalField prefix in OPTIONS:
                prefix = getattr(field, "prefix", None)
                if prefix is not None:
                    meta["actions"]["POST"][field_name]["prefix"] = prefix

                # Add DecimalField suffix in OPTIONS:
                suffix = getattr(field, "suffix", None)
                if suffix is not None:
                    meta["actions"]["POST"][field_name]["suffix"] = suffix

                # Add DateField views in OPTIONS:
                views = getattr(field, "views", None)
                if views is not None:
                    meta["actions"]["POST"][field_name]["date_views"] = views

                if field_name in serializer_fields and serializer_fields[
                    field_name
                ].__class__.__name__ in ["ManyRelatedField", "ListSerializer"]:
                    meta["actions"]["POST"][field_name]["many"] = True

                # Print multiline in OPTIONS:
                if field.__class__.__name__ == "TextField":
                    meta["actions"]["POST"][field_name]["model_multiline"] = True

                # Force slug to be read_only:
                if field_name == "slug":
                    meta["actions"]["POST"][field_name]["required"] = False
                    meta["actions"]["POST"][field_name]["read_only"] = True

        return meta
