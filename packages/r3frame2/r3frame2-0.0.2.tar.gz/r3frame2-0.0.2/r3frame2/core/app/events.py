from ..flags import R3flags
from ..atom import R3atom
from ..globals import pg

import r3frame2 as r3

class R3events(R3atom):
    def __init__(self, app: "r3.app.R3app") -> None:
        super().__init__()
        self.app: r3.app.R3app = app

        self.keyboard = {}
        self.keyboard_old = {}

        self.mouse = {}
        self.mouse_old = {}
        self.wheel: list[int] = [0, 0]
        self.mouse_wheel_up: bool=False
        self.mouse_wheel_down: bool=False

    def key_held(self, key) -> bool:
        return self.keyboard.get(key, False)

    def key_pressed(self, key) -> bool:
        return self.keyboard.get(key, False) and not self.keyboard_old.get(key, False)

    def mouse_held(self, button:int) -> bool:
        return self.mouse.get(button, False)

    def mouse_pressed(self, button) -> bool:
        return self.mouse.get(button, False) and not self.mouse_old.get(button, False)

    def update(self) -> None:
        self.wheel = [0, 0]
        self.mouse_wheel_up = False
        self.mouse_wheel_down = False
        self.mouse_old = self.mouse.copy()
        self.keyboard_old = self.keyboard.copy()

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_F12):
                self.app.rem_flag(R3flags.app.RUNNING)
            match event.type:
                case pg.KEYUP:
                    self.keyboard[event.key] = False
                case pg.KEYDOWN:
                    self.keyboard[event.key] = True
                case pg.MOUSEBUTTONUP:
                    self.mouse[event.button] = False
                case pg.MOUSEWHEEL:
                    self.wheel = [event.x, event.y]
                case pg.MOUSEBUTTONDOWN:
                    self.mouse[event.button] = True
                    if event.button == 4:
                        self.mouse_wheel_up = True
                    if event.button == 5:
                        self.mouse_wheel_down = True
