"""Стратегии реализации функций для интеграции с продуктами Образования.

Этот модуль содержит классы стратегий, определяющие способы реализации функций
для работы с продуктами Образования. Стратегии определяют конфигурацию классов
для различных компонентов системы: менеджеров, исполнителей, валидаторов и т.д.
"""

from abc import (
    ABCMeta,
)
from typing import (
    Optional,
)

from function_tools.strategies import (
    FunctionImplementationStrategy,
)

from edu_rdm_integration.adapters.caches import (
    WebEduFunctionCacheStorage,
    WebEduRunnerCacheStorage,
)
from edu_rdm_integration.adapters.errors import (
    WebEduError,
)
from edu_rdm_integration.adapters.functions import (
    WebEduFunction,
    WebEduLazySavingPredefinedQueueFunction,
)
from edu_rdm_integration.adapters.helpers import (
    WebEduFunctionHelper,
    WebEduRunnerHelper,
)
from edu_rdm_integration.adapters.managers import (
    WebEduRunnerManager,
)
from edu_rdm_integration.adapters.presenters import (
    WebEduResultPresenter,
)
from edu_rdm_integration.adapters.results import (
    WebEduFunctionResult,
    WebEduRunnerResult,
)
from edu_rdm_integration.adapters.runners import (
    WebEduRunner,
)
from edu_rdm_integration.adapters.validators import (
    WebEduFunctionValidator,
    WebEduRunnerValidator,
)


class WebEduFunctionImplementationStrategy(FunctionImplementationStrategy, metaclass=ABCMeta):
    """Базовая стратегия реализации функций для продуктов Образования.

    Определяет основную конфигурацию классов для всех компонентов системы:
    - Менеджеры для управления выполнением функций
    - Исполнители (runners) для запуска функций
    - Помощники (helpers) для вспомогательных операций
    - Валидаторы для проверки данных
    - Кэши для хранения промежуточных результатов
    - Обработчики ошибок и результатов

    Все методы в этом классе отвечают за установку конкретных реализаций
    различных компонентов системы.
    """

    def _prepare_manager_class(self):
        """Устанавливает класс менеджера для управления выполнением функций."""
        self._manager_class = WebEduRunnerManager

    def _prepare_runner_class(self):
        """Устанавливает класс исполнителя для запуска функций."""
        self._runner_class = WebEduRunner

    def _prepare_function_class(self):
        """Устанавливает базовый класс функции для обработки данных."""
        self._function_class = WebEduFunction

    def _prepare_runner_helper_class(self):
        """Устанавливает класс помощника для исполнителя функций."""
        self._runner_helper_class = WebEduRunnerHelper

    def _prepare_function_helper_class(self):
        """Устанавливает класс помощника для функций обработки данных."""
        self._function_helper_class = WebEduFunctionHelper

    def _prepare_runner_validator_class(self):
        """Устанавливает класс валидатора для проверки параметров исполнителя."""
        self._runner_validator_class = WebEduRunnerValidator

    def _prepare_function_validator_class(self):
        """Устанавливает класс валидатора для проверки данных функции."""
        self._function_validator_class = WebEduFunctionValidator

    def _prepare_runner_cache_storage_class(self):
        """Устанавливает класс хранилища кэша для исполнителя."""
        self._runner_cache_storage_class = WebEduRunnerCacheStorage

    def _prepare_function_cache_storage_class(self):
        """Устанавливает класс хранилища кэша для функции."""
        self._function_cache_storage_class = WebEduFunctionCacheStorage

    def _prepare_error_class(self):
        """Устанавливает класс для обработки ошибок."""
        self._error_class = WebEduError

    def _prepare_runner_result_class(self):
        """Устанавливает класс для хранения результатов работы исполнителя."""
        self._runner_result_class = WebEduRunnerResult

    def _prepare_function_result_class(self):
        """Устанавливает класс для хранения результатов работы функции."""
        self._function_result_class = WebEduFunctionResult

    def _prepare_result_presenter_class(self):
        """Устанавливает класс для представления результатов."""
        self._result_presenter_class = WebEduResultPresenter


class WebEduSyncBaseRunnerLazySavingPredefinedQueueFunctionImplementationStrategy(
    WebEduFunctionImplementationStrategy, metaclass=ABCMeta
):
    """Стратегия создания функции с отложенным сохранением и предустановленной очередью.

    Расширяет базовую стратегию, добавляя специфическую логику для:
    - Отложенного сохранения данных (lazy saving)
    - Работы с предустановленной очередью объектов
    - Синхронного выполнения операций

    Сохранение данных производится только после успешного выполнения всех операций
    функции, что обеспечивает целостность данных и атомарность операций.
    """

    def _prepare_key(self) -> str:
        """Возвращает уникальный идентификатор стратегии.

        Returns:
            str: Ключ для идентификации стратегии в системе
        """
        return 'WEB_EDU_SYNC_LAZY_SAVING_FUNCTION'

    def _prepare_title(self) -> str:
        """Возвращает название стратегии.

        Returns:
            str: Человекочитаемое описание стратегии
        """
        return (
            'Стратегия создания функции с отложенным сохранением и предустановленной очередью объектов на сохранение '
            'продуктов Образования. Сохранение производится после удачной работы функции'
        )

    @classmethod
    def _prepare_function_template_name(cls) -> Optional[str]:
        """Формирование названия шаблона создания функции.

        Returns:
            Optional[str]: Имя шаблона для создания функции или None,
            если шаблон не требуется
        """
        return 'function_sync_template'

    def _prepare_function_class(self):
        """Устанавливает класс функции с поддержкой отложенного сохранения."""
        self._function_class = WebEduLazySavingPredefinedQueueFunction
