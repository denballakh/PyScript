import text_editor
from settings import *
from utils import *
from block_manager import *
from block import Block


class SourceFile:
    """
    Класс графической программы/ class of grafical program
        max_id = 0 - максимальный id блоков/ max block id
        object_ids = {} - словарь ссылок на блоки {<id>:<блок>}/ dictionary of links to blocks {<id>:<block>}
        fileName = '' - файл для сохранение/ File for saving
        buildName = '' - файл для составления текста программы/ file for experting program
        data = 0 - subversion
        lang = 'py' - язык составления программы/language of export
    """

    def __init__(self, app):
        self.app = app
        self.max_id = 0
        self.object_ids = {}
        self.fileName = ''
        self.buildName = ''
        self.data = 0
        self.lang = None
        self.changeLang('python')
        self.wasEdited = False

    def changeLang(self, lang):
        if self.lang == lang: return
        self.lang = lang
        change_lang(lang)

    def save(self, fileName='', save=1):
        """Сохраняет в файл/save into file"""
        self.wasEdited = False

        self.data += 1

        data = {
            'subversion': self.data,
            'lang': self.lang,
            'build_path': self.buildName,
            'blocks': [val.toDict() for key, val in self.object_ids.items()]
        }

        if save:
            if fileName:
                self.fileName = fileName
                with open(self.fileName, 'w') as outfile:
                    json.dump(data, outfile, indent=4)
        else:
            print('Save log:')
            print(json.dumps(data, indent=4))

    def open(self, fileName):
        """Загружает из файла/ load from file"""
        self.wasEdited = False

        obj = json_load(fileName)

        self.max_id = 0
        self.object_ids = {}
        self.fileName = fileName

        self.data = obj["subversion"]
        if isinstance(self.data, int):
            self.data = int(self.data)
        else:
            logger.log(f'Bad subversion: {self.data}; setting subversion to {0}')
            self.data = 0

        self.changeLang(obj["lang"])
        self.buildName = obj["build_path"]
        blocks = obj["blocks"]
        for b in blocks:
            block_type = b['type']
            if block_type in allTypes:
                Block(self, b, creating_type=1)
            else:
                raise Exception(f'Unknown type of block: {block_type}! \nBlock: "{b}\nallTypes: {allTypes}"')

            # line = str(b)
            # if len(line.strip()) == 0 or line.strip()[0] == ';':
            #     continue  # пустые строки и строки-комментарии пропускаем/ leave empty and comment strings
            # type = literal_eval(line)["type"]
            # if type in allTypes:
            #     Block(self, line.strip(), creating_type=1)
            # else:

    def parents(self, block_id):
        """Возвращает id всех блоков, для которых данный является дочерним/ return ids of all child blocks"""
        res = []
        for i, obj in self.object_ids.items():
            if block_id in obj.childs:
                res = res + [i]
        return res

    def build(self, fileName, save=1):
        """Составляет текст программы и сохраняет его в файл/ create program text and save it to file"""

        rootBlock = Block(self, block_type='empty')
        for i, _ in self.object_ids.items():
            if not self.parents(i):
                rootBlock.addLink(i)
        rootBlock.sortChilds()
        s = rootBlock.build('')
        rootBlock.delete()

        if save:
            self.buildName = fileName
            file = open(self.buildName, 'wt')
            file.write(s)
            file.close()
        else:
            print('Build log:')
            print(s)

    def closeQ(self):
        return not self.wasEdited

    def __del__(self):
        for _, block in self.object_ids.items():
            del block
        self.object_ids = {}

