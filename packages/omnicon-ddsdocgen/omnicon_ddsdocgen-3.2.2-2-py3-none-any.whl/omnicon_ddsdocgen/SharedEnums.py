import enum
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

class ChangeStatusEnum(enum.IntEnum):
    NO_CHANGE = 0
    DELETED = 1
    ADDED = 2
    CHANGED = 3

    @classmethod
    def get_background_color(cls, value):
        color_map = {
            cls.NO_CHANGE: None,  # No color
            cls.DELETED: "cc1107",  # Red color
            cls.ADDED: "35a931",  # Green color
            cls.CHANGED: "ffd000"  # Yellow color
        }
        color_hex = color_map.get(value)
        if color_hex is None and value in cls:
            return None
        elif color_hex is not None:
            return parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_hex))
        else:
            raise ValueError(f"Unrecognized value for ChangeStatusEnum: {value}")