from django.apps import (
    AppConfig,
)


class WebEduFunctionToolsConfig(AppConfig):
    """Конфигурация приложения для интеграции с function_tools.

    Определяет основные параметры Django-приложения, которое
    обеспечивает работу с библиотекой function_tools в контексте
    продуктов Образования.

    Attributes:
        name (str): Полное имя приложения в системе Django
        verbose_name (str): Человекочитаемое название приложения
        label (str): Уникальная метка приложения для Django

    Note:
        Приложение автоматически регистрируется в Django при старте
        и обеспечивает всю необходимую инфраструктуру для работы
        с function_tools.
    """

    name = 'edu_rdm_integration.adapters.function_tools'
    verbose_name = 'Приложение для работы с function_tools'
    label = 'web_edu_function_tools'
