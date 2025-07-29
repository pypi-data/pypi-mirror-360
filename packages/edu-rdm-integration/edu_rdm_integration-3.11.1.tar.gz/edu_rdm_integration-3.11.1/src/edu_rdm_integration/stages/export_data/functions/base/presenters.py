from abc import (
    ABCMeta,
)

from edu_rdm_integration.adapters.presenters import (
    WebEduResultPresenter,
)


class BaseExportDataResultPresenter(WebEduResultPresenter, metaclass=ABCMeta):
    """Презентер результата работы функций выгрузки данных для интеграции с "Региональная витрина данных"."""
