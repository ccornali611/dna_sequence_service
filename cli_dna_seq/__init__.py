__app_name__ = "cli_dna_seq"
__version__ = "1.0.0"

from app.elastic_search.client import ElasticSearchClient

(
    SUCCESS,
    ES_CONNECTION_ERROR,
) = range(2)

ERRORS = {
    ES_CONNECTION_ERROR: 'es connection error'
}
