"""Базовые классы функций для интеграции с продуктами Образования.

Этот модуль содержит базовые классы функций, которые используются для создания
конкретных реализаций функций обработки данных в системе. Модуль предоставляет
различные варианты базовых классов с разными стратегиями сохранения данных
и управления очередями объектов.
"""

from abc import (
    ABCMeta,
)

from function_tools.functions import (
    BaseFunction,
    LazySavingPredefinedQueueFunction,
    LazySavingPredefinedQueueGlobalHelperFunction,
)

from edu_rdm_integration.adapters.helpers import (
    WebEduFunctionHelper,
)
from edu_rdm_integration.adapters.results import (
    WebEduFunctionResult,
)
from edu_rdm_integration.adapters.validators import (
    WebEduFunctionValidator,
)


class WebEduFunction(BaseFunction, metaclass=ABCMeta):
    """Базовый класс для создания функций продуктов Образования.

    Предоставляет основной интерфейс для создания функций обработки данных.
    Наследуется от BaseFunction и добавляет специфичную для продуктов
    Образования функциональность.

    Note:
        Этот класс является абстрактным и должен быть расширен конкретными
        реализациями функций.
    """


class WebEduLazySavingPredefinedQueueFunction(LazySavingPredefinedQueueFunction, metaclass=ABCMeta):
    """Базовый класс для создания функций с отложенным сохранением.

    Реализует паттерн отложенного сохранения (lazy saving) с предустановленной
    очередью объектов. Это позволяет:
    - Накапливать объекты для сохранения в течение выполнения функции
    - Сохранять все объекты атомарно после успешного выполнения всех операций
    - Откатывать все изменения в случае ошибки
    - Оптимизировать производительность за счет пакетного сохранения

    Attributes:
        helper (WebEduFunctionHelper): Помощник функции для вспомогательных операций
        validator (WebEduFunctionValidator): Валидатор для проверки данных
        result (WebEduFunctionResult): Объект для хранения результатов работы
    """

    def _prepare_helper_class(self) -> type[WebEduFunctionHelper]:
        """Возвращает класс помощника функции.

        Returns:
            type[WebEduFunctionHelper]: Класс помощника для работы с данными
        """
        return WebEduFunctionHelper

    def _prepare_validator_class(self) -> type[WebEduFunctionValidator]:
        """Возвращает класс валидатора функции.

        Returns:
            type[WebEduFunctionValidator]: Класс для валидации входных данных
        """
        return WebEduFunctionValidator

    def _prepare_result_class(self) -> type[WebEduFunctionResult]:
        """Возвращает класс результата функции.

        Returns:
            type[WebEduFunctionResult]: Класс для хранения результатов выполнения
        """
        return WebEduFunctionResult


class WebEduLazySavingPredefinedQueueGlobalHelperFunction(
    LazySavingPredefinedQueueGlobalHelperFunction,
    metaclass=ABCMeta,
):
    """Базовый класс для создания функций с глобальным помощником.

    Расширяет функциональность WebEduLazySavingPredefinedQueueFunction,
    добавляя поддержку глобального помощника. Это позволяет:
    - Использовать общие вспомогательные методы между разными функциями
    - Кэшировать часто используемые данные на уровне всего приложения
    - Оптимизировать использование ресурсов при массовой обработке данных

    Note:
        Глобальный помощник должен быть потокобезопасным, так как может
        использоваться одновременно несколькими функциями.
    """
