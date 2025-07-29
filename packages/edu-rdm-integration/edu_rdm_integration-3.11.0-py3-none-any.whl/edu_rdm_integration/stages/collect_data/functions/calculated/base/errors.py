from edu_rdm_integration.adapters.errors import (
    WebEduError,
)


class BaseCollectingCalculatedExportedDataError(WebEduError):
    """Базовая ошибка функций сбора расчетных данных для интеграции с "Региональная витрина данных"."""
