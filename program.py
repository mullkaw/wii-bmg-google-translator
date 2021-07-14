from distutils import spawn
import subprocess as spc
from configparser import ConfigParser
from iso639 import languages
import os
import sys
from wiibmg import *
from chain_translate import *

# check for wbmgt on path
# TODO also check for it in the same directory
if not spawn.find_executable('wbmgt'):
    sys.stderr.write('wbmgt not found')
    quit()

for arg in sys.argv[1:]:
    # decode the bmg and create the bmg object
    spc.run(f"wbmgt decode --single-line --dest output.txt {arg}").check_returncode()
    wii_bmg = Bmg('output.txt')

    # wii_bmg.messages = wii_bmg.messages[77:83]

    print(f"Translating {arg}")

    config = ConfigParser()
    config.read('config.ini')

    parameters = config[config.sections()[0]]

    source_name = languages.get(alpha2=parameters['source_language']).name \
        if parameters['source_language'] else "auto-detect"

    target_names = [languages.get(alpha2=target.strip()).name \
        for target in parameters['target_languages'].split(',')]

    print(f"Translating from: {source_name}")
    print(f"to: {', '.join(target_names)}")

    lines = [message.text for message in wii_bmg.messages]

    lines = [do_translations(config, line) for line in lines]

    for i, line in enumerate(lines):
        wii_bmg.messages[i].text = line 

    with open('output-translated.txt', 'w', encoding='utf-8') as fo:
        fo.write(str(wii_bmg))

    spc.run(f"wbmgt encode output-translated.txt").check_returncode()

    try:
        os.remove('output.txt')
        os.remove('output-translated.txt')
    except FileNotFoundError:
        pass

    print("All done!")
