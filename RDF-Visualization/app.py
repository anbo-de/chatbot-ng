from flask import *  
import os 
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
from pyvis.network import Network 
from SPARQLWrapper import SPARQLWrapper, JSON , XML
import requests 
from configparser import ConfigParser
app = Flask('testapp')
app.config['TEMPLATES_AUTO_RELOAD'] = True
parser = ConfigParser()
parser.read("CONFIG.TXT") 
URL = parser.get("config", "URL")
SECOND_URL = parser.get("config", "SECOND_URL")
USERNAME = parser.get("config", "USERNAME")
PASSWORD = parser.get("config", "PASSWORD")
HEIGHT = parser.get("config", "HEIGHT") 
GRAVITY = parser.get("config", "GRAVITY")
SPRING_LENGTH = parser.get("config", "SPRING_LENGTH")
CENTRAL_GRAVITY = parser.get("config", "CENTRAL_GRAVITY")



@app.route('/visualize/<graphID>')
def show_graph(graphID): 
	sparql_database = SPARQLWrapper(URL)
	sparql_database.setCredentials(USERNAME, PASSWORD)
	sparql_query = """ 
		DESCRIBE *
		FROM <""" + graphID  + """>
		WHERE {
				?s a qa:AnnotationOfAnswerSPARQL.
				?s oa:hasBody ?sparqlQueryOnDBpedia .
				?s oa:annotatedBy ?annotatingService .
				?s oa:annotatedAt ?time .
			}
			"""   
	sparql_database.setQuery(sparql_query)
	sparql_database.setReturnFormat(XML)
	sparql_database.setMethod("POST")
	results = sparql_database.query().convert()  
	networkx_graph = rdflib_to_networkx_graph(results)  
	net = Network(height=HEIGHT, width="100%")
	net.from_nx(networkx_graph)
	net.show_buttons(filter_=['physics'])
	net.force_atlas_2based(gravity=GRAVITY,spring_length = SPRING_LENGTH, central_gravity = CENTRAL_GRAVITY)
	save = net.show("templates/index.html")
	return render_template('index.html')





@app.route('/visualize/example')
def html_page():  
	get_graph_id = requests.post(SECOND_URL,
			params={
					"question": "What is the real name of hulk?",
					"componentlist[]": ["NED-DBpediaSpotlight",
					"QueryBuilderSimpleRealNameOfSuperHero",
					"SparqlExecuter",
					"OpenTapiocaNED",
					"BirthDataQueryBuilder",
					"WikidataQueryExecuter"]
	})
	res_json = get_graph_id.json()   
	graph_id_test = res_json['inGraph']  
	sparql_database = SPARQLWrapper(URL)
	sparql_database.setCredentials(USERNAME, PASSWORD)
	sparql_query = """ 
	DESCRIBE *
	FROM <""" + graph_id_test  + """>
	WHERE {
			?s a qa:AnnotationOfAnswerSPARQL.
			?s oa:hasBody ?sparqlQueryOnDBpedia .
			?s oa:annotatedBy ?annotatingService .
			?s oa:annotatedAt ?time .
		}
		"""   
	sparql_database.setQuery(sparql_query)
	sparql_database.setReturnFormat(XML)
	sparql_database.setMethod("POST")
	results = sparql_database.query().convert()  
	networkx_graph = rdflib_to_networkx_graph(results)  
	net = Network(height=HEIGHT, width="100%")
	net.from_nx(networkx_graph)
	net.show_buttons(filter_=['physics'])
	net.force_atlas_2based(gravity=GRAVITY,spring_length = SPRING_LENGTH, central_gravity = CENTRAL_GRAVITY) 
	save = net.show("templates/exampleviz.html")
	return render_template('/exampleviz.html')


if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)
	app.run()