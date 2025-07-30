from ..flags import R3flags
from ..log import R3logger
from ..atom import R3atom
from ..globals import pg
# from ..utils import 
import r3frame2 as r3

class R3app(R3atom):
    def __init__(
            self,
            title: str = "R3app",
            clock_rate: float = 0.1,
            clock_target: float = 60,
            window_size: list[int] = [ 800, 600]
        ) -> None:
        super().__init__()
        self.title: str = title
        
        self.events: r3.app.R3events = r3.app.R3events(self)
        self.window: r3.app.R3window = r3.app.R3window(size=window_size)
        self.clock: r3.app.R3clock = r3.app.R3clock(clock_rate, clock_target)
        
        self.mouse: r3.app.R3mouse = r3.app.R3mouse()
        self.keyboard: r3.app.R3keyboard = r3.app.R3keyboard()

        self.database: r3.resource.R3database = r3.resource.R3database()

        self.scene: r3.app.R3scene = None
        self.scenes: dict[str, r3.app.R3scene] = {}

        self.init()
        self.set_flag(R3flags.app.RUNNING)

    def init(self) -> None:
        R3logger.error(f'"{self.title}" Initialization Method Missing...')
        raise NotImplementedError
    
    def exit(self) -> None:
        R3logger.error(f'"{self.title}" Exit Method Missing...')
        raise NotImplementedError

    def add_scene(self, key: str, scene: "r3.app.R3scene") -> None:
        if not isinstance(scene, type):
            R3logger.warning(f"[R3app] pass the scene as a type: (key){key}")
            return
        if self.scenes.get(key, False) != False:
            R3logger.warning(f"[R3app] scene already added: (key){key}")
            return
        self.scenes[key] = scene(self)
        R3logger.info(f"[R3app] scene added: (key){key}")

    def get_scene(self, key: str) -> "r3.app.R3scene":
        if not isinstance(key, str): return
        if key not in self.scenes:
            R3logger.warning(f"[R3app] scene not found: (key){key}")
            return
        return self.scenes[key]

    def set_scene(self, key: str) -> None:
        if self.scenes.get(key, False) == False:
            R3logger.warning(f"[R3app] scene not found: (key){key}")
            return
        if isinstance(self.scene, r3.app.R3scene):
            self.scene.exit()
        self.scene = self.scenes[key]
        R3logger.info(f"[R3app] scene set: (key){key}")
        self.scene.init()
        
    def rem_scene(self, key: str) -> None:
        if self.scenes.get(key, False) != False:
            R3logger.warning(f"[R3app] scene not found: (key){key}")
            return
        self.scenes.pop(key).exit()
        self.scene = None
        R3logger.info(f"[R3app] scene removed: (key){key}")

    def run(self) -> None:
        while self.get_flag(R3flags.app.RUNNING):
            self.events.update()
            self.clock.update()
            self.window.clear()
            
            if isinstance(self.scene, r3.app.R3scene):
                self.scene.events()
                
                self.scene.physics.update(self.clock.delta)
                self.scene.camera.update(self.clock.delta)
                self.scene.update(self.clock.delta)
                
                self.scene.render()
                self.scene.renderer.render()
                self.scene.ui.render()

            self.mouse.pos.rel = pg.mouse.get_rel()
            self.mouse.pos.screen = pg.mouse.get_pos()

            self.window.update()
        else:
            if isinstance(self.scene, r3.app.R3scene):
                self.scene.exit()
            self.exit()
