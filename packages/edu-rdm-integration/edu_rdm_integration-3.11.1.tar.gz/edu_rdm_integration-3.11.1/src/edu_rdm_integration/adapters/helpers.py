from abc import (
    ABCMeta,
)

from function_tools.helpers import (
    BaseFunctionHelper,
    BaseRunnerHelper,
)

from edu_rdm_integration.adapters.caches import (
    WebEduFunctionCacheStorage,
    WebEduRunnerCacheStorage,
)


class WebEduRunnerHelper(BaseRunnerHelper, metaclass=ABCMeta):
    """Базовый класс помощников для исполнителей функций.

    Предоставляет вспомогательную функциональность для исполнителей,
    включая:
    - Кэширование данных исполнителя
    - Общие утилиты для работы с функциями
    - Доступ к разделяемым ресурсам

    Attributes:
        cache (WebEduRunnerCacheStorage): Хранилище кэша для исполнителя
    """

    def _prepare_cache_class(self) -> type[WebEduRunnerCacheStorage]:
        """Возвращает класс хранилища кэша для исполнителя.

        Returns:
            type[WebEduRunnerCacheStorage]: Класс для кэширования данных
            исполнителя
        """
        return WebEduRunnerCacheStorage


class WebEduFunctionHelper(BaseFunctionHelper, metaclass=ABCMeta):
    """Базовый класс помощников для функций обработки данных.

    Предоставляет вспомогательную функциональность для функций,
    включая:
    - Кэширование данных функции
    - Общие утилиты для обработки данных
    - Доступ к разделяемым ресурсам

    Note:
        Каждая конкретная функция может расширить этот класс,
        добавив специфичные для неё вспомогательные методы.

    Attributes:
        cache (WebEduFunctionCacheStorage): Хранилище кэша для функции
    """

    def _prepare_cache_class(self) -> type[WebEduFunctionCacheStorage]:
        """Возвращает класс хранилища кэша для функции.

        Returns:
            type[WebEduFunctionCacheStorage]: Класс для кэширования данных
            функции
        """
        return WebEduFunctionCacheStorage
