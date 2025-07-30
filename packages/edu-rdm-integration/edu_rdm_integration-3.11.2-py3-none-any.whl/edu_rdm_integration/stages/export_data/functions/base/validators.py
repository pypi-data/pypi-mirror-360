from edu_rdm_integration.adapters.validators import (
    WebEduFunctionValidator,
    WebEduRunnerValidator,
)


class BaseExportDataRunnerValidator(WebEduRunnerValidator):
    """Базовый класс валидаторов ранеров функций выгрузки данных для интеграции с "Региональная витрина данных"."""

    def validate(self, runnable):
        """Выполнение валидации."""
        super().validate(runnable=runnable)


class BaseExportDataFunctionValidator(WebEduFunctionValidator):
    """Базовый класс валидаторов функций выгрузки данных для интеграции с "Региональная витрина данных"."""

    def validate(self, runnable):
        """Выполнение валидации."""
        super().validate(runnable=runnable)
