# from utils import json_load
import json
def json_load(path: str):
    """Загружает json-объект из файла"""
    fp = open(path, 'rt')
    obj = json.load(fp)
    fp.close()

    return obj

__all__ = [
    'btnBG',
    'textBG',
    'panelBG',
    'spaceBG',
    'stateBG',
    'btnFG',
    'textFG',
    'panelFG',
    'spaceFG',
    'stateFG',
    'blockR',
    'chosen_R',
    'link_width',
    'font_size',
    'nearToLine',
    'zoomSpeed',
    'arrow_width',
    'arrow_length',
    'debug_to_console',
    'profile',
    'openEditorAfterCreating',
    'ban_impositions',
    'default_language',
    'canvas_minzoom',
    'canvas_maxzoom'
]

obj = json_load('settings.json')

# Цвета различных элементов/Colors of different elements
cs = obj['color_scheme']
bg = cs['BG']
fg = cs['FG']
btnBG = bg['btn']
textBG = bg['text']
panelBG = bg['panel']
spaceBG = bg['space']
stateBG = bg['state']

btnFG = fg['btn']
textFG = fg['text']
panelFG = fg['panel']
spaceFG = fg['space']
stateFG = fg['state']
del cs, bg, fg

# Радиус блока (1 - размер клетки)/Block radius, 1 is a cell size
blockR = obj['blockR']
chosen_R = obj['chosen_R']
link_width = obj['link_width']
font_size = obj['font_size']
# Расстояние на котором нажатие мышью удаляет линию/Distance on which mouse click deletes the link
nearToLine = obj['nearToLine']
# Чуствительность зума колесом мыши/Sensitiveness of zoom by wheel
zoomSpeed = obj['zoomSpeed']
# ширина стрелки/ arrow width
arrow_width = obj['arrow_width']
# длина стрелки/ arrow length
arrow_length = obj['arrow_length']

# Флаг дебага/Debug flag
debug_to_console = obj['debug_to_console'] and __debug__

# Флаг профилирования/Profiling flag
profile = obj['profile'] and __debug__

openEditorAfterCreating = obj['openEditorAfterCreating']

ban_impositions = obj['ban_impositions']

default_language = obj['default_language']

canvas_minzoom = 0
canvas_maxzoom = 100

del obj

if __name__ == "__main__":
    print("This module is not for direct call!")
