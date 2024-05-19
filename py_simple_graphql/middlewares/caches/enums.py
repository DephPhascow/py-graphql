from strenum import StrEnum

class CacheType(StrEnum):
    NO_SAVE = 'no_save'
    SAVE_BY_USER = 'save'
    ALL_SAVE = 'all_save'