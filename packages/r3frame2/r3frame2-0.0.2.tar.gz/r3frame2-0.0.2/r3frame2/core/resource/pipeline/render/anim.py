from ....atom import R3atom
from ....globals import pg
# from ..utils import 
import r3frame2 as r3

# anim data container -- surfaces assigned on database entry
# R3database.anim[key] -> R3anim
class R3anim(R3atom):
    def __init__(
            self,
            size: list[int] = [32, 32],
            rgba: list[int] = [255, 255, 255, 255],
    ) -> None:
        super().__init__()
        self.size: list[int] = size[:]
        self.rgba: list[int] = rgba[:]
        self.surfaces: list[r3.resource.R3surf] = None
    
    @property
    def surface(self) -> pg.Surface: return

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
