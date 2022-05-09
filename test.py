import pandas as pd
import numpy as np
import requests
import json
import openpyxl
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def main():
    f = open('PlayoffTeams.json')
    teams = json.load(f)

    teamList = [
            {
                "team": "Atlas Lions",
                "players" : {
                    "391f1aeb-744f-4c8c-8ce3-dcd53cfbf883" : "JajaTM",
                    "dc203ffc-bab7-4971-bfb3-dec83db1fa4e" : "Br0wski7",
                    "f16aba06-1952-45ab-866c-775c0f45d93a" : "MarsoTM",
                    "3a88d4bc-a2a5-4b38-9fd6-f05c02ef159a" : "BENOXy",
                    "9e51ee71-ac8e-498d-91fe-7534c5acf5f4" : "le_usf"
                }
            },
            {
            "team": "Austria's Bench Team YEP",
            "players" : {
                "711036bf-d90b-4fa4-9be5-964eb3912256" : "Mariina.",
                "b52cc9c4-4e4f-48ce-ace6-b4a6ced9bfc3" : "ParZival_TM",
                "5cafc8ea-9a29-4687-9101-71397643190b" : "DMR-GameBros",
                "c465dbfc-d145-4944-bc06-f61106323040" : "Domi_TM",
                "08e60593-f088-4d50-9a98-6945643fea50" : "Dave_it_Google"
                }
            }
        ]
    liveToken = get_live_token()
    standardToken = get_standard_token()

    writer = pd.ExcelWriter('TeamTime.xlsx', engine = 'xlsxwriter')

    produce_excel_file(liveToken, standardToken, writer, teams)

    writer.save()


def get_standard_token():
    Header = {
        'User-Agent': '<TSCC Team Position Finder> / <1.0> <Tool used to find times and positions for all players in the TSCC tournament If this usage is an issue my discord is: JohanClan#1234>',
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
        'User-Agent': '<TSCC Team Position Finder> / <1.0> <Tool used to find times and positions for all players in the TSCC tournament If this usage is an issue my discord is: JohanClan#1234>',
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
        'User-Agent': '<TSCC Team Position Finder> / <1.0> <Tool used to find times and positions for all players in the TSCC tournament If this usage is an issue my discord is: JohanClan#1234>',
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
        'User-Agent': '<TSCC Team Position Finder> / <1.0> <Tool used to find times and positions for all players in the TSCC tournament If this usage is an issue my discord is: JohanClan#1234>',
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

def convert_to_final_form(data: pd.DataFrame, outdic, playerList):
    for index, row in data.iterrows():
        playernumber = str(int((index / 20) + 1))
        if playernumber == '1':
            outdic['mapNumber'].append(row['mapNumber'])
        name = playerList[row['accountId']]
        if index % 20 == 0:
            outdic[f'{name} position'] = []
            outdic[f'{name} time'] = []
        outdic[f'{name} position'].append(row['position'])
        outdic[f'{name} time'].append(row['time'])
    return outdic

def get_map_info():
    mapFrame = pd.read_csv('mapIDs.csv')
    mapFrame = mapFrame.set_axis(['mapNumber', 'mapId', 'mapUid'], axis=1)
    mapInfo = mapFrame.to_dict()
    return mapInfo

def convert_milliseconds(input):
    milliseconds = int((int(input)%1000))
    seconds = int((int(input)/1000)%60)
    minutes = int((int(input)/(1000*60))%60)

    milliseconds = '00' + str(milliseconds) if milliseconds < 10 else '0' + str(milliseconds) if milliseconds < 100 else str(milliseconds)
    seconds = '0'+str(seconds) if seconds < 10 else str(seconds)
    minutes = '0'+str(minutes) if minutes < 10 else str(minutes)

    returnstring = f'{minutes}:{seconds}.{milliseconds}' if int(minutes) > 0 else F'{seconds}.{milliseconds}'
    return returnstring

def convert_to_readable_time(times):
    array = []
    for time in times:
        array.append(convert_milliseconds(time))
    return array

def check_and_fill_empty_maps(playerTimes: pd.DataFrame, playerList):
    for accountID in playerList.keys():
        accountIDTimes = playerTimes[playerTimes['accountId'] == accountID]
        if accountIDTimes.shape[0] < 20:
            for i in range(5,26):
                if i not in accountIDTimes['mapNumber'].tolist():
                    if i != 17:
                        playerTimes = playerTimes.append({
                            'accountId': accountID,
                            'mapNumber': i,
                            'position': 999999,
                            'time': 660000
                        }, ignore_index=True)
    return playerTimes


def get_times_and_uid(standardToken, mapInfo, playerList):
    times = get_times(playerList, mapInfo, standardToken)
    df = pd.DataFrame(times)
    df['mapUid'], df['mapNumber'] = replace_map_id_with_uid(df['mapId'], mapInfo)
    df['time'] = [d.get('time') for d in df['recordScore']]
    data = df[['accountId', 'mapId', 'mapUid', 'time', 'mapNumber']]
    return data

def get_positions(liveToken, data, playerList):
    outdic = {
    'mapNumber': []
    }
    data['position'] = get_position_from_time(liveToken, data)
    data = data[['accountId','mapNumber', 'position', 'time']]
    data = check_and_fill_empty_maps(data, playerList)
    data = data.sort_values(['accountId', 'mapNumber'])
    data = data.reset_index()
    data['time'] = convert_to_readable_time(data['time'])
    data = pd.DataFrame(convert_to_final_form(data, outdic, playerList))
    return data

def find_times_for_team(liveToken, standardToken, playerList):
    mapInfo = get_map_info()
    data = get_times_and_uid(standardToken, mapInfo, playerList)
    finalData = get_positions(liveToken, data, playerList)
    return finalData

def produce_excel_file(liveToken, standardToken, writer, teamList):
    for team in teamList:
        TopThreeAverages = []
        finalData = find_times_for_team(liveToken, standardToken, team['players'])
        TopThreeAverages = get_top_three_averages(finalData)
        finalData['Top Three Average'] = TopThreeAverages
        finalData.to_excel(writer, sheet_name=team['team'], index=False)
        print(team['team'])
        print(finalData)
        adjust_column_width(writer, team['team'], finalData)
    return finalData

def adjust_column_width(writer, teamName, finalData):
    worksheet = writer.sheets[teamName]  # pull worksheet object
    for idx, col in enumerate(finalData):  # loop through all columns
        series = finalData[col]
        max_len = max((
        series.astype(str).map(len).max(),  # len of largest item
        len(str(series.name))  # len of column name/header
        )) + 3  # adding a little extra space
        worksheet.set_column(idx, idx, max_len)

def Average(lst):
    return sum(lst) / len(lst)

def get_top_three_averages(data):
    averages = []
    for i in range(5,26):
        if i != 17:
            positionsCol = data[data['mapNumber'] == i].filter(regex='position')
            positions = positionsCol.values.flatten().tolist()
            positions.sort()
            top_three = positions[:3]
            mapAverages = Average(top_three)
            averages.append(int(mapAverages))
    return averages
            
if __name__ == "__main__":
    main()