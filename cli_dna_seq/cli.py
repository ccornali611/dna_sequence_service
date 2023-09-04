import asyncio
import os
from typing import Optional

import typer
from rich import print as rich_print
from rich.console import Console
from rich.table import Table

from cli_dna_seq import (SUCCESS, ElasticSearchClient, __app_name__,
                         __version__, async_helper, config)

app = typer.Typer()

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )) -> None:
    return

@app.command()
def init(
    env: str = typer.Option(
        'local',
        "--app-env",
        "-env",
        prompt="app environment (local or dev)",
    )
) -> None:
    '''
    Initialize the ES database, if it is not already
    '''
    os.environ['APP_ENV'] = env
    app_init_error = config.init_app()

    if app_init_error != SUCCESS:
        typer.secho(
            'If you used "dev" for the `APP_ENV`, ensure your elasticsearch docker container is up and running, then try again', 
            fg=typer.colors.YELLOW
        )
        typer.secho(
            f'Initializing ES failed with "{ConnectionError}"',
            fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        typer.secho('Elasticsearch has been initialized for index', fg=typer.colors.GREEN)

@app.command('search')
def search(
    # env: str = typer.Option(
    #     'local',
    #     "--app-env",
    #     "-env",
    #     prompt="app environment (local or dev)",
    # ),
    text: str = typer.Option(
        '',
        "--text",
        "-t",
        help="text to query"
    ),
    fields: str = typer.Option(
        None,
        "--fields",
        "-f",
        help="Comma separated list fields to query (only valid options: 'bases', 'name', 'creatror.handle', 'creator.name')",
        is_eager=True,
    ),
    page: int = typer.Option(
        0,
        "--page",
        "-pg",
        help="pagination"
    ),
    size: int = typer.Option(
        20,
        "--size",
        "-sz",
        help="Length of results to be returned"
    ),
    with_highlight: bool =  typer.Option(
        False,
        "--with-highlight",
        "-wh",
        help="If true will return highlighted sections of the ES document",
        is_flag=True
    ),
    return_fields: str =  typer.Option(
        None,
        "--return-fields",
        help="Comma separated list of fields to return from the ES doument. "
    ),
):
    '''
    Search an index based on the given text and criteria and returns paginated matching documents
    '''
    es = ElasticSearchClient()

    if fields:
        fields = fields.split(',')
    if return_fields:
        return_fields = return_fields.split(',')

    loop = asyncio.new_event_loop()
    r = async_helper.make_async_call(es.search_index(
        text,
        fields=fields,
        page=page,
        size=size,
        with_highlight=with_highlight,
        return_fields=return_fields
    ), loop)
    
    if r['total']:
        total = r['total']
        hits= r['hits']
        page = r['page'] + 1
        on_page = len(hits)
        num_remaining_results = total - (page * on_page)
        total_pages = round(total / size)
        overview_table = Table('Total', 'Page', 'On page', 'Remaining Results')
        overview_table.add_row(f'{total}', f'{page}', f'{on_page}', f'{num_remaining_results}')
        data_table = Table('ID', 'Name', 'Bases', 'Created At', 'Creator ID', 'Creator Name')
        if with_highlight:
            data_table.add_column('highlights')
        for hit in hits:
            row_data = [hit['id'],
                hit['name'],
                hit['bases'],
                hit['createdAt'],
                hit['creator']['id'],
                hit['creator']['name']
                ]
            if with_highlight:
                row_data.append(str(hit['highlight']['bases']))
            data_table.add_row(*row_data)

        console = Console()
        console.print(overview_table)
        console.print(data_table)

        typer.secho(
            f' {on_page} / {total}', 
            fg=typer.colors.YELLOW
        )
        if page < total_pages:
            typer.secho(
                f'Page {page} of {total_pages}, to view next paginated results, `python3 -m cli_dna_seq search --text {text} -pg {page}`', 
                fg=typer.colors.YELLOW
            )
    else:
        print(f'No documents were found matching "{text}"')

@app.command('get-by-id')
def get_by_id(
    _id: str = typer.Option(
        "--id",
        help="ES document ID"
    ),
    view_bases: bool = typer.Option(
        False,
        '--view-bases',
        help='will display the value "bases" value',
        is_flag=True
    )
):
    '''
    Search an index based on the given text and criteria and returns paginated matching documents
    '''
    es = ElasticSearchClient()
    loop = asyncio.new_event_loop()
    r = async_helper.make_async_call(es.get_doc_by_id(_id), loop)
    if view_bases:
        rich_print(r)
    else:
        data_table = Table('ID', 'Name', 'Bases', 'Created At', 'Creator ID', 'Creator Name')
        Console.print(data_table)
