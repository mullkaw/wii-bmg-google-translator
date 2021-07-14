import re

# the magic for a bmg text file
magic = '#BMG'

# regular expression strings for parsing bmg text files
# NOTE this assumes the hex values always use uppercase letters
parameter_re_str = r"@(?P<name>[\S]+)[\s]*=[\s]*(?P<value>[\S]+)"
attribute_re_str = r"\[[,0-9A-Fa-f/]+\]"
attribute32_re_str = r"|0x[0-9A-Fa-f]+"
mid_re_str = r"[0-9a-f]+" + "|" + r"T[1-8][1-4]" + "|" + r"U[1-2][1-5]" \
    + "|" + r"M(?:0[1-9]|[1-8][0-9]|9[0-6])"
escape_re_str = r"\\(?:[^n][\S]*|n)"
text_re_str = r"(?:.)*"

# MID ~ ATTRIB32
format1_re_str = fr"(?P<mid>{mid_re_str})[\s]*~[\s]*(?P<attrib32>{attribute32_re_str})"

# MID /
format2_re_str = fr"(?P<mid>{mid_re_str})[\s]*/"

# MID '[' ATTRIB ']' /
format3_re_str = fr"(?P<mid>{mid_re_str})[\s]*(?P<attrib>{attribute_re_str})[\s]*/"

# MID = TEXT
format4_re_str = fr"(?P<mid>{mid_re_str})[\s]*=[\s]?(?P<text>(?:.)*)"

# MID '[' ATTRIB ']' = TEXT
format5_re_str = fr"(?P<mid>{mid_re_str})[\s]*(?P<attrib>{attribute_re_str})[\s]*=[\s]?(?P<text>(?:.)*)"

# MID1 : MID2
format6_re_str = fr"(?P<mid1>{mid_re_str})[\s]*:[\s]*(?P<mid2>{mid_re_str})"

# any of the above six formats
# uses re.sub to get rid of the named captures
format_any_re_str = re.sub(
    r"\?P<[^<>]+>",
    "?:",
    f"{format1_re_str}|{format2_re_str}|{format3_re_str}|{format4_re_str}|{format5_re_str}|{format6_re_str}",
)

class Parameter:
    def __init__(self, line):
        m = re.match(parameter_re_str, line)
        self.name = m.group('name')
        self.value = m.group('value')

    def __str__(self):
        return f'@{self.name} = {self.value}'

class Message:
    def __init__(self, line):
        format = mid = mid2 = attrib = attrib32 = text = escapes = None

        if re.match(format1_re_str, line):
            m = re.match(format1_re_str, line)
            format = 1
            mid = m.group('mid')
            attrib32 = m.group('attrib32')

        elif re.match(format2_re_str, line):
            m = re.match(format2_re_str, line)
            format = 2
            mid = m.group('mid')

        elif re.match(format3_re_str, line):
            m = re.match(format3_re_str, line)
            format = 3
            mid = m.group('mid')
            attrib = m.group('attrib')

        elif re.match(format4_re_str, line):
            m = re.match(format4_re_str, line)
            format = 4
            mid = m.group('mid')
            text = m.group('text')

        elif re.match(format5_re_str, line):
            m = re.match(format5_re_str, line)
            format = 5
            mid = m.group('mid')
            attrib = m.group('attrib')
            text = m.group('text')
            
        elif re.match(format6_re_str, line):
            m = re.match(format6_re_str, line)
            format = 6
            mid = m.group('mid1')
            mid2 = m.group('mid2')
        else:
            pass

        # take the escape sequences and put them in a separate list
        # also, in the text, replace all of the escapes with {}
        if text:
            escapes = re.findall(escape_re_str, text)

            # replace brackets so that they survive the format step
            text = text.replace('{', '{{').replace('}', '}}')
            text = re.sub(escape_re_str, '{}', text)

        self.format = format
        self.mid = mid
        self.mid2 = mid2
        self.attrib = attrib
        self.attrib32 = attrib32
        self.text = text
        self.escapes = escapes

    def __str__(self):

        f_text = ""

        # In case translate adds some surprise brackets
        # make sure there are enough args in format
        space_lst = [' '] * len(re.findall(r"(?<!\{)\{\}(?!\})", self.text))

        # re-insert the escape sequences into the text
        if self.text:
            try:
                f_text = self.text.format(*self.escapes, *space_lst) if self.escapes else self.text.format(*space_lst)
            except ValueError:
                f_text = re.sub(r"(?<![\{])\{(?![\{\}])", "{{", self.text)
                f_text = re.sub(r"(?<![\{\}])\}(?![\}])", "}}", f_text)
                f_text = f_text.format(*self.escapes, *space_lst) if self.escapes else f_text.format(*space_lst)
        
        formats = {
            None: ">>>ERROR: NO FORMAT FOUND", # should be unreachable
            1: f'{self.mid} ~ {self.attrib32}',
            2: f'{self.mid} /',
            3: f'{self.mid} {self.attrib}',
            4: f'{self.mid} = {f_text}',
            5: f'{self.mid} {self.attrib} = {f_text}',
            6: f'{self.mid} : {self.mid2}',
        }

        return formats[self.format]

class Bmg:
    def __init__(self, filename):
        parameters = []
        messages = []

        with open(filename, 'r', encoding='utf-8') as f:
            for line in [line.lstrip() for line in f.readlines() \
                if len(line) > 0 and not re.match(r"^[#\s](?:\s)*$", line)]:
                # check if line is a parameter
                # add it to parameter list if so
                if re.match(parameter_re_str, line):
                    parameters.append(Parameter(line))
                elif re.match(format_any_re_str, line):
                    messages.append(Message(line))

        self.parameters = parameters
        self.messages = messages

    def __str__(self):
        return magic + '\n' \
            + '\n'.join([str(param) for param in self.parameters]) + '\n' \
            + '\n'.join([str(msg) for msg in self.messages]) + '\n'
