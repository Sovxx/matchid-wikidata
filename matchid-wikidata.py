#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip install sparqlwrapper
# pip install Jinja2
# https://rdflib.github.io/sparqlwrapper/

import requests
from pprint import pprint #nécessaire pour pprint (affichage des données JSON sur plusieurs lignes)

from datetime import date

import sys
sys.path
sys.executable

from SPARQLWrapper import SPARQLWrapper, JSON

# https://www.youtube.com/watch?v=9v6kDoUjIs4
# pip3 install jinja2
import jinja2 #ne pas mettre de majuscule (Jinja2) !
from jinja2 import Environment, FileSystemLoader
fileLoader = FileSystemLoader("templates")
env = Environment(loader=fileLoader)

score_target = 0.1

try:
    date_debut = sys.argv[1]
    print(date_debut)
except:
    date_debut = input("Date (incluse) de début ? (ex: 1970-01-01) : ")
    if (len(date_debut) != 10): raise SystemExit("Erreur : Renseigner une date de début de recherche")

try:
    date_fin = sys.argv[2]
    print(date_fin)
except:
    date_fin = input("Date (incluse) de début ? (ex: 1970-01-01) : ")
    if (len(date_fin) != 10): raise SystemExit("Erreur : Renseigner une date de début de recherche")

try:
    apikey = sys.argv[3]
    print(apikey)
