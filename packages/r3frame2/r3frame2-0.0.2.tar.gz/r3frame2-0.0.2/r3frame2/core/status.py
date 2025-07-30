
class R3status:
    class database:
        CACHE_NOT_FOUND: int = 0x00
        KEY_NOT_FOUND: int = 0x01
        KEY_FOUND: int = 0x02
        LOAD_SUCCESS: int = 0x03
        LOAD_FAIL: int = 0x04
    
    class physics:
        ENTITY_NOT_FOUND: int = 0x05
        ENTITY_FOUND: int = 0x06
        ENTITY_INVALID: int = 0x07
