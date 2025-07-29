from edu_rdm_integration.adapters.results import (
    WebEduFunctionResult,
    WebEduRunnerResult,
)


class BaseExportDataRunnerResult(WebEduRunnerResult):
    """Базовый класс результата работы ранера функций выгрузки данных для интеграции с РВД."""


class BaseExportDataFunctionResult(WebEduFunctionResult):
    """Базовый класс результата функции выгрузки данных для интеграции с РВД."""
