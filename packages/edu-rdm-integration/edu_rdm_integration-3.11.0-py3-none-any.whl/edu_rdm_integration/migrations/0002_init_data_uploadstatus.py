# flake8: noqa
from django.db import (
    migrations,
)


def load_initial_data(apps, schema_editor):
    # Вместо модели UploadStatus создана модель-перечисление DataMartRequestStatus (см. миграцию 0004)
    pass


def delete_all_data(apps, schema_editor):
    """Удаление всех данных из модели UploadStatus при откате миграции."""
    apps.get_model('regional_data_mart_integration', 'UploadStatus').objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('edu_rdm_integration', '0001_initial'),
    ]

    operations = [migrations.RunPython(load_initial_data, reverse_code=delete_all_data)]
