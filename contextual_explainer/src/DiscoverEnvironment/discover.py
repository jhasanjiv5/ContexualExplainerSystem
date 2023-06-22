from SPARQLWrapper import SPARQLWrapper, JSON, N3, POST
from rdflib import Graph
import configparser

config = configparser.ConfigParser()
config.read("contextual_explainer/src/config.ini")

sparql = SPARQLWrapper(config['resources']['sparql_endpoint'])

sparql.setCredentials(config['credentials']['sparql_username'],
                      config['credentials']['sparql_password'])


def select_relationships(ontology_prefix, ontology_uri, subject, object):
    sparql.setQuery(
        """ PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX %s: %s
            PREFIX cd: <https://things.interactions.ics.unisg.ch#>
            select ?influence_type ?rating 
            where{
                ?influence a prov:Entity ;
               a %s:%s .
                %s:%s brick:hasTag ?t1 .
                ?entity a prov:Entity;
                prov:wasInfluencedBy ?influence;
                prov:qualifiedInfluence [ 
                a prov:EntityInfluence ; prov:influencer ?m1 ; cd:influenceType ?influence_type ;  cd:rating ?rating ;] .
                } 
            """ % (ontology_prefix, ontology_uri, ontology_prefix, object, ontology_prefix, subject)
    )
    found_relationships = {}
    count = 0
    sparql.setReturnFormat(JSON)
    qres2 = sparql.query().convert()
    for r in qres2['results']['bindings']:
        data = {}
        for i in r:
            data.update({i: r[i]['value']})
        found_relationships.update({count: data})
        count += 1
    return found_relationships


def show_effects(ontology_prefix, ontology_uri, subject):
    sparql.setQuery(
        """ PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX %s: %s
            PREFIX cd: <https://things.interactions.ics.unisg.ch#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            select ?influence ?influence_type ?feature ?rating ?feedback
            where{
               
                %s:%s brick:hasTag ?t1 .
    
                ?i a prov:Entity ;
                   rdfs:label ?influence .
    			
    			?t1 rdfs:label ?feature ;
                			a prov:Entity;
                			prov:wasInfluencedBy ?i;
                            prov:qualifiedInfluence [ 
                            a prov:EntityInfluence ; 
                            prov:influencer ?i ;
                            cd:influenceType ?influence_type ; 
                            cd:rating ?rating ;
                            cd:textualFeedback ?feedback ; ] .

                } 
        """ % (ontology_prefix, ontology_uri, ontology_prefix, subject)
    )
    found_relationships = {}
    sparql.setReturnFormat(JSON)
    qres2 = sparql.query().convert()
    count = 0
    for r in qres2['results']['bindings']:
        data = {}
        for i in r:
            data.update({i: r[i]['value']})
        found_relationships.update({count: data})
        count += 1
    return found_relationships


def insert_relationship(ontology_prefix, ontology_uri, subject, predicate, object, count, feedback, rating, feature):
    sparqlpost = SPARQLWrapper(
        config['resources']['sparql_endpoint'] + "/statements")
    sparqlpost.setCredentials(
        config['credentials']['sparql_username'], config['credentials']['sparql_password'])

    sparqlpost.setQuery(
        """ PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX %s: %s
            PREFIX cd: <https://things.interactions.ics.unisg.ch#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            INSERT{ 
                ?m1 a %s:%s ;
                    a prov:Entity ;
                    rdfs:label '%s' .
                %s:%s brick:hasTag ?t1 .
                ?t1 a %s:%s ;
                    rdfs:label '%s' ;
                a prov:Entity ;
                prov:wasInfluencedBy ?m1 ;
                prov:qualifiedInfluence [ 
                a prov:EntityInfluence ; 
                prov:influencer ?m1 ;
                cd:influenceType "%s" ;
                cd:rating %s ;
                cd:textualFeedback "%s" ; ] .
                } 
                
            WHERE{
               
                BIND(IRI(CONCAT("https://things.interactions.ics.unisg.ch#context",
                strUUID())) as ?m1) .
                BIND(IRI(CONCAT("https://things.interactions.ics.unisg.ch#context",
                strUUID())) as ?t1) .
                
            }
            """ % (ontology_prefix, ontology_uri, ontology_prefix, object, object, ontology_prefix, subject, ontology_prefix, feature, feature, predicate, rating, feedback)

    )
    sparqlpost.setMethod(POST)
    sparql.setReturnFormat(JSON)
    qres2 = sparqlpost.query().convert()
    return qres2


def discover_context(ontology_prefix, ontology_uri, seed, cps_name=['ex_lamp_1']):
    """
    Query the context and extract the location and observable contextual variables

    :return: location, context_variables
    """
    # prefix should also be passed or not?
    for c in cps_name:
        sparql.setQuery(
            """PREFIX %s: %s
            DESCRIBE ?td where
            {
            %s:%s %s:hasTD ?td
            }""" % (ontology_prefix, ontology_uri, ontology_prefix, c, ontology_prefix)

        )
        cps_td = ''

        sparql.setReturnFormat(N3)
        qres1 = sparql.query().convert()
        g = Graph()
        g.parse(data=qres1, format="n3")
        data = g.serialize(format='n3')
        cps_td = data.split("\n\n")[1].split('"')[1]
        # TODO: store the ontology prefixes of all the variables
        sparql.setQuery(
            """PREFIX %s: %s
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            select ?TD{
                %s:%s brick:%s ?loc .
                ?things brick:%s ?loc;
                                   hsg:hasTD ?TD .  
            }	
            """ % (ontology_prefix, ontology_uri, ontology_prefix, c, seed, seed)
        )

        sparql.setReturnFormat(JSON)
        qres2 = sparql.query().convert()

        context_variables = []

        for r in qres2['results']['bindings']:
            for i in r:
                if 'datatype' in r[i] and r[i]['datatype'] == "http://www.w3.org/2001/XMLSchema#anyURI":
                    context_variables.append(r[i]['value'])

        return cps_td, context_variables