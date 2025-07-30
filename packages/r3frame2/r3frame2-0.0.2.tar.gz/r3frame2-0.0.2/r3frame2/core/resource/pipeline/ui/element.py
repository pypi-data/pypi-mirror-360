from ....atom import R3atom
from ....globals import pg
from ....utils import add_v2, div_v2
import r3frame2 as r3

# element data container -- surface assigned on database entry
# R3database.element[key] -> R3element
class R3element(R3atom):
    def __init__(
            self,
            pos: list[int] = [0, 0, 0],
            size: list[int] = [32, 32],
            rgba: list[int] = [255, 255, 255, 255],
    ) -> None:
        super().__init__()
        self.pos: list[int] = pos[:]
        self.size: list[int] = size[:]
        self.rgba: list[int] = rgba[:]
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

    @property
    def x(self) -> float:
        return self.pos[0]
    @property
    def y(self) -> float:
        return self.pos[1]
    @property
    def z(self) -> float:
        return self.pos[2]
    @property
    def c(self) -> list[float]:
        return add_v2(self.pos, div_v2(self.size, 2))
