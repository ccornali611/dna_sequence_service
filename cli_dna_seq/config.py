import asyncio

from cli_dna_seq import (ES_CONNECTION_ERROR, SUCCESS, ElasticSearchClient,
                         __app_name__, async_helper)


def init_app() -> int:
    """Initialize the application."""
    es = ElasticSearchClient()
    loop = asyncio.new_event_loop()
    is_initialized = async_helper.make_async_call(es.is_initalized(), loop)
    if is_initialized is True:
        async_helper.make_async_call(es.close_connection(), loop)
        return SUCCESS
    elif is_initialized is False:
        async_helper.make_async_call(es.initialize_es(populate=True), loop)
        async_helper.make_async_call(es.close_connection(), loop)
        return SUCCESS
    else:
        return ES_CONNECTION_ERROR
