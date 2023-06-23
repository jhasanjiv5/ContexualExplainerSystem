from SPARQLWrapper import SPARQLWrapper, JSON, N3, POST
from rdflib import Graph
import configparser
import pandas as pd
import requests
import time

config = configparser.ConfigParser()
config.read("contextual_explainer/src/config.ini")

sparql = SPARQLWrapper(config['resources']['sparql_endpoint'])

sparql.setCredentials(config['credentials']['sparql_username'],
                      config['credentials']['sparql_password'])

# Find entities at the location that has the name same as the contextual influences
def find_entities(ontology_prefix, ontology_uri, seed, ci_name, location):
    sparql.setQuery(
        """ PREFIX %s: %s
            PREFIX td: <https://www.w3.org/2019/wot/td#>
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            SELECT * where
            {
                ?t ?b ?a;
                %s:%s %s:%s;
                hsg:hasTD ?td .
                filter(regex(str(?a), %s))
            } 
            """ % (ontology_prefix, ontology_uri, ontology_prefix, seed, ontology_prefix, location, ci_name)
    )
    found_entities = {}
    count = 0
    sparql.setReturnFormat(JSON)
    qres2 = sparql.query().convert()
    for r in qres2['results']['bindings']:
        for i in r:
            if 'datatype' in r[i] and r[i]['datatype'] == "http://www.w3.org/2001/XMLSchema#anyURI":
                found_entities.append(r[i]['value'])
    return found_entities

# Collect URLs and methods from the TDs for modifying the values as per the obtained counterfactuals
def get_affordances(found_entites):
    links_dict = dict()
    for l in found_entites:
        results = requests.get(l)
        r = results.json()
        for i in r['properties']:
            if r['properties'][i]['forms'][0]['op'][0] == "writeproperty":
                links_dict.update({
                    i: {'url':r['properties'][i]['forms'][0]['href'], 'method':r['properties'][i]['forms'][0]['htv:methodName']}})
    return links_dict

# Set rating values based on the reaction of the context update
def set_rating(links_dict, CPS_url, attribute, ci, cf_value, relationship):
    # TODO: fix the method according to the setup.
    # TODO: get the token by installing android mobile app
    rating = 0
    value_initial = requests.request('GET', CPS_url, payload=attribute) # TODO: fix it for getting the specific value of the CPS attribute

    print(value_initial.text.encode('utf8'))

    payload = '%s=%s' % (ci, cf_value)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request(links_dict['method'], links_dict['url'], headers=headers, data=payload)

    print(response.text.encode('utf8'))

    value_new = requests.request('GET', CPS_url, payload=attribute) # TODO: fix it for getting the specific value of the CPS attribute

    print(value_new.text.encode('utf8'))
    if value_new.status_code == 200:
        if value_initial < value_new and relationship == "positiveInfluence":
            rating = 1
        else:
            rating = 0
    return rating
