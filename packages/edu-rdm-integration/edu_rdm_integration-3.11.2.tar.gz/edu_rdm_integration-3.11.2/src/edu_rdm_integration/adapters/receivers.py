from sys import (
    stdout,
)


def m3_edu_function_tools_after_migrate_receiver(sender, **kwargs):
    """Обработчик сигнала, выполняющийся после применения миграций.

    Автоматически регистрирует сущности в системе после успешного
    выполнения миграций базы данных. Это обеспечивает:
    - Синхронизацию моделей с системой регистрации
    - Корректную инициализацию новых сущностей
    - Обновление существующих регистраций

    Args:
        sender: Отправитель сигнала (обычно приложение Django)
        **kwargs: Дополнительные параметры сигнала

    Note:
        В случае возникновения ошибок при регистрации, они будут
        перехвачены и залогированы, но не будут прерывать процесс
        миграции.
    """
    from function_tools.management.commands.register_entities import (
        EntityRegistrar,
    )

    try:
        registrar = EntityRegistrar(logger=stdout)
        registrar.run()
    except Exception as e:
        stdout.write(
            f'Register function_tools_entities exception. ----- START IGNORING EXCEPTION\n{e}\n----- '
            f'FINISH IGNORING EXCEPTION\n'
        )
