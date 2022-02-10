from multiprocessing.sharedctypes import Value
import requests, json, time, os
from steam.steamid import SteamID

class VACTracker():

    def __init__(self):
        self.refresh()

    def refresh(self):
        self.banned = []
        self.players = []
        self.players_readable = open("players.txt", "r+")
        self.players_writeable = open("players.txt", "a+")
        self.listify()

    def listify(self):
        try:
            players = self.players_readable.read().split(",")
            for str in players:
                self.players.append(int(str))
        except: pass
    def makeRequest(self):
        url = f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key=FCC3CCD9F0EF902B6D12A08F7A697E0E&steamids={str(self.players).split("[")[1].split("]")[0]}'
        request = requests.get(url) 
        return(request)

    def checker(self):
        while True:

            request = self.makeRequest()

            self.request = request

            filtered_list = []
            for id in json.loads(request.text)["players"]:
                filtered_list.append(id["SteamId"])

            self.filtered_list = filtered_list

            banned = []

            for player in range(0, len(filtered_list)):
                profile = requests.get(f'https://steamcommunity.com/profiles/{filtered_list[player]}')
                persona_name = profile.text.split("actual_persona_name\">")[1].split("<")[0]

                ban_vac = json.loads(request.text)['players'][player]['VACBanned']
                days = json.loads(request.text)['players'][player]['DaysSinceLastBan']
                count_vac = json.loads(request.text)['players'][player]['NumberOfVACBans']

                #if json.loads(request.text)['players'][player]['SteamId'] == str(filtered_list[player]): print(f"Player {persona_name}: banned: {ban_vac}(VAC, Days since last: {days}, Count: {count_vac}) steamid: {json.loads(request.text)['players'][player]['SteamId']}, url: {SteamID(self.players[player]).community_url}")
                #else: print("mismatch steam id")

                if ban_vac == True:
                    try:
                        self.banned.append(f"Player {persona_name}, Days since last: {days}, Count: {count_vac} steamid: {json.loads(request.text)['players'][player]['SteamId']}, url: {SteamID(self.players[player]).community_url}")
                    except IndexError: pass
            time.sleep(5)

    def console(self):
        os.system('clear')
        print("---VACTRACKER SHELL---")
        while True:
            command = input()
            command = command.split(" ")
            if command[0] == "ADD":
                try:
                    int(command[1])
                    self.players_writeable.write(f"{command[1]},")
                    print("User sucessfully added, please be patient, it might take a while to refresh the list. (SteamID)")
                    self.refresh()
                except ValueError:
                    steamid = SteamID.from_url(f'https://steamcommunity.com/id/{command[1]}')
                    self.players_writeable.write(f"{steamid},")
                    print("User sucessfully added, please be patient, it might take a while to refresh the list. (Username)")
                    self.refresh()
                except: pass

            if command[0] == "REMOVE":
                try:
                    int(command[1])
                    try: 
                        index = self.players.index(f"{command[1]}")
                        self.players.pop(index)
                        players_rewritable = open("players.txt", "w")
                        players_rewritable.write(str(self.players).split("[")[1].split("]")[0])
                        print("User sucessfully removed, please be patient, it might take a while to refresh the list. (SteamID)")
                        self.refresh()
                    except: print("No such user")
                except ValueError:
                    steamid = SteamID.from_url(f'https://steamcommunity.com/id/{command[1]}')
                    try:
                        index = self.players.index(steamid)
                        self.players.pop(index)
                        players_rewritable = open("players.txt", "w")
                        players_rewritable.write(str(self.players).split("[")[1].split("]")[0])
                        print("User sucessfully removed, please be patient, it might take a while to refresh the list. (Username)")
                        self.refresh()
                    except: print("No such user")
                except: pass

            if command[0] == "ALL":
                os.system('clear')
                print("---VACTRACKER SHELL---")
                temp_list = []
                print("Please wait getting usernames...")
                for player in range(0, len(self.players)):
                    profile = requests.get(f'https://steamcommunity.com/profiles/{self.filtered_list[player]}')
                    persona_name = profile.text.split("actual_persona_name\">")[1].split("<")[0]
                    ban_vac = json.loads(self.request.text)['players'][player]['VACBanned']
                    temp_list.append(f"{persona_name}: VAC-{ban_vac}")
                os.system('clear')
                print("---VACTRACKER SHELL---")
                for name in temp_list:
                    print(name)

            if command[0] == "BANNED":
                os.system('clear')
                print("---VACTRACKER SHELL---")
                for player in self.banned:
                    print(player)
            



VACTracker = VACTracker()
