
import glob
import json
import os
from uuid import uuid4


def get_bulk_json_data_generator(files_dir: str) -> tuple:
    '''
    Generator function that yields the 'id' and data from each .json file in a directory.

    For each file in the directory, extracts the 'id' field from JSON data, if an 'id' field does not exist,
    a new UUID is generated as the ID.

    :param files_dir: path to the directory of the .json files

    Yields:
        tuple:
            id from the JSON data or a newly generated UUID if 'id' is not present.
            JSON data
    '''

    file_list = glob.glob(os.path.join(files_dir, '*.json'))
    for filename in file_list:
        with open(filename, 'r') as f:
            data = json.load(f) 
            _id = data.pop('id', None)
            if not _id:
                _id = uuid4()
            yield _id, data

def actions_list_gen(files_dir: str, index: str, chunk_size: int) -> tuple[list[dict], int]:
    '''
    Generator produces chunks of action lists for bulk processing
    
    This function reads JSON data from the directory, creates actions for each piece 
    of data. Each action consists of an index action followed by the corresponding document data 
    and groups these actions into chunks of a specified size.

    :param files_dir: path to the directory pf the .json files
    :param index: es index name for action meta-data
    :param chunk_size: number of documents per chunk

    Yields:
        tuple:
            list of actions for bulk processing
            count of documents in the current chunk
    '''
    files_gen = get_bulk_json_data_generator(files_dir)
    count = 0
    actions_list = []
    while files_gen:
        try:
            data = next(files_gen)
            _id, doc = data
            actions_list.extend([{'index': { '_index': index, '_id': _id }}, doc])
            count += 1
            if count % chunk_size == 0 and count != 0:
                yield actions_list, count
                actions_list = []
                count = 0
        except StopIteration:
            if len(actions_list) != 0:
                yield actions_list, count
            return
    return
