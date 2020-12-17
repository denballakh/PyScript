import tkinter as tk


class states:
    NONE = 0
    SINGLE_QUOTE = 1  # 'string'
    DOUBLE_QUOTE = 2  # "string"
    ML_QUOTE = 3  # `string`
    REGEX_LITERAL = 4  # /regex/
    SL_COMMENT = 5  # // single line comment
    ML_COMMENT = 6  # /* multiline comment */
    NUMBER_LITERAL = 7  # 123
    KEYWORD = 8  # function, var etc.
    SPECIAL = 9  # null, true etc.


class colors:
    NONE = '#FFFFFF'
    SINGLE_QUOTE = '#E6DB74'  # 'string'
    DOUBLE_QUOTE = '#E6DB74'  # "string"
    ML_QUOTE = '#E6DB74'  # `string`
    REGEX_LITERAL = '#FF0000'  # /regex/
    SL_COMMENT = '#6E7066'  # // single line comment
    ML_COMMENT = '#6E7066'  # /* multiline comment */
    NUMBER_LITERAL = '#AE81FF'  # 123
    KEYWORD = '#F92672'  # function, var etc.
    SPECIAL = '#66D9EF'  # null, true etc.
    SYMBOLS = '#F92672'  # +-/*=&|%!<>?:
    BACKGROUND = '#272822'


# keywords = ('async await break case class const continue debugger default delete do else enum export extends for from function ' +
# 'get if implements import in instanceof interface let new of package private protected public return set static super ' +
# 'switch throw try typeof var void while with yield catch finally').split(' ')
keywords = ('and with as assert break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while yield').split(' ')
specials = 'self True False None'.split(' ')
digits = '0123456789'
symbols = '+ - / * = & | % ! < > ? : . , @ ( ) { } [ ] ; ^ ~'.split(' ')
letters = 'abcdefghijklmnopqrstuvwxyz' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + '_'


def isAlphaNumericChar(char):
    return char in letters or char in digits


def pos(code, i):
    prefix = code[:i+1]
    lines = prefix.count('\n') + 1
    line = prefix.split('\n')[-1:][0]
    symbol = len(line)-1
    if line == '':
        lines -= 1
        line = prefix.split('\n')[-2:][0]
        symbol = len(line)
    return f'{lines}.{symbol}'


def highlight(code):
    tags = {}

    id = [0]

    def startTag(i, color, id=id):
        tags[id[0]] = {}
        tags[id[0]][0] = pos(code, i)
        tags[id[0]][1] = None
        tags[id[0]][2] = color
        return f'<span style="color: {color}">'

    def endTag(i, id=id):
        tags[id[0]][1] = pos(code, i+1)
        id[0] += 1
        return '</span>'

    output = ''
    state = states.NONE
    for i in range(0, len(code)):
        char = code[i]
        if i-1 >= 0:
            prev = code[i-1]
        else:
            prev = ' '
        if i+1 < len(code):
            next = code[i+1]
        else:
            next = ' '

        if (state == states.NONE and char == '#'):
            state = states.SL_COMMENT
            output += startTag(i, colors.SL_COMMENT) + char
            continue

        if (state == states.SL_COMMENT and char == '\n'):
            state = states.NONE
            output += char + endTag(i)
            continue


        closingCharNotEscaped = prev != '\\' or prev == '\\' and code[i-2] == '\\'
        if (state == states.NONE and char == '\''):
            state = states.SINGLE_QUOTE
            output += startTag(i, colors.SINGLE_QUOTE) + char
            continue

        if (state == states.SINGLE_QUOTE and char == '\'' and closingCharNotEscaped):
            state = states.NONE
            output += char + endTag(i)
            continue

        if (state == states.NONE and char == '"'):
            state = states.DOUBLE_QUOTE
            output += startTag(i, colors.DOUBLE_QUOTE) + char
            continue

        if (state == states.DOUBLE_QUOTE and char == '"' and closingCharNotEscaped):
            state = states.NONE
            output += char + endTag(i)
            continue

        if (state == states.NONE and (char in digits) and not isAlphaNumericChar(prev)):
            state = states.NUMBER_LITERAL
            output += startTag(i, colors.NUMBER_LITERAL) + char
            continue

        if (state == states.NUMBER_LITERAL and (char not in digits) and (char != '.')):
            state = states.NONE
            output += endTag(i-1)

        if (state == states.NONE and not isAlphaNumericChar(prev)):
            word = ''
            j = 0
            while (code[i + j] and isAlphaNumericChar(code[i + j])):
                word += code[i + j]
                j += 1

            if (word in keywords):
                state = states.KEYWORD
                output += startTag(i, colors.KEYWORD)

            if (word in specials):
                state = states.SPECIAL
                output += startTag(i, colors.SPECIAL)

        if ((state == states.KEYWORD or state == states.SPECIAL) and not isAlphaNumericChar(char)):
            state = states.NONE
            output += endTag(i)

        if (state == states.NONE and (char in symbols)):
            output += startTag(i, colors.SYMBOLS) + \
                char + endTag(i)
            continue

    return tags


fp = open('syntax_coloring.py', 'rt', encoding="utf-8")
code = fp.read()
fp.close()


def applyTags(text, tags):
    for tag in text.tag_names():
        text.tag_delete(tag)
    for tag_id, val in tags.items():
        text.tag_add(tag_id, val[0], val[1])
        text.tag_config(tag_id, background="", foreground=val[2])


def onModification(event):
    textArea = event.widget
    text = textArea.get("1.0", "end-1c")
    chars = len(text)
    label.configure(text=f"{chars} chars")

    applyTags(textArea, highlight(text))


class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        """A text widget that report on internal widget commands"""
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result


root = tk.Tk()
label = tk.Label(root, anchor="w")
text = CustomText(root, bg=colors.BACKGROUND, fg=colors.NONE)

label.pack(side="bottom", fill="x")
text.pack(side="top", fill="both", expand=True)


text.bind("<<TextModified>>", onModification)

text.insert('1.0', code)

applyTags(text, highlight(code))

root.mainloop()
