from edu_rdm_integration.adapters.errors import (
    WebEduError,
)


class BaseExportDataError(WebEduError):
    """Базовая ошибка функций выгрузки данных для интеграции с "Региональная витрина данных"."""
