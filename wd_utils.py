import os
from shutil import rmtree
import time
import json
from collections import defaultdict
import statistics
from datetime import datetime

import requests

import utils


QUERIES = {
    "subclass_of": """SELECT ?subclass1 ?subclass2 WHERE {
      ?subclass1 wdt:P279 ?subclass2 .
    }""",
    "instance_of": """SELECT ?type_id ?incident WHERE {
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        ?type_id wdt:P279* wd:Q1656682 .
        ?incident wdt:P31 ?type_id .
        ?incident rdfs:label ?label .
        FILTER (langMatches( lang(?label), "EN" ) )
        }""",
    "inc_to_props": """SELECT ?incident ?property WHERE {
          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
          VALUES ?incident { %s }
          ?incident ?property ?value.
          FILTER(STRSTARTS(str(?property), str(wdt:)))
        }""",
    "inc_to_labels": """SELECT ?incident ?label WHERE {
          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
          VALUES ?incident { %s }
          ?incident rdfs:label ?label .
          filter langMatches( lang(?label), "EN" )
    }""",
    "event_type_to_labels": """SELECT ?event_type ?label WHERE {
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
      VALUES ?event_type { %s }
      ?event_type rdfs:label ?label .
      filter langMatches( lang(?label), "EN" )
    }""",
    "prop_to_labels": """SELECT ?prop ?label WHERE {
        ?prop wikibase:directClaim ?a .
        ?prop rdfs:label ?label.  
        filter(lang(?label) = "en").
        }""",
}

WDT_SPARQL_URL = 'https://query.wikidata.org/sparql'
BATCH_SIZE = 500

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
    set_of_relations = set()
    for info in response['results']['bindings']:
        incident = info['incident']['value']
        label = info['label']['value']
        set_of_relations.add((incident, label))

    if verbose >= 2:
        print(f'found {len(set_of_relations)} English labels for wd incident uris')

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
        print(f'found {len(set_of_relations)} English labels for event type wd uris')

    return set_of_relations


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
        event_type = info['prop']['value']
        label = info['label']['value']
        set_of_relations.add((event_type, label))

    if verbose >= 2:
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
    while True:
        try:
            r = requests.get(wdt_sparql_url,
                             params={'format': 'json', 'query': query})
            response = r.json()
            break
        except Exception as e:
            print(e, 'error, retrying')
            time.sleep(2)
            continue

    return response


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


def run_queries(output_folder, verbose=0):
    """
    run queries as defined in global variable QUERIES
    in this Python module

    :param str output_folder: store the result to
    OUTPUT_FOLDER/QUERY_NAME.json
    """
    # (remove and) recreate folder
    if os.path.exists(output_folder):
        rmtree(output_folder)
        if verbose >= 1:
            print(f'removed folder {output_folder}')
    os.mkdir(output_folder)
    if verbose >= 1:
        print(f'recreated folder {output_folder}')

    for query_name, sparql_query in QUERIES.items():

        if sparql_query:

            if verbose >= 3:
                sparql_query = sparql_query + ' LIMIT 100'

            if verbose >= 2:
                print()
                print(query_name)
                print(sparql_query)

            if query_name in {'subclass_of',
                              'instance_of',
                              'prop_to_labels'}:
                post_processed = call_wikidata(sparql_query=sparql_query,
                                               query_name=query_name,
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

                    if verbose >= 2:
                        print()
                        print(f'working on batch starting from index {count} ({datetime.now()})')

                    part_post_processed = call_wikidata(sparql_query=the_query,
                                                        query_name=query_name,
                                                        verbose=verbose)

                    post_processed.update(part_post_processed)

                    count += len(batch)


                post_processed = list(post_processed)

            output_path = os.path.join(output_folder,
                                       f'{query_name}.json')

            with open(output_path, 'w') as outfile:
                json.dump(post_processed, outfile)

if __name__ == '__main__':

    # TODO: postprocess functions
    # TODO: add preprocess functions for properties and labels
    # TODO: run this thing on kyoto at some point or other server

    output_folder = 'wd_cache'
    verbose = 3

    run_queries(output_folder, verbose=verbose)
