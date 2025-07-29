from edu_rdm_integration.adapters.errors import (
    WebEduError,
)


class BaseCollectingExportedDataError(WebEduError):
    """Базовая ошибка функций сбора данных для интеграции с "Региональная витрина данных"."""
