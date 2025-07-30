from abc import (
    ABCMeta,
)

from edu_rdm_integration.adapters.presenters import (
    WebEduResultPresenter,
)


class BaseCollectingCalculatedExportedDataResultPresenter(WebEduResultPresenter, metaclass=ABCMeta):
    """Презентер результата работы функций сбора расчетных данных для интеграции с "Региональная витрина данных"."""
