import configparser

from ..utils.get_es_config import get_project_root

default_settings = {
    'number_of_shards': 5,
    'index': {
        'max_ngram_diff': 50
    },
    'analysis': {
        'analyzer': {
            'custom_ngram_index_analyzer': {
                'type': 'custom',
                'tokenizer': 'custom_ngram',
                'filter': ['lowercase']
            },
            'ngram_search_analyzer': {
                'type': 'custom',
                'tokenizer': 'custom_ngram',
                'filter': ['lowercase']
            }
        },
        'tokenizer': {
            'custom_ngram': {
                'type': 'ngram',
                'min_gram': 2,
                'max_gram': 50
            },
        }
    }
}


def create_settings() -> dict:
    '''
    Reads custom index configuration from a config.ini file and updates default settings

    Supported configuration values include: 
    - max_ngram_diff 
    - number_of_shards
    - refresh_interval 
    - number_of_replicas
    - min_gram 
    - max_ngram 
    '''
    config = configparser.ConfigParser()
    config_file = get_project_root().as_posix() + '/elastic_search/config/config.ini'
    config.read(config_file)

    custom_settings = default_settings.copy()
    custom_settings['index']['max_ngram_diff'] = config.get(
        'index-config', 'max_ngram_diff', fallback=50)
    custom_settings['number_of_shards'] = config.get(
        'index-config', 'number_of_shards', fallback=5)
    custom_settings['index']['refresh_interval'] = config.get(
        'index-config', 'refresh_interval', fallback='1s')
    custom_settings['index']['number_of_replicas'] = config.get(
        'index-config', 'number_of_replicas', fallback=1)
    min_gram = config.get('index-config', 'min_gram', fallback=2)
    max_gram = config.get('index-config', 'max_ngram', fallback=50)
    custom_settings['analysis']['tokenizer']['custom_ngram']['min_gram'] = min_gram
    custom_settings['analysis']['tokenizer']['custom_ngram']['max_ngram'] = max_gram

    return custom_settings
