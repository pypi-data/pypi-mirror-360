from edu_rdm_integration.adapters.results import (
    WebEduFunctionResult,
    WebEduRunnerResult,
)


class BaseCollectingCalculatedExportedDataRunnerResult(WebEduRunnerResult):
    """Базовый класс результатов работы ранеров функций сбора расчетных данных для РВД."""


class BaseCollectingCalculatedExportedDataFunctionResult(WebEduFunctionResult):
    """Базовый класс результатов работы функций сбора расчетных данных для интеграции с РВД."""
