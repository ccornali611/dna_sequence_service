# dna_sequence_service

On startup, will initialize ES index. There is one API endpoint to search the index. This service is setup an average dataset. You can scale it, please see `Notes for scaling` section.

### Setup
1) Run `make copy-config`
2) Set the values in `./app/elastic_search/config/config.ini`
   - `data_files_dir_name` is not required, will initialize the ES database will JSON files from `./app/data/test_set`
   - If you do not wish to use the data in `./dna_sequence/data/test_set`. Add JSON files to directory of choice and save relative path in `./app/elastic_search/config/config.ini`
3) [Run locally](#run-locally) or [Run on Docker](#docker-run)


<div id="run-locally"></div>
###### Run locally
1) If you wish to use a virtual environment, run `python3 -m venv .[venv name]` and `. .[venv name]/bin/activate`
1) Run `make install-req`
2) Run `make run-es`
3) Run `make start-app`

<div id="docker-run"></div>
##### Run on Docker
1) Run `make run`

### Notes for scaling
If you want to scale the index please review: https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules.html#index-refresh-interval-setting
To make changes to the index setting, set those values in the `./app/elastic_search/config/config.ini` file.
If you want to change the length of the ngram difference, `max_ngram_diff` must be greater than the difference of `min_ngram` and `max_ngram`.
Another helpful resource regarding scaling: https://www.elastic.co/guide/en/elasticsearch/reference/current/tune-for-indexing-speed.html
