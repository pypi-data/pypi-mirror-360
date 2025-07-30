from edu_rdm_integration.adapters.validators import (
    WebEduFunctionValidator,
    WebEduRunnerValidator,
)


class BaseCollectingExportedDataRunnerValidator(WebEduRunnerValidator):
    """Базовый класс валидаторов ранеров функций сбора данных для интеграции с "Региональная витрина данных"."""

    def validate(self, runnable):
        """Выполнение валидации."""
        super().validate(runnable=runnable)


class BaseCollectingExportedDataFunctionValidator(WebEduFunctionValidator):
    """Базовый класс валидаторов функций сбора данных для интеграции с "Региональная витрина данных"."""

    def validate(self, runnable):
        """Выполнение валидации."""
        super().validate(runnable=runnable)
