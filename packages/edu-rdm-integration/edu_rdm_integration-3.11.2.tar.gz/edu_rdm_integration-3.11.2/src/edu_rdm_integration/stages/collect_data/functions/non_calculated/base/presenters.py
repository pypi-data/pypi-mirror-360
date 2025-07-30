from abc import (
    ABCMeta,
)

from edu_rdm_integration.adapters.presenters import (
    WebEduResultPresenter,
)


class BaseCollectingExportedDataResultPresenter(WebEduResultPresenter, metaclass=ABCMeta):
    """Презентер результата работы функций сбора данных для интеграции с "Региональная витрина данных"."""
