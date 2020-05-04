import os
from shutil import rmtree
import time
import json
from collections import defaultdict
import statistics
from datetime import datetime
import inspect
import sys

import requests

import utils

def from_short_uri_to_full_uri(short_uri):
    """
    replace:
    - wdt: by http://www.wikidata.org/prop/direct/
    - wd: by http://www.wikidata.org/entity/
    """
    for prefix, full in [('wd:', 'http://www.wikidata.org/entity/'),
                         ('wdt:', 'http://www.wikidata.org/prop/direct/')]:
        short_uri = short_uri.replace(prefix, full)

    return short_uri

assert from_short_uri_to_full_uri('wd:Q6534') == 'http://www.wikidata.org/entity/Q6534'
assert from_short_uri_to_full_uri('wdt:P17') == 'http://www.wikidata.org/prop/direct/P17'


QUERIES = {
    "subclass_of": """SELECT ?subclass1 ?subclass2 WHERE {
      ?subclass1 wdt:P279 ?subclass2 .
    }""",
    "instance_of": """SELECT ?type_id ?incident WHERE {
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        ?type_id wdt:P279* wd:Q1656682 .
        ?incident wdt:P31 ?type_id .
        ?incident rdfs:label ?label .
        }""",
    "inc_to_props": """SELECT ?incident ?property WHERE {
          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
          VALUES ?incident { %s }
          ?incident ?property ?value.
          FILTER(STRSTARTS(str(?property), str(wdt:)))
        }""",
    "inc_to_labels": """SELECT ?incident ?label ?lang WHERE {
          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
          VALUES ?incident { %s }
          ?incident rdfs:label ?label .
          filter(lang(?label) = 'it' || lang(?label) = 'en' || lang(?label) = 'nl')
          BIND(lang(?label) as ?lang)
    }""",
    "id_props" : """SELECT ?prop WHERE {
        ?prop wikibase:directClaim ?a .
        ?prop rdfs:label ?label.  
        filter(lang(?label) = "en") .
        ?prop wdt:P31*/wdt:P279* wd:Q19847637}
    """,
    "prop_to_labels": """SELECT ?prop ?label WHERE {
        ?prop wikibase:directClaim ?a .
        ?prop rdfs:label ?label.  
        filter(lang(?label) = "en").
        }""",
    "event_type_to_labels": """SELECT ?event_type ?label WHERE {
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
      VALUES ?event_type { %s }
      ?event_type rdfs:label ?label .
      filter langMatches( lang(?label), "EN" )
    }""",
}

WDT_SPARQL_URL = 'https://query.wikidata.org/sparql'
BATCH_SIZE = 250 # at 500 the api calls do not work anymore
DEV_LIMIT = 100000 # how many items do you want to have when you put verbose to 4 or higher
NUM_RETRIES = 5 # after how many retries do you give up
LOG_BATCHES = False # if True, send information about each batch to stdout
OVERWRITE = True # if True, overwrite existing results


def preprocess_inc_to_props(output_folder, verbose=0):
    """
    preprocess inc_to_props query by extracting list
    with all instance wd uris

    :rtype: list
    :return: list of wd incident uris
    """
    input_path = f'{output_folder}/instance_of.json'
    with open(input_path) as infile:
        instance_of = json.load(infile)

    inc_wd_uris = set()
    for event_type, inc_wd_uri in instance_of:
        inc_wd_uris.add(inc_wd_uri.replace('http://www.wikidata.org/entity/', 'wd:'))

    if verbose >= 1:
        print()
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'found {len(inc_wd_uris)} wd incident uris')

    return list(inc_wd_uris)

def preprocess_inc_to_labels(output_folder, verbose=0):
    """
    preprocess inc_to_labels query by extracting list
    with all instance wd uris

    :rtype: list
    :return: list of wd incident uris
    """
    input_path = f'{output_folder}/instance_of.json'
    with open(input_path) as infile:
        instance_of = json.load(infile)

    inc_wd_uris = set()
    for event_type, inc_wd_uri in instance_of:
        inc_wd_uris.add(inc_wd_uri.replace('http://www.wikidata.org/entity/', 'wd:'))

    if verbose >= 1:
        print()
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'found {len(inc_wd_uris)} wd incident uris')

    return list(inc_wd_uris)




def preprocess_event_type_to_labels(output_folder, verbose=0):
    """
    preprocess subclass_of  query by extracting
    list of event types

    :rtype: list
    :return: list
    """
    input_path = f'{output_folder}/subclass_of.json'
    with open(input_path) as infile:
        instance_of = json.load(infile)

    event_type_uris = set()
    for event_type_one, event_type_two in instance_of:
        for event_type in [event_type_one, event_type_two]:
            event_type_uris.add(event_type.replace('http://www.wikidata.org/entity/', 'wd:'))

    if verbose >= 1:
        print()
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'found {len(event_type_uris)} wd event type uris')

    return list(event_type_uris)



