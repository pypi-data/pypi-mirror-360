from ....atom import R3atom
from ....globals import pg
# from ..utils import 
import r3frame2 as r3

# surf data container -- surface assigned on database entry
# R3database.surf[key] -> R3surf
class R3surf(R3atom):
    def __init__(
            self,
            size: list[int] = [32, 32],
            rgba: list[int] = [255, 255, 255, 255],
            rgba_key: list[int] = [0, 0, 0, 0],
    ) -> None:
        super().__init__()
        self.size: list[int] = size[:]
        self.rgba: list[int] = rgba[:]
        self.rgba_key: list[int] = rgba_key[:]
        
        self.mask: pg.Mask = None
        self.surface: pg.Surface = None
    
    @property
    def red(self) -> int:
        return self.rgba[0]
    @property
    def green(self) -> int:
        return self.rgba[1]
    @property
    def blue(self) -> int:
        return self.rgba[2]
    @property
    def alpha(self) -> int:
        return self.rgba[3]

    @property
    def w(self) -> float:
        return self.size[0]
    @property
    def h(self) -> float:
        return self.size[1]
    @property
    def a(self) -> float:
        return self.size[0] * self.size[1]
