import pandas as pd
import numpy as np
import requests
import json
import openpyxl

def get_standard_token():
    Header = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Basic am9oYW5jbGFuc2VydmVyOngvW0JNR1coNnckW0YlTmA='
    }
    url = 'https://prod.trackmania.core.nadeo.online/v2/authentication/token/basic?'
    r =requests.post(url, headers=Header)
    jsonResponse = json.loads(r.content)
    return jsonResponse['accessToken']

def get_live_token():
    Header = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Basic am9oYW5jbGFuc2VydmVyOngvW0JNR1coNnckW0YlTmA='
    }
    url = 'https://prod.trackmania.core.nadeo.online/v2/authentication/token/basic?'
    r =requests.post(url, json={'audience': 'NadeoLiveServices'}, headers=Header)
    jsonResponse = json.loads(r.content)
    return jsonResponse['accessToken']

def getMapString(mapInfo):
    string = ''
    for i in range(5,26):
        if i != 17:
            string += mapInfo['mapId'][i]
            if i != 25:
                string += '%2c'
    return string

def getPlayerString(playerList):
    string = ''
    for player in playerList.keys():
        string += player
        string += '%2c'
    string = string[:-3]
    return string

def get_times(playerList, mapInfo, token):
    Header = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'nadeo_v1 t={token}'
    }
    mapString = getMapString(mapInfo)
    playerString = getPlayerString(playerList)
    url = f'https://prod.trackmania.core.nadeo.online/mapRecords/?accountIdList={playerString}&mapIdList={mapString}'
    r = requests.get(url, headers=Header)
    jsonResponse = json.loads(r.content)
    return jsonResponse

def get_position_from_time(token, data):
    positions = []
    Header = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'nadeo_v1 t={token}'
    }
    for index, row in data.iterrows():
        mapUid = row['mapUid']
        score = row['time']
        url = f'https://live-services.trackmania.nadeo.live/api/token/leaderboard/group/Personal_Best/map/{mapUid}/surround/0/0?score={score}'
        r = requests.get(url, headers=Header)
        jsonResponse = json.loads(r.content)
        positions.append(jsonResponse['tops'][0]['top'][0]['position'] - 1)
    return positions

def replace_map_id_with_uid(mapIDs, mapInfo):
    uids = []
    mapNumber = []
    for mapID in mapIDs:
        for i in range(5,26):
            if i != 17:
                Id = mapInfo['mapId'][i]
                if mapID == Id:
                    uids.append(mapInfo['mapUid'][i])
                    mapNumber.append(mapInfo['mapNumber'][i])
    return uids, mapNumber

def convert_to_final_form(data: pd.DataFrame, outdic):
    for index, row in data.iterrows():
        playernumber = str(int((index / 20) + 1))
        if playernumber == '1':
            outdic['mapNumber'].append(row['mapNumber'])
        if index % 20 == 0:
            outdic[playernumber+'position'] = []
            outdic[playernumber+'time'] = []
        outdic[playernumber+'position'].append(row['position'])
        outdic[playernumber+'time'].append(row['time'])
    return outdic

def insert_names(data: pd.DataFrame, playerList):
    names = list(playerList.values())
    for i in range(0, len(names)):
        data.rename(columns={f"{str(i+1)}position":f"{names[i]} position"}, inplace=True)
        data.rename(columns={f"{str(i+1)}time":f"{names[i]} time"}, inplace=True)
    return data


def get_map_info():
    mapFrame = pd.read_csv('mapIDs.csv')
    mapFrame = mapFrame.set_axis(['mapNumber', 'mapId', 'mapUid'], axis=1)
    mapInfo = mapFrame.to_dict()
    return mapInfo

def get_times_and_uid( standardToken, mapInfo, playerList):
    times = get_times(playerList, mapInfo, standardToken)
    df = pd.DataFrame(times)
    df['mapUid'], df['mapNumber'] = replace_map_id_with_uid(df['mapId'], mapInfo)

    df['time'] = [d.get('time') for d in df['recordScore']]
    data = df[['accountId', 'mapId', 'mapUid', 'time', 'mapNumber']]
    return data

def get_positions(liveToken, data):
    outdic = {
    'mapNumber': []
    }
    data['position'] = get_position_from_time(liveToken, data)
    data = data.sort_values(['accountId', 'mapNumber'])
    finalData = data[['accountId','mapNumber', 'position', 'time']]
    finalData = finalData.reset_index()
    finalData = pd.DataFrame(convert_to_final_form(finalData, outdic))
    return finalData

def find_times_for_team(liveToken, standardToken, playerList):
    mapInfo = get_map_info()
    data = get_times_and_uid(standardToken, mapInfo, playerList)
    finalData = get_positions(liveToken, data)
    finalData = insert_names(finalData, playerList)
    return finalData

def convert_milliseconds(input):
    milliseconds = int((int(input)%1000))
    seconds = int((int(input)/1000)%60)
    minutes = int((int(input)/(1000*60))%60)

    seconds = '0'+str(seconds) if seconds < 10 else str(seconds)
    minutes = '0'+str(minutes) if minutes < 10 else str(minutes)

    returnstring = f'{minutes}:{seconds}.{milliseconds}' if int(minutes) > 0 else F'{seconds}.{milliseconds}'
    return returnstring

teamList = [
    {
        "team": "italy",
        "players" : {
            "3288d084-1aab-41af-99e6-f6e2367dcfc8" : "johanclanTM",
            "55a6453a-8fd8-47da-831b-d4c90ecc7506" : "DexteR.771"
        }
    },
    {
        "team": "denmark",
        "players" : {
            "794a286c-44d9-4276-83ce-431cba7bab74" : "Marius",
            "fb678553-f730-442a-a035-dfc50f4a5b7b" : "Mime"
        }
    }
]

liveToken = get_live_token()
standardToken = get_standard_token()

writer = pd.ExcelWriter('TeamTime.xlsx', engine = 'xlsxwriter')



for team in teamList:
    finalData = find_times_for_team(liveToken, standardToken, team['players'])
    finalData['time'].map()
    finalData.to_excel(writer, sheet_name=team['team'], index=False)
    #finalData.to_excel('TeamTime.xlsx', sheet_name=team['team'])
    print(finalData)
writer.save()
writer.close()