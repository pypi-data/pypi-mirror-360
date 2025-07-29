"""Commons - Model class methods."""

from .general import GeneralMixin
from .indexes import IndexMixin
from .many import ManyMixin
from .one import OneMixin
from .unit_manager import UnitMixin


class QCommonsMixin(
    GeneralMixin,
    OneMixin,
    ManyMixin,
    IndexMixin,
    UnitMixin,
):
    """Commons - Model class methods."""

    def __init__(self) -> None:  # noqa: D107
        super().__init__()
