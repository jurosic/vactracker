from multiprocessing.sharedctypes import Value
import requests, json, time, os
from steam.steamid import SteamID

class VACTracker():

    def __init__(self):
        self.refresh()

    def refresh(self):

        self.player_txt_path = "Data/Files/players.txt"
        self.pleyer_info_path = "Data/Files/info.json"
        self.banned = []
        self.players = []
        self.players_readable = open(self.player_txt_path, "r+")
        self.players_writeable = open(self.player_txt_path, "a+")
        self.info_writable = open(self.pleyer_info_path, "a+")
        self.detailed = None
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
            self.refresh()

            request = self.makeRequest()

            self.request = request

            filtered_list = []
            for id in json.loads(request.text)["players"]:
                filtered_list.append(id["SteamId"])

            self.filtered_list = filtered_list

            self.banned = []

            for player in range(0, len(filtered_list)):
                steamid = json.loads(request.text)['players'][player]['SteamId']
                steamid_index = filtered_list.index(steamid)
                player = filtered_list[steamid_index]

                url = SteamID(player).community_url
                profile = requests.get(url).text
                try: persona_name = profile.split("actual_persona_name\">")[1].split("<")[0]
                except ValueError: persona_name = "(Failed to get persona name)"

                ban_vac = json.loads(request.text)['players'][steamid_index]['VACBanned']
                days = json.loads(request.text)['players'][steamid_index]['DaysSinceLastBan']
                count_vac = json.loads(request.text)['players'][steamid_index]['NumberOfVACBans']

                if self.detailed == True:
                    if json.loads(request.text)['players'][steamid_index]['SteamId'] == player: print(f"Player {persona_name}: banned: {ban_vac}(VAC, Days since last: {days}, Count: {count_vac}) steamid: {steamid}, url: {url}")
                    else: print("mismatch steam id")

                if ban_vac == True:
                    try:
                        self.banned.append(f"Player {persona_name}, Days since last: {days}, Count: {count_vac} steamid: {steamid}, url: {url}")
                    except IndexError: pass
            self.detailed = False
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
                    print("User sucessfully added, please be patient, it might take a while to refresh the list. Sleeping three seconds to prevent crashes (SteamID)")
                    self.refresh()
                    for i in range(0, 3):
                        time.sleep(1)
                except ValueError:
                    steamid = SteamID.from_url(f'https://steamcommunity.com/id/{command[1]}')
                    self.players_writeable.write(f"{steamid},")
                    print("User sucessfully added, please be patient, it might take a while to refresh the list. Sleeping three seconds to prevent crashes (Username)")
                    self.refresh()
                    for i in range(0, 3):
                        time.sleep(1)

            if command[0] == "REMOVE":
                os.system('clear')
                print("---VACTRACKER SHELL---")
                if command[1] == "ALL":
                    players_rewritable = open("players.txt", "w")
                    players_rewritable.close()
                    self.refresh()
                else:
                    try:
                        int(command[1])
                        try: 
                            index = self.players.index(f"{command[1]}")
                            self.players.pop(index)
                            print(self.players)
                            players_rewritable = open(self.player_txt_path, "w")
                            players_rewritable.write(f'{str(self.players).split("[")[1].split("]")[0]},')
                            players_rewritable.close()
                            print("User sucessfully removed, please be patient, it might take a while to refresh the list. Sleeping three seconds to prevent crashes (SteamID)")
                            self.refresh()
                            for i in range(0, 3):
                                time.sleep(1)
                        except: print("No such user")
                    except ValueError:
                        steamid = SteamID.from_url(f'https://steamcommunity.com/id/{command[1]}')
                        try:
                            index = self.players.index(steamid)
                            self.players.pop(index)
                            players_rewritable = open(self.player_txt_path, "w")
                            players_rewritable.write(f'{str(self.players).split("[")[1].split("]")[0]},')
                            players_rewritable.close()
                            print("User sucessfully removed, please be patient, it might take a while to refresh the list. Sleeping three seconds to prevent crashes (Username)")
                            self.refresh()
                            for i in range(0, 3):
                                time.sleep(1)
                        except: print("No such user")
                    except: pass
                    
            if command[0] == "ALL":
                os.system('clear')
                print("---VACTRACKER SHELL---")
                temp_list = []
                print("Please wait getting usernames...")
                for player in range(0, len(self.filtered_list)):
                    profile = requests.get(f'https://steamcommunity.com/profiles/{self.filtered_list[player]}')
                    persona_name = profile.text.split("actual_persona_name\">")[1].split("<")[0]
                    ban_vac = json.loads(self.request.text)['players'][player]['VACBanned']
                    ban_com = json.loads(self.request.text)['players'][player]['CommunityBanned']
                    temp_list.append(f"{persona_name}: VAC-{ban_vac}, COM-{ban_com}")

                os.system('clear')
                print("---VACTRACKER SHELL---")
                for name in temp_list:
                    print(name)

            if command[0] == "BANNED":
                os.system('clear')
                print("---VACTRACKER SHELL---")
                for player in self.banned:
                    print(player)
            
            if command[0] == "DETAILED":
                os.system('clear')
                print("---VACTRACKER SHELL---")
                print("Please wait getting detailed info..")
                self.detailed = True            

VACTracker = VACTracker()
