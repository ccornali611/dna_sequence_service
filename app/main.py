import logging
from typing import List

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from .elastic_search.client import ElasticSearchClient


async def on_startup() -> None:
    logging.info('on_startup')
    app.state.es_client =  ElasticSearchClient()
    await app.state.es_client.initialize_es(populate=True)

logging.basicConfig(filename='app_log.log', level=logging.INFO)
app = FastAPI(on_startup=[on_startup])

def get_es(request: Request) -> ElasticSearchClient:
    return request.app.state.es_client

@app.get('/health-check')
async def health_check(es_client: ElasticSearchClient = Depends(get_es)):
    assert isinstance(es_client, ElasticSearchClient)
    es_ping = await es_client.health_check()
    if es_ping:
        await es_client.initialize_es(populate=True)
        return JSONResponse('OK', status_code=200)
    else:
        return JSONResponse('INTERNAL_SERVER_ERROR', status_code=500)

@app.get('/api/search/')
async def search(
    text: str,
    fields: List[str] = None,
    page: int = 0,
    size: int = 20,
    with_highlight: bool = False,
    return_fields: List[str] = None,
    es_client: ElasticSearchClient = Depends(get_es),
):
    '''
    Endpoint to search an index based on the given text and criteria 
    and returns paginated matching documents
    '''
    r = await es_client.search_index(
        text,
        fields=fields,
        page=page,
        size=size,
        with_highlight=with_highlight,
        return_fields=return_fields
    )
    return JSONResponse(r, status_code=200)

if __name__ == '__main__':
    uvicorn.run(app, log_level=logging.INFO, port=80)
