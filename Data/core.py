import requests, json, time, threading, time

class Core():

    def __init__(self):
        self.key = open("Data/key.txt", "r").read()
        if self.key == "":
            print("Please add your key in the key.txt file") 
            exit()

        while True:
            try:
                players_file = open("Data/players.txt", "r").read()
                for player in players_file.split(","):
                    if player == "":
                        pass
                    else:
                        self.fetchInfo(player)
                time.sleep(10)
            except FileNotFoundError: 
                print("Players file could not be found please run REBASE")
                time.sleep(2)

    def rename(self, old, new, type):
        if type == "info":
            try: self.info_json[f"{new}"] = self.info_json.pop(f"{old}")
            except KeyError: self.info_json[f"{new}"] = "Could not get info"
        elif type == "time":
            try: self.info_json[f"{new}"] = time.strftime("%d.%m %Y", time.localtime(self.info_json.pop(f"{old}")))
            except KeyError: self.info_json[f"{new}"] = "Could not get info"
            
        elif type == "ban":
            try: self.info_json[f"{new}"] = self.ban_json.pop(f"{old}")
            except KeyError: self.ban_json[f"{new}"] = "Could not get info"

    def fetchInfo(self, steamid):
        try:

            basic_request = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v1/?key={self.key}&steamids={steamid}')
            ban_request = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={self.key}&steamids={steamid}')

            basic_request.raise_for_status()
            ban_request.raise_for_status()


            self.info_json = json.loads(basic_request.text)["response"]["players"]["player"][0]
            self.ban_json = json.loads(ban_request.text)["players"][0]


            self.rename("personaname", "Persona Name: ", "info")
            self.rename("realname", "Real Name: ", "info")
            self.rename("steamid", "SteamID: ", "info")
            self.rename("profileurl", "URL: ", "info")
            self.rename("VACBanned", "VAC Banned: ", "ban")
            self.rename("CommunityBanned", "Community Banned: ", "ban")
            self.rename("NumberOfGameBans", "Number of Game Bans: ", "ban")
            self.rename("DaysSinceLastBan", "Days Since Last Ban: ", "ban")
            self.rename("gameextrainfo", "Currently in Game: ", "info")
            self.rename("loccountrycode", "Country Code: ", "info")
            self.rename("personastate", "Account Status: ", "info")
            self.rename("communityvisibilitystate", "Profile Visibility: ", "info")
            self.rename("profilestate", "Configured Profile: ", "info")
            self.rename("commentpermission", "Comment Permissions: ", "info")
            self.rename("primaryclanid", "Primary Clan ID: ", "info")
            self.rename("timecreated", "Account Age: ", "time")
            self.rename("lastlogoff", "Last Logoff: ", "time")

            filename = self.info_json['Persona Name: '].replace(".", "_").replace(" ", "_")
            
            with open(fr"Data/Info/{filename}.json", 'w') as outfile:
                json.dump(self.info_json, outfile)
        except requests.exceptions.ConnectionError: print("steam api did not respond, skipping..")
        except IndexError: print("Failed to get player info..")

core_thread = threading.Thread(target=Core)
core_thread.start()