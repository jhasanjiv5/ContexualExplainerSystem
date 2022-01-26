from SPARQLWrapper import SPARQLWrapper, JSON
import config


def discover_context(cps_name="Robot13"):
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
        ?s1 a sosa:Sensor;
             a td:Thing;
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
