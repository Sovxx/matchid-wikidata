# matchid-wikidata
Import tool from deces.matchid.io list of french deceased persons to Wikidata

### Qu'est-ce que matchid-wikidata ?
matchid-wikidata est un outil d'importation qui facilite le renseignement des "Fichier des personnes décédées ID" <a href="https://www.wikidata.org/wiki/Property:P9058">P9058</a> du site https://deces.matchid.io sur Wikidata.

Il permet d'afficher :
* Sur fond blanc, les personnes françaises existantes sur Wikidata, sans ID P9058, et décédées pendant une période choisie.
* Sur fond orange (ou vert), les personnes sur https://deces.matchid.io susceptibles de correspondre.
Si vous voyez qu'il s'agit de la même personne, un bouton permet de préparer un import rapide dans wikidata.
<img src="doc/commande.png">
<a href="doc/html1.png"><img src="doc/html1_400px.png"></a> <a href="doc/html2.png"><img src="doc/html2_400px.png"></a>

---

### Utilisation
* Installez Python3 (gratuit).
* Installez les modules ``requests``, ``SPARQLWrapper`` et ``jinja2`` pour Python3 (gratuits).
* Téléchargez matchid-wikidata (bouton vert "Code" en haut à droite et "Download ZIP") et dézippez-le.
* Ouvrez un terminal (invite de commande) dans le dossier (Par exemple ``cd C:/xxx/xxx``).
* Lancez le programme avec la commande ``python3 matchid-wikidata.py`` (ou éventuellement ``py matchid-wikidata.py``).
* Renseignez les quelques questions posées.
* Attendez... (Comptez ~45 minutes pour 500 personnes).
* Ouvrez out.html :<br>
Les lignes blanches sont les personnes déjà listées sur Wikidata et qui n'ont pas encore d'id matchid.<br>
Les lignes oranges sont les personnes sur matchid qui peuvent potentiellement correspondre.
* Si la personne correspond (<b>Attention aux homonymes ! Veillez à avoir un esprit critique</b>), cliquez sur le bouton correspondant. Note : Aucune donnée n'est envoyée à Wikidata.
* Allez tout en bas du fichier out.html pour récupérer le texte qui sera à importer dans QuickStatements (outil d'import rapide pour Wikidata).
---

### Bug
Vous pouvez signaler les bugs dans l'onglet Issue ou me laisser un message sur ma page wikidata https://www.wikidata.org/wiki/User:Sovxx
