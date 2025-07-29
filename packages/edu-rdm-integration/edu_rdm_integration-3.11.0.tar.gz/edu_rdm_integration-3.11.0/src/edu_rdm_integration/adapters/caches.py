from abc import (
    ABCMeta,
)

from function_tools.caches import (
    CacheStorage,
    EntityCache,
    PatchedGlobalCacheStorage,
    PeriodicalEntityCache,
)


class WebEduEntityCache(EntityCache, metaclass=ABCMeta):
    """Базовый класс кэша для сущностей продуктов Образования.

    Предоставляет механизм кэширования отдельных сущностей системы.
    Используется для:
    - Хранения часто запрашиваемых объектов
    - Снижения нагрузки на базу данных
    - Ускорения доступа к данным

    Note:
        Конкретные реализации должны определить специфику кэширования
        для каждого типа сущности.
    """


class WebEduPeriodicalEntityCache(PeriodicalEntityCache, metaclass=ABCMeta):
    """Базовый класс периодического кеша продуктов Образования.

    Кеш создается для определенной модели с указанием двух дат, на которые
    должны быть собраны кеши актуальных объектов модели.
    """


class WebEduRunnerCacheStorage(CacheStorage, metaclass=ABCMeta):
    """Базовый класс кешей помощников ранеров функций продуктов Образования."""


class WebEduFunctionCacheStorage(CacheStorage, metaclass=ABCMeta):
    """Базовый класс кешей функций продуктов Образования."""


class WebEduFunctionPatchedGlobalCacheStorage(PatchedGlobalCacheStorage, metaclass=ABCMeta):
    """Базовый класс глобального хранилища кэша с поддержкой патчинга.

    Расширяет стандартное хранилище кэша, добавляя возможность
    модификации данных через механизм патчинга. Это позволяет:
    - Обновлять кэшированные данные без полной перезагрузки
    - Синхронизировать кэш между разными компонентами
    - Эффективно управлять общими данными

    Note:
        Патчинг должен использоваться с осторожностью, чтобы избежать
        несогласованности данных между разными частями системы.
    """
