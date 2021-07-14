import six
from google.cloud import translate_v2 as translate

def do_translations(config, text):
    """Does a series of subsequent translations on the input text.
    The config file determines the languages this is done on.
    This function is based off of the example code here:
    https://cloud.google.com/translate/docs/basic/quickstart#translate_translate_text-python
    
    Returns the translated text
    """
    
    # set config variable to first section of given config
    config = config[config.sections()[0]]

    # the initial language of the texts
    # auto-detects if not specified
    source = config['source_language']

    # load up this configuration's credentials from the path specified in the config
    # if nothing is there then assume the environment variable was already set
    translate_client = translate.Client.from_service_account_json(config['credentials']) \
        if config['credentials'] else translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    for target in [target.strip() for target in config['target_languages'].split(',')]:
        result = translate_client.translate(
            values=text,
            format_='text',
            source_language=source,
            target_language=target,
        )
        text = result['translatedText']

        # this iteration's target language is the next iteration's source
        source = target

    return text