except:
    try:
        with open("apikey.txt", 'r') as fichier:
            apikey = fichier.read()
            apikey = apikey.strip() # pour retirer les \n de retour ligne
            print("API Key trouvée dans apikey.txt:", apikey)
    except:
        print("Pas de fichier apikey.txt contenant la clé API (vous pouvez en obtenir une sur le site deces.matchid.io) trouvé")
        apikey = input("Renseignez manuellement l'API Key si vous en avez une (laisser vide sinon, mais le nombre de demandes va être limité) : ")

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?human ?humanLabel ?nom_de_familleLabel ?prenomLabel ?prenoms_num ?prenomsLabel ?nom_de_naissance ?pseudo ?date_de_naissance ?precision_de_naissance ?lieu_de_naissanceLabel ?date_de_mort ?precision_de_mort ?lieu_de_mortLabel WHERE {
  ?human wdt:P31 wd:Q5.
  MINUS { ?human wdt:P9058 _:b8. }
  ?human wdt:P27 wd:Q142;
    (p:P570/psv:P570) _:b9.
  _:b9 wikibase:timePrecision ?precision_de_mort;
    wikibase:timeValue ?date_de_mort.
  BIND(CONCAT(STR(YEAR(?date_de_mort)), "-", STR(MONTH(?date_de_mort))) AS ?yearmonth)
  FILTER(?date_de_mort >= """ + "\"" + date_debut + """T00:00:00"^^xsd:dateTime)
  FILTER(?date_de_mort < """ + "\"" + date_fin + """T00:00:00"^^xsd:dateTime)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],fr". }

  OPTIONAL { ?human wdt:P734 ?nom_de_famille. }
  OPTIONAL { ?human wdt:P735 ?prenom. }
  OPTIONAL { ?human p:P735 [pq:P1545 ?prenoms_num;
                            ps:P735 ?prenoms;
                           ]. }
  OPTIONAL { ?human wdt:P569 ?date_de_naissance.
             ?human p:P569/psv:P569 ?date_de_naissance_node.
             ?date_de_naissance_node wikibase:timePrecision ?precision_de_naissance.
           }
  OPTIONAL { ?human wdt:P19 ?lieu_de_naissance. }
  OPTIONAL { ?human wdt:P20 ?lieu_de_mort. }
  OPTIONAL { ?human wdt:P1477 ?nom_de_naissance. }
  OPTIONAL { ?human wdt:P742 ?pseudo. }
}
LIMIT 10000"""

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

print("----------------------------------------")
print("RECUPERATION DES DONNEES SUR WIKIDATA...")
print("----------------------------------------")
results = get_results(endpoint_url, query)

for result in results["results"]["bindings"]:
    print(result)

pprint(results)
print("---------")
#pprint(results["results"]["bindings"][0])
#pprint(results["results"]["bindings"][1])
#pprint(results["results"]["bindings"][2])
print("---------")

wikidata = []
item_wikidata = ["human",\
"humanLabel",\
"nom_de_familleLabel",\
"prenomLabel",\
"prenoms_num",\
"prenomsLabel",\
"nom_de_naissance",\
"pseudo",\
"date_de_naissance",\
"lieu_de_naissanceLabel",\
"date_de_mort",\
"lieu_de_mortLabel"]

for i in range(len(results["results"]["bindings"])):
    print("----- i: ", i," -----")
    wikidata.append([]) #pour passer à 2 dimensions à la position i
    for j in range(len(item_wikidata)):
        try:
            wikidata[i].append(results["results"]["bindings"][i][item_wikidata[j]]["value"])

            if item_wikidata[j] == "human":
                wikidata[i][j] = wikidata[i][j][31:] #pour enlever "http://www.wikidata.org/entity/" de "http://www.wikidata.org/entity/Q55740039"

            if item_wikidata[j] == "date_de_naissance":
                wikidata[i][j] = wikidata[i][j][:10] #pour garder "2010-02-02" dans "2010-02-02T00:00:00Z"
                d = date.fromisoformat(wikidata[i][j])
                wikidata[i][j] = d.strftime("%d/%m/%Y") #pour passer à JJ/MM/AAAA
                if results["results"]["bindings"][i]["precision_de_naissance"]["value"] in {"7","8"}: # précision = siècle ou décennie
                    wikidata[i][j] = ""
                if results["results"]["bindings"][i]["precision_de_naissance"]["value"] == "9" :
                    wikidata[i][j] = d.strftime("%Y") #pour passer à AAAA

            if item_wikidata[j] == "date_de_mort":
                wikidata[i][j] = wikidata[i][j][:10] #pour garder "2010-02-02" dans "2010-02-02T00:00:00Z"
                d = date.fromisoformat(wikidata[i][j])
                wikidata[i][j] = d.strftime("%d/%m/%Y") #pour passer à JJ/MM/AAAA
                if results["results"]["bindings"][i]["precision_de_mort"]["value"] in {"7","8"}: # précision = siècle ou décennie
                    wikidata[i][j] = ""
                if results["results"]["bindings"][i]["precision_de_mort"]["value"] == "9" :
                    wikidata[i][j] = d.strftime("%Y") #pour passer à AAAA

        except KeyError:
            wikidata[i].append("")
        print("i: ", i, "  j:", j, "  ",item_wikidata[j],(30-len(item_wikidata[j])-len(str(i))-len(str(j)))*" "," : ", wikidata[i][j])

print("-------------------------------")
print("DONNEES RECUPEREES SUR WIKIDATA")
print("-------------------------------")

print("---------------------------------------")
print("RECUPERATION DES DONNEES SUR MATCHID...")
print("---------------------------------------")
# https://matchid.io/link-api
# Merci à MohamedRahmouni https://replit.com/@MohamedRahmouni/API-deces-linkage-1
import time

url = "https://deces.matchid.io/deces/api/v1/search"
gap = 1.2 #nombre de secondes entre 2 requetes (éviter de mettre moins d'1)
nb_methodes = 4 #sert juste à l'ETA

human_precedent = ""
res_saved = []

k = 0
for i in range(len(wikidata)):
    print(f"----- i: {i}  /  {len(wikidata)} ({round(i/len(wikidata)*100,1)}%) (ETA: {round(gap*nb_methodes*(len(wikidata)-i)/60*1.25,1)} min)  -----  {wikidata[i][0]}   {wikidata[i][1]}")
    pprint(wikidata[i])
    if 1:# wikidata[i][0] != human_precedent: #pour trouver chaque nouveau human (Qxxxxxxx)
        res_saved.append([])

        params_matrice = [\
        #Nom DOD
        {
            'q': str(wikidata[i][1]+" "+wikidata[i][10]),
            'size': 20 #sinon, par défaut, seuls 20 résultats sont affichés, alors que le programme va essayer de tous les afficher !
        },
        #Nom DOB LOB DOD LOD
        {
            'lastName': wikidata[i][1],
            'birthDate': wikidata[i][8],
            'birthCity': wikidata[i][9],
            'deathDate': wikidata[i][10],
            'deathCity': wikidata[i][11],
            'size': 20 #sinon, par défaut, seuls 20 résultats sont affichés, alors que le programme va essayer de tous les afficher !
        },
        #NomFamille Prenom DOB LOB DOD LOD
        {
            'lastName': wikidata[i][2],
            'firstName': wikidata[i][3],
            'birthDate': wikidata[i][8],
            'birthCity': wikidata[i][9],
            'deathDate': wikidata[i][10],
            'deathCity': wikidata[i][11],
            'size': 20 #sinon, par défaut, seuls 20 résultats sont affichés, alors que le programme va essayer de tous les afficher !
        },
        #NomFamille Prenoms DOB LOB DOD LOD
        #NomNaissance DOB LOB DOD LOD
        #Pseudo DOB LOB DOD LOD
        #Nom DOD
        #NomFamille Prenom DOD
        #NomFamille Prenoms DOD
        #NomNaissance DOD
        #Pseudo DOD
        #Nom YOD
        #NomFamille Prenom YOD
        {
            'lastName': wikidata[i][2],
            'firstName': wikidata[i][3],
            'deathDate': wikidata[i][10][-4:],
            'size': 20 #sinon, par défaut, seuls 20 résultats sont affichés, alors que le programme va essayer de tous les afficher !
        #NomFamille Prenoms YOD
        #NomNaissance YOD
        #Pseudo YOD   ==> renvoie trop de résultats
        #{
        #    'firstName': wikidata[i][7],
        #    'deathDate': wikidata[i][10][-4:],
        #    'size': 20 #sinon, par défaut, seuls 20 résultats sont affichés, alors que le programme va essayer de tous les afficher !
        }]
        for m in range(len(params_matrice)): #balaye chaque ligne de la matrice
            print("i: ", i,"  k: ", k, "  m:", m)
            pprint(params_matrice[m])
            res_saved[k].append([])
            time.sleep(gap) #pour ne pas dépasser la limite d'une requête par seconde
            if apikey:
                r = requests.get(url, params=params_matrice[m], headers={'Authorization': 'Bearer '+apikey})
            else:
                r = requests.get(url, params=params_matrice[m])
            res = r.json()
            #pprint(res)
            try:
                print("PROBLEME DE REPONSE =========================================== Message retourné par deces.matchid.io :", res['message'])
            except:
                pass
            try:
                print("PROBLEME DE REPONSE =========================================== Message retourné par deces.matchid.io :", res['msg'])
            except:
                pass
            scored_size = 0
            try:
                print("i: ", i,"  k: ", k, "  m:", m,"  response size :", res['response']['total'])
            except:
                print("PROBLEME DE REPONSE ===========================================")
                pprint(res)
            for o in range(min(res['response']['total'],20)):
                #print ("o:", o)
                #print ("o:", o, "   score : ", res['response']['persons'][o]['score'])
                if res['response']['persons'][o]['score'] is not None:
                    if res['response']['persons'][o]['score'] > score_target:
                        #print("o:", o," :")
                        #pprint(res['response']['persons'][o])
                        res_saved[k][m].append(res['response']['persons'][o])
                        scored_size = scored_size + 1
                    #else:
                        #res_saved[k][m].append("score trop bas")
            print("i: ", i,"  k: ", k, "  m:", m, "  scored size :", scored_size)
        k = k + 1
    else:
        print("Qxxxxxx identique au i précédent. Passage au suivant.")
    human_precedent = wikidata[i][0]
print("------------------------------")
print("DONNEES RECUPEREES SUR MATCHID")
print("------------------------------")
print("res_saved:")
pprint(res_saved)
#print("res_saved[0][0][0]:")
#print(res_saved[0][0][0])
#pprint(res_saved[3])
#print("res_saved[2]:")
#pprint(res_saved[2])
#print("res_saved[2][1][0]:")
#pprint(res_saved[2][1][0])
#print("res_saved[2][1][0]['name']")
#print(res_saved[2][1][0]['name'])
print('----------')

print("---------------------------------")
print("MISE EN FORME SUR LA PAGE HTML...")
print("---------------------------------")
rendered = env.get_template("template.html").render(\
date_debut = date_debut, date_fin = date_fin,\
wikidata = wikidata,len_wikidata = len(wikidata),\
item_wikidata = item_wikidata, len_item_wikidata = len(item_wikidata),\
res_saved= res_saved)
with open("out.html", 'w') as file:
    file.write(rendered)
print("-----------------------")
print("PAGE HTML MISE EN FORME")
print("    OUVREZ out.html    ")
print("-----------------------")
