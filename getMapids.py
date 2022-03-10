import pandas as pd
import numpy as np
import requests
import json

url = 'https://trackmania.io/api/officialcampaign/18729'
userAgentHeader = {
    'User-Agent': 'TSCCTeamPositionFinder/0.1',
    'Authorization': 'Trackmania.io F32_D4On2ui0b0dgw2ydL6hTID11p_eie83wfmptC07DtUMjmpgxAlWczLOaK5Bc'
}
#r =requests.get(url, headers=userAgentHeader)
jsonResponse = json.loads(r.content)

mapids = {
    'ids': [],
    'uids': []
}
mapids['ids'].append('cd7facc2-3cee-45cf-b7c6-816da8e99db4')
mapids['uids'].append('')
for track in jsonResponse['playlist']:
    print(track['mapId'] + track['mapUid'])
    mapids['ids'].append(track['mapId'])
    mapids['uids'].append(track['mapUid'])
mapids = pd.DataFrame(mapids)
mapids.to_csv('mapIDs.csv')
