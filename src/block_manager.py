from utils import *

# Цвета соединяющих линий
# A_B = A==>B
# A_  = A==>*
#  _B = *==>B
#  _  = *==>*
linkColors = {
    "_": "#000000",

    "_creating": "#ffff00",

    # "op_":"#000000",
    # "_op":"#000000",
    "op_op": "#ffffff",


    # "if_":"#000000",
    # "_if":"#000000",
    "if_if": "#ffffff",

    # "for_" :"",
    # "_for" :"",
    "for_for": "#ffffff",

    # "fun_" :"",
    # "_fun" :"",
    "fun_fun": "#ffffff",

    "class_": "#0000ff",
    # "_class" :"",
    "class_class": "#ffffff",

    # "op_if": "#ff0000",
    # "if_op": "#00ff00",
    "class_fun": "#8080ff",
    "class_op": "#80ff80",
    # "_" :"",
    # "_" :"",
    # "_" :"",
    # "_" :"",
    # "_" :"",
    # "_" :"",
    # "_" :"",

}


def load_lang_blocks(lang):
    """Загружает"""
    path = langs[lang]
    res = {}
    blocks = json_load(f'block_types/{path}')
    for block_type, block_path in blocks.items():
        res[block_type] = json_load(f'block_types/{lang}/{block_path}')
    return res


def load_lang(lang):
    global allTypes
    logger.log(f'changing lang to {lang}')
    logger.log('#old blocks: ', len(allTypes))
    allTypes.clear()
    lng = load_lang_blocks(lang)
    df = load_lang_blocks('default')
    for k, v in dictMerge(lng, df).items():
        allTypes[k] = v
    logger.log('#new blocks: ', len(allTypes))


langs = json_load('block_types/LANGS.json')
allTypes = load_lang_blocks('default')

if __name__ == '__main__':
    print('This module is not for direct call!')
