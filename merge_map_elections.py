#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, json, pandas

def main(argv):
    elections = pandas.read_csv('election_results.csv')
    map_file = open('map.json', 'rb')
    map_data = json.load(map_file)
    parties = {
        '50PLUS': True,
        'Christen Democratisch Appèl (CDA)': True,
        'ChristenUnie': False,
        'Democraten 66 (D66)': True,
        'GROENLINKS': True,
        'PVV (Partij voor de Vrijheid)': False,
        'Partij van de Arbeid (P.v.d.A.)': True,
        'Partij voor de Dieren': False,
        'SP (Socialistische Partij)': False,
        'Staatkundig Gereformeerde Partij (SGP)': False,
        'VVD': True
    }
    for gem in map_data['objects']['gem']['geometries']:
        if not gem['properties']['GM_NAAM']: continue
        print 'parsing district: '+gem['properties']['GM_NAAM']
        c = float(gem['properties']['GM_CODE'].lstrip('GM'))
        for election in elections.values:
            if not election[1] == c: continue
            print 'found matching district: '+election[2]+'\n'
            for i, col in enumerate(elections.columns):
                gem['properties'][col] = election[i]
            count = 0
            for party in parties:
                votes = gem['properties'][party]
                count = count + votes if parties[party] else count - votes
            gem['properties']['in_favor'] = True if count >= 0 else False
    with open('_map.json', 'w') as outfile:
        json.dump(map_data, outfile)

if __name__ == "__main__":
    main(sys.argv[1:])
