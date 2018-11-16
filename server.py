#!/usr/bin/env python
# coding: utf-8

from flask import (
    Flask,
    render_template
)
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
import requests
import json

# Create the application instance
app = Flask(__name__, template_folder="templates")

def parseBusToObject(text):
	busAttrs = text.split(' - ')
	
	bus = {
		'name': busAttrs[0].replace('\u00a0',''),
		'minutes': busAttrs[1].replace('\u00a0','')
	}
	
	return bus
	
def parseHaltestelleToObject(text):
	haltestelleAttrs = text.split(' - ')
	
	haltestelle = {
		'num': haltestelleAttrs[0],
		'name': haltestelleAttrs[1]
	}
	
	return haltestelle

def getNextBus(haltestelle, bus):
	
	body = {
		'parada': haltestelle
	}
	
	busUrl = "https://www.emtvalencia.es/ciudadano/modules/mod_tiempo/busca_parada.php"
	res = []
	request = requests.post(busUrl, data=body)
	request.encoding = 'UTF-8'
	response = requests.post(busUrl, data=body)
	busList = list(response.text.split('<br/>'))
	
	for bus in busList:
		parsedBus = BeautifulSoup(bus, "html.parser")
		if parsedBus.find_all(filter=bus) != None:
			busContents = parsedBus.find_all('span', class_="llegadaHome")
			for content in busContents:
				res.append(parseBusToObject(content.text))
	
		print(' ')
		
	return res

def getHaltestelle(name):
	haltestelleUrl = "https://www.emtvalencia.es/ciudadano/modules/mod_tiempo/sugiere_parada.php"
	body = {
		'parada': name
	}
	res = []
		
	request = requests.post(haltestelleUrl, data=body)
	request.encoding = 'UTF-8'
	haltestelleList = request.text
	parsedHaltestelleList = BeautifulSoup(haltestelleList, "html.parser")
	

	for haltestelle in parsedHaltestelleList.find_all('li'):
		res.append(parseHaltestelleToObject(haltestelle.text))
	
	return res

# Create a URL route in our application for "/"
@app.route('/haltestelle/<haltestelle>/', methods=['GET'])
def haltestelle(haltestelle):
	print(haltestelle)
	return json.dumps(getHaltestelle(haltestelle))
	
@app.route('/bus/<haltestelle>/<bus>/', methods=['GET'])
def bus(haltestelle,bus):
	return json.dumps(getNextBus(haltestelle,bus))

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)