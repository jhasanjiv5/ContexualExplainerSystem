from SPARQLWrapper import SPARQLWrapper, JSON, N3, POST
from rdflib import Graph
import configparser

config = configparser.ConfigParser()
config.read("contextual_explainer/src/config.ini")

sparql = SPARQLWrapper(config['resources']['sparql_endpoint'])

sparql.setCredentials(config['credentials']['sparql_username'], config['credentials']['sparql_password'])


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
            data.update({i:r[i]['value']})
        found_relationships.update({count: data})
        count += 1
    return found_relationships


def show_effects(ontology_prefix, ontology_uri, subject):
    sparql.setQuery(
        """ PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX %s: %s
            PREFIX cd: <https://things.interactions.ics.unisg.ch#>
            select ?entity ?influence ?influence_type ?rating ?feedback
            where{
                ?influence a prov:Entity .
                %s:%s brick:hasTag ?t1 .
                ?entity a prov:Entity;
                prov:wasInfluencedBy ?influence;
                prov:qualifiedInfluence [ 
                a prov:EntityInfluence ; 
                prov:influencer ?influence ;
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
    sparqlpost = SPARQLWrapper(config['resources']['sparql_endpoint'] + "/statements")
    sparqlpost.setCredentials(config['credentials']['sparql_username'], config['credentials']['sparql_password'])

    sparqlpost.setQuery(
        """ PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX %s: %s
            PREFIX cd: <https://things.interactions.ics.unisg.ch#>

            INSERT{ 
                ?m1 a %s:%s ;
                    a prov:Entity .
                %s:%s brick:hasTag ?t1 .
                ?t1 a %s:%s ;
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
                SELECT  ?m1 ?t1
                WHERE{
                BIND(IRI(CONCAT("https://things.interactions.ics.unisg.ch#context",
                strUUID())) as ?m1) .
                BIND(IRI(CONCAT("https://things.interactions.ics.unisg.ch#context",
                strUUID())) as ?t1) .
                }
            }
            """ % (ontology_prefix, ontology_uri, ontology_prefix, object, ontology_prefix, subject, ontology_prefix, feature, predicate, rating, feedback )

    )
    sparqlpost.setMethod(POST)
    sparql.setReturnFormat(JSON)
    qres2 = sparqlpost.query().convert()
    return qres2


def discover_context(ontology_prefix, ontology_uri, seed, cps_name=['RB30_OG4_61-400_standing_lamp_1']):
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
            %s:%s %s:%s ?td
            }""" % (ontology_prefix, ontology_uri, ontology_prefix, c, ontology_prefix, seed)

        )
        cps_td = ''

        sparql.setReturnFormat(N3)
        qres1 = sparql.query().convert()
        g = Graph()
        g.parse(data=qres1, format="n3")
        data = g.serialize(format='n3')
        cps_td = data.split("\n\n")[1].split('"')[1]
        # TODO: can we use select instead of describe for sparql query? td link extraction would be easier. Perhaps add title to the instances and then select instances based on titles. it would return JSON and then easier to extract the TD link.
        # TODO: ask users for context relationship like hasTD
        # TODO: solve error that includes kims lamp. it gives an opportunity to filter on expeected terms in any data stream. Update error info to say exactly that 
        sparql.setQuery(
            """PREFIX %s: %s
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            select ?TD{
                %s:%s brick:hasLocation ?loc .
                ?things brick:hasLocation ?loc;
                                   hsg:%s ?TD .  
            }	
            """ % (ontology_prefix, ontology_uri, ontology_prefix, c, seed)
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





