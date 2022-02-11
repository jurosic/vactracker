import requests, json, time, threading

class Core():

    def __init__(self):
        while True:
            players_file = open("Data/players.txt", "r").read()
            for player in players_file.split(","):
                self.fetchInfo(player)
            time.sleep(3)

    def rename(self, old, new):
        try: self.info_json[f"{new}"] = self.info_json.pop(f"{old}")
        except KeyError: self.info_json[f"{new}"] = "Could not get info"
        except AttributeError: pass

    def fetchInfo(self, steamid):

        basic_request = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v1/?key=FCC3CCD9F0EF902B6D12A08F7A697E0E&steamids={steamid}')

        self.info_json = json.loads(basic_request.text)["response"]["players"]["player"][0]

        self.rename("personaname", "Persona Name: ")
        self.rename("steamid", "SteamID: ")
        self.rename("profileurl", "URL: ")
        self.rename("loccountrycode", "Country Code: ")
        self.rename("personastate", "Account Status: ")
        self.rename("communityvisibilitystate", "Profile Visibility: ")
        self.rename("profilestate", "Configured Profile: ")
        self.rename("commentpermission", "Comment Permissions: ")
        self.rename("primaryclanid", "Primary Clan ID: ")
        self.rename("timecreated", "Account Age: ")
        self.rename("lastlogoff", "Last Logoff: ")

        try: filename = self.info_json['Persona Name: '].replace(".", "_")
        except TypeError: pass
        
        try: 
            with open(fr"Data/Info/{filename}.json", 'w') as outfile:
                json.dump(self.info_json, outfile)
        except UnboundLocalError: pass

core_thread = threading.Thread(target=Core)
core_thread.start()