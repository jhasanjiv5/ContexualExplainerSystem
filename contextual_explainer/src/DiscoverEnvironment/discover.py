from SPARQLWrapper import SPARQLWrapper, JSON, N3, POST
import config
from rdflib import Graph

sparql = SPARQLWrapper(config.sparql_endpoint)

sparql.setCredentials(config.sparql_username, config.sparql_password)


def select_relationships(ontology_prefix, ontology_uri, subject, object):
    sparql.setQuery(
        """PREFIX %s: %s
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX san: <http://www.irit.fr/recherches/MELODI/ontologies/SAN#>
PREFIX cd: <https://things.interactions.ics.unisg.ch#>
select ?type where{
    %s:%s ?t ?a .
    ?a rdf:type %s:%s ;
       san:hasEffect ?effect .
    ?effect rdf:type ?type ;
            cd:observationCount ?count .
} """ % (ontology_prefix, ontology_uri, ontology_prefix, subject, ontology_prefix, object)
    )
    found_relationships = []
    sparql.setReturnFormat(JSON)
    qres2 = sparql.query().convert()
    for r in qres2['results']['bindings']:
        data = []
        for i in r:
            data.append(r[i]['value'])
        found_relationships.append(data)
    return found_relationships


def show_effects(ontology_prefix, ontology_uri, subject):
    sparql.setQuery(
        """PREFIX %s: %s
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX cd: <https://things.interactions.ics.unisg.ch#>
PREFIX san: <http://www.irit.fr/recherches/MELODI/ontologies/SAN#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select ?entity ?type ?count ?rating ?feedback where{
    %s:%s san:isActedUponBy ?e .
    ?e rdf:type ?entity ;
       san:hasEffect ?effect .
    ?effect rdf:type ?type ;
            cd:observationCount ?count ;
    	cd:textualFeedback ?feedback ;
        cd:influenceRating ?rating .
} """ % (ontology_prefix, ontology_uri, ontology_prefix, subject)
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


def insert_relationship(ontology_prefix, ontology_uri, subject, predicate, object, count, feedback, rating):
    sparqlpost = SPARQLWrapper(config.sparql_endpoint + "/statements")
    sparqlpost.setCredentials(config.sparql_username, config.sparql_password)

    sparqlpost.setQuery(
        """PREFIX %s: %s
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX cd: <https://things.interactions.ics.unisg.ch#>
PREFIX san: <http://www.irit.fr/recherches/MELODI/ontologies/SAN#>

INSERT{ 
    ?m1 a %s:%s .
    ?o1 a cd:%s ;
    cd:observationCount %s ;
    cd:textualFeedback "%s";
    cd:influenceRating  %s.
    ?m1 san:hasEffect ?o1 .
    %s:%s san:isActedUponBy ?m1 .
    
    } 
    
WHERE{
    SELECT  ?m1 ?o1
    WHERE{
    
    BIND(IRI(CONCAT("https://things.interactions.ics.unisg.ch#contextsensor",strUUID())) as ?m1) . 
    BIND(IRI(CONCAT("https://things.interactions.ics.unisg.ch#contextseffect",strUUID())) as ?o1) .
    
    }
    }	
        """ % (
            ontology_prefix, ontology_uri, ontology_prefix, object, predicate, count, feedback, rating, ontology_prefix,
            subject)

    )
    sparqlpost.setMethod(POST)
    sparql.setReturnFormat(JSON)
    qres2 = sparqlpost.query().convert()
    return qres2


def discover_context(ontology_prefix, ontology_uri, cps_name=['RB30_OG4_61-400_standing_light_1']):
    """
    Query the context and extract the location and observable contextual variables

    :return: location, context_variables
    """
    # prefix should also be passed or not?
    for c in cps_name:
        sparql.setQuery(
            """PREFIX %s: %s
            PREFIX brick: <https://brickschema.org/schema/Brick#>
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
        # TODO: can we use select instead of describe for sparql query? td link extraction would be easier. Perhaps add title to the instances and then select instances based on titles. it would return JSON and then easier to extract the TD link.
        print(cps_td)

        sparql.setQuery(
            """PREFIX %s: %s
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            select ?TD{
                ?room brick:regulates %s:%s ;
                      (brick:hasPoint|brick:hasPart|hsg:hasTD|brick:hasLocation)* ?TD .   
            }	
            """ % (ontology_prefix, ontology_uri, ontology_prefix, c)
        )

        sparql.setReturnFormat(JSON)
        qres2 = sparql.query().convert()

        context_variables = []

        for r in qres2['results']['bindings']:
            for i in r:
                if 'datatype' in r[i] and r[i]['datatype'] == "http://www.w3.org/2001/XMLSchema#anyURI":
                    context_variables.append(r[i]['value'])

        return cps_td, context_variables


'''def discover_context(cps_name="Robot13"):
    """
    Query the context and extract the location and observable contextual variables

    :return: location, context_variables
    """
    sparql = SPARQLWrapper(config.sparql_endpoint)
    sparql.setCredentials(config.sparql_username, config.sparql_password)

    sparql.setQuery(
        """PREFIX td: <https://www.w3.org/2019/wot/td#> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select ?cpsName ?label where 
    {           
        ?c a td:thing ;
        td:name ?cpsName ;
        rdfs:label ?label .
        
        FILTER regex(?cpsName, "%s") .
    }""" % cps_name
    )
    sparql.setReturnFormat(JSON)
    qres1 = sparql.query().convert()
    location = ''
    for r in qres1['results']['bindings']:
        location = r['label']['value']
    print(location)

    sparql.setQuery(
        """PREFIX bot: <https://w3id.org/bot#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    PREFIX td: <https://www.w3.org/2019/wot/td#>
    PREFIX hctl: <https://www.w3.org/2019/wot/hypermedia#>
    PREFIX htv: <http://www.w3.org/2011/http#>
    
    select ?roomName ?sensorName ?methodName ?link where {
        ?room a bot:Space ;          
                rdfs:label ?roomName ;
             bot:containsElement ?s1 .
        ?s1 a sosa:Sensor ;
             a td:Thing ;
            td:name ?sensorName  ;
    	    td:hasPropertyAffordance ?pi .
        ?pi a td:PropertyAffordance;
            td:hasForm ?f .
        ?f a hctl:Form ;
            htv:methodName ?methodName ;
            hctl:hasTarget ?link .
       
        FILTER regex(?roomName, "^%s") .
        }
        """ % location
    )
    sparql.setReturnFormat(JSON)
    qres2 = sparql.query().convert()
    print(qres2)
    context_variables = []

    for r in qres2['results']['bindings']:
        context_variables.append({"context_variable": r['sensorName']['value'],
                                  "room_name": r['roomName']['value'],
                                  "method": r['methodName']['value'],
                                  "link": r['link']['value']
                                  })

    return location, context_variables
'''
