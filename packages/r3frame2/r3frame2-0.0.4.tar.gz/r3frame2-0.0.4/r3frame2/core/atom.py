from .globals import inspect
from .log import R3logger

def R3private(func):
    def wrapper(*args, **kwargs):
        caller = inspect.stack()[1].frame.f_globals.get("__name__")
        if not caller.startswith("r3frame2."):
            R3logger.warning(f"Internal Method, cannot call `{func.__name__}`: (caller){caller}")
            return
        return func(*args, **kwargs)
    return wrapper

class R3atom:
    def __init__(self) -> None:
        self._flags: int = 0
        self._uid: int = id(self)

    @property
    def flags(self) -> int:
        return self._flags
    
    @property
    def uid(self) -> int:
        return self._uid

    def swap_flag(self, rem: int, set: int) -> None:
        self.rem_flag(rem)
        self.set_flag(set)

    def set_flag(self, flag: int) -> None:
        if flag < 0 or not isinstance(flag, int): return
        self._flags |= flag

    def get_flag(self, flag: int) -> bool:
        if flag < 0 or not isinstance(flag, int): return
        return ((self._flags & flag) == flag)

    def rem_flag(self, flag: int) -> None:
        if flag < 0 or not isinstance(flag, int): return
        self._flags &= ~flag

