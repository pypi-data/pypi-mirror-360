from edu_rdm_integration.adapters.results import (
    WebEduFunctionResult,
    WebEduRunnerResult,
)


class BaseCollectingExportedDataRunnerResult(WebEduRunnerResult):
    """Базовый класс результатов работы ранеров функций сбора данных для интеграции с "Региональная витрина данных"."""


class BaseCollectingExportedDataFunctionResult(WebEduFunctionResult):
    """Базовый класс результатов работы функций сбора данных для интеграции с "Региональная витрина данных"."""
