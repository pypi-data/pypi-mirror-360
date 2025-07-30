from ..status import R3status
from ..log import R3logger
from ..atom import R3atom
from ..globals import pg
# from ..utils import 
import r3frame2 as r3

class R3database(R3atom):
    def __init__(self) -> None:
        __meta__: dict = {
            "_count": 0,
        }
        self.surf: dict[str, r3.resource.R3surf] =          { k: v for k,v in __meta__.items() }
        self.anim: dict[str, r3.resource.R3anim] =          { k: v for k,v in __meta__.items() }
        self.atlas: dict[str, r3.resource.R3atlas] =        { k: v for k,v in __meta__.items() }
        self.entity: dict[str, r3.resource.R3entity] =      { k: v for k,v in __meta__.items() }
        self.element: dict[str, r3.resource.R3element] =    { k: v for k,v in __meta__.items() }

    def _valid_key(self, cache: str, key: str) -> int:
        if not getattr(self, cache, 0):
            R3logger.error(f"[R3database] invalid cache attr: (cache){cache}")
            return R3status.database.CACHE_NOT_FOUND
        else:
            value = getattr(self, cache).get(key, 0)
            if not value:
                return R3status.database.KEY_NOT_FOUND
            else: return R3status.database.KEY_FOUND

    def _load_surf(self, path: str) -> pg.Surface:
        try:
            return pg.image.load(path).convert_alpha()
        except Exception as e:
            R3logger.error(f"[R3database] failed to load surface '{path}': {e}")
            return None

    def _load_surf_array(self, path: str, frame_size: list[int]) -> list[pg.Surface]:
        sheet = self._load_surf(path)
        frame_x = sheet.get_width() // frame_size[0]
        frame_y = sheet.get_height() // frame_size[1]

        frames = []
        for row in range(frame_y):
            for col in range(frame_x):
                x = col * frame_size[0]
                y = row * frame_size[1]
                frame = pg.Surface(frame_size, pg.SRCALPHA).convert_alpha()
                frame.blit(sheet, [0, 0], pg.Rect([x, y], frame_size))  # texture sampling :)
                frames.append(frame)
        return frames

    def _load_font(self, path: str, size: int) -> pg.font.Font:
        try:
            return pg.font.Font(path, size)
        except Exception as e:
            R3logger.error(f"[R3database] failed to load font '{path}' size {size}: {e}")
            return None

    def _load_sound(self, path: str) -> pg.mixer.Sound:
        try:
            return pg.mixer.Sound(path)
        except Exception as e:
            R3logger.error(f"[R3database] failed to load sound '{path}': {e}")
            return None


    def load_entity(
            self,
            key: str,
            pos: list[int] = [0, 0],
            size: list[int] = [32, 32],
            rgba: list[int] = [255, 255, 255, 255],
            rgba_key: list[int] = [0, 0, 0, 0],
        ) -> int:
        if self._valid_key("entity", key) != R3status.database.KEY_NOT_FOUND:
            R3logger.error(f"[R3database] failed to load entity: (key){key}")
            return R3status.database.LOAD_FAIL

        self.entity[key] = r3.resource.R3entity(self.entity["_count"], pos, size, rgba)
        
        surface = self.load_surf(f"{key}.surface", size, rgba, rgba_key, None)
        if surface == R3status.database.LOAD_FAIL:
            R3logger.error(f"[R3database] failed to load entity: (key){key}")
            return R3status.database.LOAD_FAIL
        self.entity[key].surface = self.query_surf(f"{key}.surface")

        self.entity["_count"] += 1

        R3logger.debug(f"[R3database] loaded entity: (key){key} (pos){pos} (size){size} (rgba){rgba}")
        return R3status.database.LOAD_SUCCESS

    def unload_entity(self, key: str) -> int:
        if self._valid_key("entity", key) != R3status.database.KEY_FOUND:
            R3logger.error(f"[R3database] failed to unload entity: (key){key}")
            return R3status.database.LOAD_FAIL

        self.entity.pop(key)
        self.entity["_count"] -= 1

        R3logger.debug(f"[R3database] unloaded entity: (key){key}")
        return R3status.database.LOAD_SUCCESS

    def query_entity(self, key: str) -> "r3.resource.R3entity":
        if self._valid_key("entity", key) != R3status.database.KEY_FOUND:
            R3logger.error(f"[R3database] failed to query entity: (key){key}")
            return R3status.database.LOAD_FAIL        
        return self.entity.get(key, R3status.database.LOAD_FAIL)


    def load_surf(
            self,
            key: str,
            size: list[int] = [32, 32],
            rgba: list[int] = [255, 255, 255, 255],
            rgba_key: list[int] = [0, 0, 0, 0],
            path: str = None,
        ) -> int:
        if self._valid_key("surf", key) != R3status.database.KEY_NOT_FOUND:
            R3logger.error(f"[R3database] failed to load surf: (key){key}")
            return R3status.database.LOAD_FAIL

        self.surf[key] = r3.resource.R3surf(size, rgba, rgba_key)
        if path is None:
            self.surf[key].surface = pg.Surface(size, pg.SRCALPHA)
            self.surf[key].surface.set_colorkey(rgba_key)
            self.surf[key].surface.set_alpha(*rgba[3:])
            self.surf[key].surface.fill(rgba[:3])
        else:
            self.surf[key].surface = self._load_surf(path)
        self.surf[key].mask = pg.mask.from_surface(self.surf[key].surface)

        self.surf["_count"] += 1

        R3logger.debug(f"[R3database] loaded surf: (key){key} (size){size} (rgba){rgba}")
        return R3status.database.LOAD_SUCCESS
    
    def unload_surf(self, key: str) -> int:
        if self._valid_key("surf", key) != R3status.database.KEY_FOUND:
            R3logger.error(f"[R3database] failed to unload surf: (key){key}")
            return R3status.database.LOAD_FAIL

        self.surf.pop(key)
        self.surf["_count"] -= 1

        R3logger.debug(f"[R3database] unloaded surf: (key){key}")
        return R3status.database.LOAD_SUCCESS

    def query_surf(self, key: str) -> "r3.resource.R3surf":
        if self._valid_key("surf", key) != R3status.database.KEY_FOUND:
            R3logger.error(f"[R3database] failed to query surf: (key){key}")
            return R3status.database.LOAD_FAIL        
        return self.surf.get(key, R3status.database.LOAD_FAIL)
