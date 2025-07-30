from typing import Iterator

import requests

scheme='www'
domain = 'wheelodex.org'


def _project_names_from_wheelodex_response(
    response: requests.Response,
    ) -> Iterator[str]:

    for dict_ in response.json()['items']:
        yield dict_['name']


def _rev_deps(project: str) -> Iterator[str]:

    starting_page_query = '?page=1'

    json_api_sub_folder = f'/json/projects/{project}/rdepends'

    # Infinite loop if the next links in the response form 
    # a later cycle that excludes the hardcoded starting_page_query above, 
    # and if they are never Falsey.
    # Wheelodex is in control here, but we do want to traverse all 
    # its links.
    while True:
        url = f'https://{scheme}.{domain}{json_api_sub_folder}'

        response = requests.get(url)
        
        response.raise_for_status()

        yield from _project_names_from_wheelodex_response(response)

        json_api_sub_folder = response.json()['links']['next']


        if not json_api_sub_folder:
            break

        if json_api_sub_folder.endswith(starting_page_query):
            break




