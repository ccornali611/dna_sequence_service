import asyncio
import logging
import os
from typing import List, Union

from elastic_transport import (ConnectionError, HeadApiResponse,
                               ObjectApiResponse)
from elasticsearch import AsyncElasticsearch

from .es_types import IndexDocWithHighlight, SearchHit, SearchRequestResult
from .index.index_mappings import default_mapping
from .index.index_settings import create_settings
from .utils.bulk_data_helper import actions_list_gen
from .utils.get_es_config import get_es_client_config


class ElasticSearchClient:
    '''
    Client for Elasticsearch (ES) interactions

    Attributes:
        _config: dict holding configurations for ES.
        _client: AsyncElasticsearch client instance
        _index_name: name of the default index
    '''

    def __init__(self, host: str = None) -> None:
        '''
        Initializes the ElasticSearchClient with configurations and a connection to ES
        '''
        self._config = get_es_client_config()
        es_host = host if host else self._config['connection_url']
        self._client = AsyncElasticsearch(
            hosts=es_host,
            max_retries=5,
            sniff_on_start=False,
            request_timeout=6000
        )
        self.host = es_host
        self.index_name = self._config.get('es_index_name')

    async def health_check(self) -> bool:
        '''
        Checking status of ES cluster
        '''
        try:
            info = await self._client.info()
            return True
        except ConnectionError as err:
            raise err

    async def rest_index(
        self,
        index: str = None,
        populate: bool = False,
        files_dir: str = None,
        chunk_size: int = 50
    ) -> None:
        '''
        Async reset (delete and then initialize) an index

        Deletes the specified ES index and then recreates it (can populate with existing data)
        If no index is provided, it defaults to the class's `_index` attribute.

        :param index: name of the ES index to reset and recreate (optional)
        :param populate: if True, populates the index after initializing it (optional)
        :param files_dir: directory path where the JSON files are located (optional)
        :param chuck_size: number of documents to send in a single bulk request, 
                            deault is 50 (optional)
        '''

        logging.info('[ INFO ] - Resetting ES index')
        if not index:
            index = self.index_name
        delete_index_result = await self._client.indices.delete(index=index)
        if delete_index_result.body['acknowledged']:
            await self.initialize_es(
                index=index,
                populate=populate,
                files_dir=files_dir,
                chunk_size=chunk_size
            )

    async def is_initalized(self, index: str = None) ->  Union[bool, ConnectionError]:
        if not index:
            index = self.index_name
        try:
            healthcheck = await self.health_check()
            if healthcheck:
                exists_result: HeadApiResponse = await self._client.indices.exists(index=index)
                if not exists_result.body:
                    return False
                return True
        except ConnectionError as err:
            raise err
        return False

    async def create_index(self, index: str = None) -> bool:
        if not index:
            index = self.index_name
        create_result: ObjectApiResponse = await self._client.indices.create(
                index=index,
                settings=create_settings(),
                mappings=default_mapping
            )
        return create_result['acknowledged']

    async def initialize_es(
        self,
        index: str = None,
        populate: bool = False,
        files_dir: str = None,
        chunk_size: int = 50
    ) -> None:
        '''
        Async initialize (or create if not existing) an ES index

        Checks if the specified index exists, if it doesn't, creates it.
        If the `populate` flag is set to True, will populate the index.
        If the index already exists, will only populate if the index is empty.

        :param index: name of the index to initialize (optional)
        :param populate: if True, populates the index using (optional)
        :param files_dir: directory path where the JSON files are located (optional)
        :param chuck_size: number of documents to send in a single bulk request, 
                            deault is 50 (optional)

        '''
        if not index:
            index = self.index_name
        logging.info('[ INFO ] - Initializing ES index: %s', index)
        is_initalized = await self.is_initalized(index=index)
        if not is_initalized:
            create_result = await self.create_index(index)
            if create_result:
                if populate:
                    await self.populate_index(
                        index=index,
                        files_dir=files_dir,
                        chuck_size=chunk_size
                    )
            else:
                raise Exception('Failed to create index: ', index)
        else:
            logging.info('[ INFO ] - %s already exists', index)
            if populate:
                count_response: ObjectApiResponse = await self._client.count(index=index)
                # If there are no documents in the index, will populate from json files
                if not count_response['count']:
                    await self.populate_index()

    async def populate_index(self, index: str = None, files_dir: str = None, chuck_size: int = 50) -> None:
        '''
        Async populate an ES index with data from directory files

        Retrieves JSON data, adds it to the Elasticsearch index in bulk, 
        using chunks of a specified size. If no directory path, it defaults to the class's 
        configuration for the data files directory path.

        :param index: name of the index to populate
        :param files_dir: directory path where the JSON files are located (optional)
        :param chuck_size: number of documents to send in a single bulk request, 
                            deault is 50 (optional)

        Raises exception if the directory does not exist or an issue during the data ingestion
        '''

        if not index:
            index = self.index_name
        if not files_dir:
            files_dir = self._config['data_files_dir_path']
        if not os.path.exists(files_dir):
            raise Exception('No directory exists at: ', files_dir)
        logging.info(
            '[ INFO ] - Populating index from files located in directory: %s', files_dir)
        files_gen = actions_list_gen(files_dir, index, chuck_size)
        tasks = []
        while files_gen:
            try:
                actions_list, count = next(files_gen)
                if actions_list:
                    logging.info(f'Adding {count} to bulk insert!')
                    tasks.append(self._client.bulk(operations=actions_list))
            except StopIteration:
                break
            except Exception as error:
                raise error
        await asyncio.gather(*tasks)

    async def search_index(
        self,
        text: str,
        index: str = None,
        fields: List[str] = None,
        page: int = 0,
        size: int = 20,
        with_highlight: bool = False,
        return_fields: List[str] = None
    ) -> SearchRequestResult:
        '''
        Async search an index based on the given text and criteria, 
            returns paginated matching documents.

        :param text: search text for query
        :param index: name of the index to search
        :param fields: fields to search the text in, defaults to ['bases'] (optional)
        :param page: page number to retrieve results for, defaults to 0 (optional)
        :param size: number of results to retrieve, defaults to 20 (optional)
        :param with_highlight: if True, includes highlighted snippets in the results, 
                            defaults to False (optional)
        :param return_fields: fields to return in the results. default returns all (optional)

        Returns:
            SearchRequestResult: dict, containing the total matches, current page number, 
                                    and a list of documents
        '''
        if not index:
            index = self.index_name
        start = page * size

        if fields:
            # filtering any values that are not existing properties of the index document
            fields = list(filter(lambda it: it in [
                          'bases', 'name', 'creator.handle', 'creator.name', 'creator.id'], fields))
        if not fields:
            fields = ['bases']

        if return_fields:
            # filtering any values that are not existing properties of the index document
            return_fields = list(
                filter(
                    lambda it: it in ['bases', 'name', 'createdAt', 'creator'],
                    return_fields
                )
            )

        highlight = {'fields': {'bases': {}}} if with_highlight else None

        resp: ObjectApiResponse = await self._client.search(
            index=index,
            source=True,
            query={"query_string": {'query': f'*{text}*', 'fields': fields}},
            from_=start,
            size=size,
            highlight=highlight,
            fields=return_fields
        )

        hits: IndexDocWithHighlight = []
        for hit in resp['hits']['hits']:
            doc = hit['_source']
            doc['id'] = hit['_id']
            if hit.get('highlight'):
                doc['highlight'] = hit['highlight']
            hits.append(doc)
        return {
            'total': resp['hits']['total']['value'],
            'page': page,
            'hits': hits
        }

    async def get_doc_by_id(self, _id: str, index: str = None) -> SearchHit:
        '''
        Async get a document by ID

        :param id: document ID
        :param index: name of index to search (optional)
        '''
        if not index:
            index = self.index_name
        result: ObjectApiResponse = await self._client.get(index=index, id=_id)
        doc = None
        if result['found']:
            doc = result['_source']
            doc['id'] = result['_id']
        return doc

    async def close_connection(self):
        '''
        Closes the current ES connection associated with this client
        '''
        await self._client.close()
