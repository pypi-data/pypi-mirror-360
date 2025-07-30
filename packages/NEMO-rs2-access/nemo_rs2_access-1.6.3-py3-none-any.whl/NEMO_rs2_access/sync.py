from logging import getLogger
from typing import Dict, Type

from NEMO.utilities import distinct_qs_value_list
from django.db.models import Model

sync_logger = getLogger(__name__)


def sync_model_rest_data(data, model_class: Type[Model], remote_id_field_name: str, mapping: Dict):
    model_id_field = f"{model_class._meta.model_name}_id"
    try:
        db_data_ids = distinct_qs_value_list(model_class.objects.all(), model_id_field)
        remote_data_ids = set()
        for item in data:
            item_id = item.get(remote_id_field_name)
            remote_data_ids.add(item_id)
            defaults = {model_field: item.get(remote_field) for model_field, remote_field in mapping.items()}
            defaults["data"] = item
            model_class.objects.update_or_create(**{model_id_field: item_id}, defaults=defaults)
        to_remove = db_data_ids.difference(remote_data_ids)
        model_class.objects.filter(**{f"{model_id_field}__in": to_remove}).delete()
        if to_remove:
            sync_logger.info(f"Deleted {model_class} with ids: {', '.join(str(x) for x in to_remove)}")
    except:
        sync_logger.exception(f"Error syncing {model_class} table")