def post_process_subclass_of(response, verbose=0):
    """
    postprocess the response of the "subclass of" query

    :param dict response: api response

    :rtype: set of tuples
    :return: {(wd_uri, wd_uri)}
    """
    set_of_relations = set()
    for info in response['results']['bindings']:
        x = info['subclass1']['value']
        y = info['subclass2']['value']
        set_of_relations.add((x, y))

    if verbose >= 2:
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'found {len(set_of_relations)} unique relations')

    return list(set_of_relations)


def post_process_instance_of(response, verbose=0):
    """
    postprocess the response of the "instance of" query

    :param dict response: api response

    :rtype: set of tuples
    :return: {(event_type_wd_uri,
               incident_wd_uri)}
    """
    set_of_relations = set()
    type_id_to_num_incidents = defaultdict(set)
    for info in response['results']['bindings']:
        type_id  = info['type_id']['value']
        incident = info['incident']['value']
        set_of_relations.add((type_id, incident))

        type_id_to_num_incidents[type_id].add(incident)

    values = [len(incidents)
              for type_id, incidents in type_id_to_num_incidents.items()]

    if verbose >= 2:
        print()
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'unique number of event types: {len(type_id_to_num_incidents)}')
        print(f'number of incidents matched to event type: {sum(values)}')
        minimum, mean, maximum = min(values), statistics.mean(values), max(values)
        print(f'min, mean, max event type to num incidents: {minimum} {mean} {maximum}')

    return list(set_of_relations)



def post_process_inc_to_props(response, verbose=0):
    """
    postprocess the response of the "inc_to_props" query

    :param dict response: api response

    :rtype: set of tuples
    :return: {(incident_wd_uri,
               property_wdt_uri)}
    """
    set_of_relations = set()
    for info in response['results']['bindings']:
        incident = info['incident']['value']
        property = info['property']['value']
        set_of_relations.add((incident, property))

    if verbose >= 2:
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'found {len(set_of_relations)} properties of wd incident uris')

    return set_of_relations

def post_process_inc_to_labels(response, verbose=0):
    """
    postprocess the response of the "inc_to_labels" query

    :param dict response: api response

    :rtype: set of tuples
    :return: {(incident_wd_uri,
               english_label)}
    """
    inc_to_labels = defaultdict(dict)

    for info in response['results']['bindings']:
        incident = info['incident']['value']
        label = info['label']['value']
        lang = info['lang']['value']

        inc_to_labels[incident][lang] = label


    if verbose >= 2:
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'found {len(inc_to_labels)} incidents with at least label in Italian, English, and Dutch')


    set_of_relations = set()

    for inc, labels in inc_to_labels.items():
        for lang, label in labels.items():
            set_of_relations.add((inc, (lang, label)))

    return set_of_relations

def post_process_event_type_to_labels(response, verbose=0):
    """
    postprocess the response of the "event_type_to_labels" query

    :param dct response: api response

    :rtype: set of tuples
    :return: {(event_type_uri,
               english_label)}
    """
    set_of_relations = set()
    for info in response['results']['bindings']:
        event_type = info['event_type']['value']
        label = info['label']['value']
        set_of_relations.add((event_type, label))

    if verbose >= 2:
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'found {len(set_of_relations)} English labels for event type wd uris')

    return set_of_relations

def post_process_id_props(response, verbose=0):
    """
    postprocess the response of the "id_props" query

    :param dict response: api response

    :rtype: list of wd_prop_uri
    :return: [wd_prop_uri, ..]
    """
    set_of_relations = set()

    for info in response['results']['bindings']:
        prop = info['prop']['value']
        set_of_relations.add(prop)

    if verbose >= 2:
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'found {len(set_of_relations)} Wikidata property identifiers')

    return list(set_of_relations)

def post_process_prop_to_labels(response, verbose=0):
    """
    postprocess the response of the "prop_to_labels" query

    :param dict response: api response

    :rtype: list of tuples
    :return: [(wd_prop_uri,
               english_label)]
    """
    set_of_relations = set()

    for info in response['results']['bindings']:
        prop = info['prop']['value']
        label = info['label']['value']
        set_of_relations.add((prop, label))

    if verbose >= 2:
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'found {len(set_of_relations)} English labels for properties')

    return list(set_of_relations)


def get_results_with_retry(wdt_sparql_url, query):
    """
    Run SPARQL query multiple times until the results are there.

    :param str wdt_sparql_url: the Wikidata sparql url
    :param str query: the query to execute

    :rtype: dict
    :return: response from api
    """
    num_attempts = 0
    while True:
        try:
            r = requests.get(wdt_sparql_url,
                             params={'format': 'json', 'query': query})
            response = r.json()
            break
        except Exception as e:
            sys.stderr.write(f'{e},error, retrying\n')
            num_attempts += 1
            time.sleep(2)
        
            if num_attempts == NUM_RETRIES:
                print(f'unable to run query: {query}')
                response = {'results' : {'bindings' : []}}
                break

            continue

    return response



