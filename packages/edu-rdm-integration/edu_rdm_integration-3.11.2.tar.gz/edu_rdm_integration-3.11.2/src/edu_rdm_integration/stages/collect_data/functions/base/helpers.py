from edu_rdm_integration.adapters.helpers import (
    WebEduFunctionHelper,
    WebEduRunnerHelper,
)
from edu_rdm_integration.core.operations import (
    ALL_OPERATIONS,
    UPDATED_OPERATIONS,
)


class BaseCollectingDataRunnerHelper(WebEduRunnerHelper):
    """Базовый класс помощников ранеров функций сбора данных для интеграции с "Региональная витрина данных"."""


class BaseCollectingDataFunctionHelper(WebEduFunctionHelper):
    """Базовый класс помощников функций сбора данных для интеграции с "Региональная витрина данных"."""

    def get_filtered_operations(self, with_deleted: bool = False) -> tuple[int]:
        """Возвращает кортеж отфильтрованных операций."""
        return ALL_OPERATIONS if with_deleted else UPDATED_OPERATIONS
