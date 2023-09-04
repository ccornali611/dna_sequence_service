import configparser
import os
from pathlib import Path
from typing import TypedDict


def get_project_root() -> Path:
    return Path(Path(Path(Path(__file__)).parent).parent.parent).absolute()

class ESConfig(TypedDict):
    connection_url: str
    es_index_name: str
    data_files_dir_path: str

def get_es_client_config() -> ESConfig:
    '''
    Reads Elasticsearch and index configuration from config.ini file
    :return: dictionary for Elasticsearch configuration details
    '''
    config = configparser.ConfigParser()
    config_file = get_project_root().as_posix() + '/elastic_search/config/config.ini'
    config.read(config_file)
    es_port = os.environ.get("ES_PORT", 9200)

    if os.environ.get('APP_ENV') == 'dev':
        es_url =f'http://elasticsearch:{es_port}'
    else:
        es_url =f'http://localhost:{es_port}'

    if not config.has_section('index-config'):
        print('Need `index-config` section in db_config.ini file! Must have values for `es_index_name`')
    if not config.has_section('initial-data'):
        print('Need `initial-data` section in db_config.ini file! Must have values for `data_files_dir_name`')
        
    try:
        connection_url = es_url
        es_index_name = config.get('index-config', 'es_index_name')
        data_files_dir_path = config.get('initial-data', 'data_files_dir_name')

        return {
            'connection_url': connection_url,
            'es_index_name': es_index_name,
            'data_files_dir_path': get_project_root().as_posix() + data_files_dir_path
        }
    except configparser.NoOptionError as err:
        print('[ERROR] configparser.NoOptionError: ', err)
        raise configparser.NoOptionError(err.section, err.option)
