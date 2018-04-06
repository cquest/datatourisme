#!/usr/bin/env python3
import sys
import json
import csv
import re


def ldget(obj, path, default=None):
    "Descente dans le graphe de données"
    if obj is not None and path[0] in obj:
        if len(path) == 1:
            return obj[path[0]]
        else:
            return ldget(obj[path[0]], path[1:], default=default)
    else:
        return default


# fichier CSV de sortie
# avec python3 ajout de l'encoding et newline='' pour l'ouverture du fichier et 
# éviter des lignes vides dans le csv
# with open(re.sub(r'json.*', 'csv', sys.argv[1]), 'w', newline='', encoding="utf-8") as csvfile:
with open(re.sub(r'json.*', 'csv', sys.argv[1]), 'w') as csvfile:
    fields = ['id', 'label', 'type', 'theme', 'startdate', 'enddate',
              'street', 'postalcode', 'city', 'insee',
              'latitude', 'longitude', 'email', 'web', 'tel',
              'lastupdate', 'comment']
    csv_out = csv.writer(csvfile)
    csv_out.writerow(fields)

    # fichier json-ld en entrée
	# avec python3 ajout de l'encoding 
    # with open(sys.argv[1], 'r', encoding="utf-8") as json_file:
    with open(sys.argv[1], 'r') as json_file:
        data = json.load(json_file)
        for e in data['@graph']:
            # extraction des éléments du graphe à sortir en CSV
            uri = ldget(e, ['@id'])
            label = ldget(e, ['rdfs:label'])
            comment = ldget(e, ['rdfs:comment'])
            startdate = ldget(e, [':takesPlaceAt', ':startDate', '@value'])
            enddate = ldget(e, [':takesPlaceAt', ':endDate', '@value'])
            geo = ldget(e, [':isLocatedAt', 'schema:geo'])
            lat = ldget(geo, ['schema:latitude', '@value'])
            lon = ldget(geo, ['schema:longitude', '@value'])
            addr = ldget(e, [':isLocatedAt', 'schema:address'])
            street = ldget(addr, ['schema:streetAddress'])
            cp = ldget(addr, ['schema:postalCode'], '')
            city = ldget(addr, [':hasAddressCity', 'rdfs:label'])
            if city:
                city = city[0]['@value']
            insee = ldget(addr, [':hasAddressCity', ':insee'])
            last_update = ldget(addr, [':lastUpdate'])
            event_type = '/'.join(ldget(e, ['@type']))
            email = ldget(e, [':hasContact', 'schema:email'])
            web = ldget(e, [':hasContact', 'foaf:homepage'])
            tel = ldget(e, [':hasContact', 'schema:telephone'])

            themes = ldget(e, [':hasTheme', 'rdfs:label'], None)
            event_theme = ''
            if themes:
                for t in themes:
                    if t['@language'] == 'fr':
                        event_theme = event_theme + t['@value'] + ', '
                event_theme = event_theme[:-2]

            # écriture dans le fichier CSV
            csv_out.writerow([uri, label, event_type, event_theme, startdate,
                              enddate, street, cp, city, insee, lat, lon,
                              email, web, tel,
                              last_update, comment])