def validate(output, items, verbose=0):
    """
    determine for which items there is no information in the output

    :param list output: list of lists (item, piece_of_information)
    :param list items: list of items
    """
    item_to_information = defaultdict(set)

    items = [from_short_uri_to_full_uri(item)
             for item in items]

    for item, piece_of_information in output:
        item_to_information[item].add(piece_of_information)

    missing = set(items) - set(item_to_information)

    if verbose >= 2:
        print()
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'MISSING: no information found for {len(missing)} items')

def call_wikidata(sparql_query,
                  query_name,
                  verbose=0):
    """
    call wikidata sparql query and optionally store results in
    OUTPUT_FOLDER/QUERY_NAME.json

    :param str sparql_query: the sparql query
    :param str query_name: name of the query

    :rtype: dict
    :return: response
    """
    response = get_results_with_retry(wdt_sparql_url=WDT_SPARQL_URL,
                                      query=sparql_query)

    post_process_function = globals()[f'post_process_{query_name}']

    post_processed = post_process_function(response, verbose=verbose)

    return post_processed


def remove_prop_ids_from_props(all_props, output_folder, verbose=0):
    """
    filter Wikidata property identifiers from all properties

    :param set all_props: output from post_process_prop_to_labels
    :param str output_folder: the output folder
    """

    with open(f'{output_folder}/id_props.json') as infile:
        prop_ids = json.load(infile)

    statement_props = set()

    for prop_uri, label in all_props:
        if prop_uri not in prop_ids:
            statement_props.add((prop_uri, label))

    if verbose >= 2:
        this_function_name = inspect.currentframe().f_code.co_name
        print('INSIDE FUNCTION', this_function_name)
        print(f'found {len(statement_props)} Wikidata statements properties')
        print(f'{len(all_props) - len(statement_props)} Wikidata properties identifiers were discarded')

    return list(statement_props)


def run_queries(output_folder, verbose=0):
    """
    run queries as defined in global variable QUERIES
    in this Python module

    :param str output_folder: store the result to
    OUTPUT_FOLDER/QUERY_NAME.json
    """
    # (remove and) recreate folder
    if os.path.exists(output_folder):
        if OVERWRITE:
            rmtree(output_folder)
            if verbose >= 1:
                print(f'removed folder {output_folder}')
            os.mkdir(output_folder)
    else:
        os.mkdir(output_folder)

    if verbose >= 1:
        print(f'recreated folder {output_folder}')

    for query_name, sparql_query in QUERIES.items():

        if sparql_query:

            if verbose >= 4:
                sparql_query = sparql_query + f' LIMIT {DEV_LIMIT}'

            if verbose >= 2:
                print()
                print('QUERY NAME', query_name)
                print('QUERY', sparql_query)

            if query_name in {'subclass_of',
                              'instance_of',
                              'id_props',
                              'prop_to_labels'}:
                post_processed = call_wikidata(sparql_query=sparql_query,
                                               query_name=query_name,
                                               verbose=verbose)

                if query_name == 'prop_to_labels':
                    post_processed = remove_prop_ids_from_props(post_processed,
                                                                output_folder,
                                                                verbose=verbose)


            elif query_name in {'inc_to_props', 'inc_to_labels',
                                'event_type_to_labels'}:

                pre_process_function = globals()[f'preprocess_{query_name}']
                pre_processed = pre_process_function(output_folder, verbose=verbose)

                post_processed = set()

                count = 0
                for batch in utils.chunks(pre_processed, BATCH_SIZE):

                    items_string = ' '.join(batch)
                    the_query = sparql_query % items_string

                    if verbose >= 4:
                        the_query = the_query.replace(f' LIMIT {DEV_LIMIT}', '')

                    sys.stderr.write(f'working on batch starting from index {count} ({datetime.now()})\n')

                    verbose_here = verbose
                    if not LOG_BATCHES:
                        verbose_here = 0

                    part_post_processed = call_wikidata(sparql_query=the_query,
                                                        query_name=query_name,
                                                        verbose=verbose_here)

                    post_processed.update(part_post_processed)

                    count += len(batch)

                post_processed = list(post_processed)

                validate(output=post_processed,
                         items=pre_processed,
                         verbose=verbose)

            output_path = os.path.join(output_folder,
                                       f'{query_name}.json')

            with open(output_path, 'w') as outfile:
                json.dump(post_processed, outfile)

if __name__ == '__main__':

    output_folder = 'wd_cache'
    verbose = 2

    run_queries(output_folder, verbose=verbose)
