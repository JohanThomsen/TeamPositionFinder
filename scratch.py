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

def insert_names(playerList):
    names = list(playerList.values())
    for i in range(0, len(names)):
        print(names[i])


insert_names(teamList[0]['players'])

#for team in teamList:
#    insert_names(team['players'])