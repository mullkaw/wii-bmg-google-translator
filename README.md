# Wii BMG Google Translator

A python program that interfaces with [Google's Translate API](https://github.com/googleapis/python-translate) and [Wiimms BMG Tool](https://szs.wiimm.de/wbmgt/) to automatically machine-translate BMG files into a list of languages one after the other!

Do note that machine translation doesn't purport to be all too accurate, mainly due to the lack of linguistic context among other things. The purpose of this program isn't for accurate translation though, inaccuracies are welcome and might even be encouraged!

## Usage
This program is written in Python 3. You can run like this:
```bat
program.py INPUTFILE.EXT
```
Where, `.EXT` is whatever file extension that the input file has, if any.

After the translation process is done, a file called `INPUTFILE-translated.bmg` will have been created which is the Google-translated BMG file.

> **The path to wbmgt (Wiimms BMG Tool) must be on your computer's path variable in order for the program to work.**

## Configuration

The `config.ini` file is where the settings for the program are. There is one section [PARAMETERS] with the following values under it:

**credentials**: This is the path to your service's account JSON keyfile which is the file used for authentication with the client of the Google Cloud Project that is using the Translate API. This value is optional as using a JSON keyfile isn't required for using the API. More information on Google API authentication can be found [here](https://googleapis.dev/python/google-api-core/latest/auth.html).

**source_language**: This is the original language of the BMG that you want to translate. This value is optional as Translate can try to auto-detect the source language if it isn't supplied here. This value must be in the form of an [ISO 639-1 language code](https://www.loc.gov/standards/iso639-2/php/code_list.php) and it also must be a language supported by Translate.
> For example, a value of `en` indicates that the original BMG is in English.

**target_languages**: This the sequence of languages that the BMG is translated to. These values are comma-separated and just like the source language value, they are the form of an [ISO 639-1 language code](https://www.loc.gov/standards/iso639-2/php/code_list.php). Trying to translate from any one language into itself is not allowed.
> For example, a value of `es, th, zu, en` tells the program to first translate from the source language into Spanish, then from Spanish to Thai, then from Thai to Zulu, and finally from Zulu to English
