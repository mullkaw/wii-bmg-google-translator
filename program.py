import os
import sys
import subprocess as spc
from configparser import ConfigParser
from distutils import spawn

from iso639 import languages

from wiibmg import *
from chain_translate import *

# check for wbmgt on path
# TODO also check for it in the same directory
if not spawn.find_executable('wbmgt'):
    sys.stderr.write('wbmgt not found')
    quit()

for arg in sys.argv[1:]:
    # the argument with no file extension
    arg_no_ext = arg[:arg.rfind('.')] if arg.rfind('.') != -1 else arg

    # the file extension (including the dot)
    ext = arg[arg.rfind('.'):] if arg.rfind('.') != -1 else ""

    if os.path.isfile(f"{arg_no_ext}-translated.bmg"):
        err = f"{arg_no_ext}-translated.bmg is already in this directory.\n" + \
            "Move this file before running the program.\n"

        sys.stderr.write(err)
        continue

    # decode the bmg and create the bmg object
    # if it's a .txt file then we assume it is a BMG text file and dont decode
    if 'txt' not in ext:
        # https://szs.wiimm.de/wbmgt/cmd-decode.html
        command = f"wbmgt decode --single-line --dest {arg_no_ext}.txt {arg}"
        spc.run(command).check_returncode()
        print()

    wii_bmg = Bmg(f"{arg_no_ext}.txt")

    print(f"Translating {arg}")
    print()

    config = ConfigParser()
    config.read('config.ini')

    # config file has one section so we receive this one section
    parameters = config[config.sections()[0]]

    source_name = languages.get(alpha2=parameters['source_language']).name \
        if parameters['source_language'] else "auto-detect"

    target_names = [languages.get(alpha2=target.strip()).name \
        for target in parameters['target_languages'].split(',')]

    print(f"Translating from: {source_name}")
    print(f"to: {', '.join(target_names)}")
    print()

    lines = [message.text for message in wii_bmg.messages]

    lines = [do_translations(config, line) for line in lines]

    for i, line in enumerate(lines):
        wii_bmg.messages[i].text = line 

    with open(f"{arg_no_ext}-translated.txt", 'w', encoding='utf-8') as fo:
        fo.write(str(wii_bmg))

    # https://szs.wiimm.de/wbmgt/cmd-encode.html
    command = f"wbmgt encode {arg_no_ext}-translated.txt"
    spc.run(command).check_returncode()
    print()

    try:
        if 'txt' not in ext:
            os.remove(f"{arg_no_ext}.txt")
        
        os.remove(f"{arg_no_ext}-translated.txt")
    except FileNotFoundError:
        pass

    print(f"Finished Translating {arg} !")
    print(f"Output file is {arg_no_ext}-translated{ext}")
    print()
