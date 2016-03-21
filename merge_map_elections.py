import json, pandas
elections = pandas.read_csv('election_results.csv')
# elections.columns # Shows all columns of the election results file
map_file = open('map.json', 'rb')
map = json.load(map_file)
# map['objects']['gem']['geometries'][0]['properties'] # A single municipality in the map data
parties = {'50PLUS': True, 'Christen Democratisch Appèl (CDA)': True, 'ChristenUnie': False, 'Democraten 66 (D66)': True, 'GROENLINKS': True, 'PVV (Partij voor de Vrijheid)': False, 'Partij van de Arbeid (P.v.d.A.)': True, 'Partij voor de Dieren': False, 'SP (Socialistische Partij)': False, 'Staatkundig Gereformeerde Partij (SGP)': False, 'VVD': True}
for gem in map['objects']['gem']['geometries']:
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
    json.dump(map, outfile)
