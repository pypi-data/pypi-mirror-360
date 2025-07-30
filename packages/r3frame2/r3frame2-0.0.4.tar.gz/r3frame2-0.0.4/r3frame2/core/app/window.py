from ..globals import pg
from ..atom import R3atom
from ..log import R3logger
from ..utils import add_v2, r3_path

class R3window(R3atom):
    def __init__(self, title: str = "R3window", size: list[int] = [800, 600], color: list[int] = [25, 25, 25]) -> None:
        super().__init__()
        self.title: str = title
        self.size: list[int] = size
        self.color: list[int] = color
        
        self.raster: pg.Surface = pg.display.set_mode(size)
        self.icon: pg.Surface = pg.image.load(r3_path(".external/images/logo-16x.png", 1)).convert_alpha()
        
        pg.display.set_caption(title)
        pg.display.set_icon(self.icon)

    def set_title(self, title: str) -> None:
        if not isinstance(self.title, str): return
        pg.display.set_caption(title)
        self.title = title

    def set_icon(self, icon: pg.Surface) -> None:
        if not isinstance(self.icon, pg.Surface): return
        pg.display.set_icon(self.icon)
        self.icon = icon

    def set_size(self, size: list[int]) -> None:
        if not isinstance(size, list): return
        self.raster = pg.display.set_mode(size)
        self.size = size[:]

    def clear(self) -> None:
        self.raster.fill(self.color)

    def blit(self, surface: pg.Surface, location: list[int], offset: list[int]=[0, 0]) -> None:
        self.raster.blit(surface, add_v2(location, offset))

    def update(self) -> None:
        pg.display.flip()
