from datetime import datetime

import json
import os
import requests
import threading
import time


class Core:
    def __init__(self):
        self.key = open("Data/key.txt", "r").readline(32)
        try:
            os.mkdir("Data/Info")
            os.mkdir("Data/Info/TimeData")
        except FileExistsError:
            pass
        if self.key == "":
            print("Please add your key in the key.txt file")
            exit()

        self.curr_day = None
        self.max_pos = -1
        self.account_time_tracked = {}

        thread = threading.Thread(target=self.start)
        thread.start()

    def start(self):
        os.system('clear')
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
            except KeyboardInterrupt:
                print("Exiting..")
                exit()

    def rename(self, old, new, dir_type, failback=""):
        if dir_type == "info":
            try:
                self.info_json[f"{new}"] = [self.info_json.pop(f"{old}")]
            except KeyError:
                self.info_json[f"{new}"] = [failback]

        elif dir_type == "time":
            try:
                self.info_json[f"{new}"] = [time.strftime("%d.%m %Y", time.localtime(self.info_json.pop(f"{old}")))]
            except KeyError:
                self.info_json[f"{new}"] = [failback]

        elif dir_type == "ban":
            try:
                self.info_json[f"{new}"] = [self.ban_json.pop(f"{old}")]
            except KeyError:
                self.ban_json[f"{new}"] = [failback]

        elif dir_type == "gametime":
            try:
                self.info_json[f"{new}"] = [f'{round(self.game_list[f"{old}"] / 60, 2)} H']
            except KeyError:
                self.info_json[f"{new}"] = [failback]

        elif dir_type == "add":
            self.info_json[f"{new}"] = [old]

    def fetchInfo(self, steamid):
        try:

            self.trackTime()

            basic_request = requests.get(
                f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v1/?key={self.key}&steamids={steamid}')
            ban_request = requests.get(
                f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={self.key}&steamids={steamid}')
            game_request = requests.get(
                f'''https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={self.key}&steamid={steamid}&format=json''')

            basic_request.raise_for_status()
            ban_request.raise_for_status()

            self.info_json = json.loads(basic_request.text)["response"]["players"]["player"][0]
            self.ban_json = json.loads(ban_request.text)["players"][0]
            try:
                self.game_json = json.loads(game_request.text)["response"]["games"]
                game_json_failed = False
            except KeyError:
                game_json_failed = True
                pass

            self.rename("personaname", "Persona Name: ", "info", "Could not get persona name")
            self.rename("realname", "Real Name: ", "info", "Could not get real name (not defined/private)")
            self.rename("steamid", "SteamID: ", "info", "Could not get steamid")
            self.rename("profileurl", "URL: ", "info", "No profile URL")
            self.rename("VACBanned", "VAC Banned: ", "ban", "Failed to get VAC status")
            self.rename("CommunityBanned", "Community Banned: ", "ban", "Failed to get GameBan status")
            self.rename("NumberOfGameBans", "Number of Game Bans: ", "ban", "Could not get number of game bans")
            self.rename("DaysSinceLastBan", "Days Since Last Ban: ", "ban", "Could not get days since last time")
            self.rename("gameextrainfo", "Currently in Game: ", "info", "Currently Not in any Game")
            self.rename("gameserverip", "IP of Current Game Server: ", "info", "Currently Not in any Server/NA")
            if game_json_failed == False:
                for game in self.game_json:
                    if game["appid"] == 730:
                        self.game_list = game
                        self.rename("playtime_2weeks", "CS:GO PlayTime 2W: ", "gametime", "Could not get PlayTime")
                        self.rename("playtime_forever", "CS:GO PlayTime Forever: ", "gametime", "Cound not get PlayTime")
            else:
                self.rename("Account Private", "CS:GO PlayTime 2W: ", "add")
                self.rename("Account Private", "CS:GO PlayTime Forever: ", "add")
            self.rename("loccountrycode", "Country Code: ", "info", "Does not have country code set")
            self.rename("personastate", "Account Status: ", "info", "Could not get Account Status")
            self.rename("communityvisibilitystate", "Profile Visibility: ", "info", "Could not get Profile Visibility")
            self.rename("profilestate", "Configured Profile: ", "info", "Could not get Configured Profile")
            self.rename("commentpermission", "Comment Permissions: ", "info", "Could not get comment permissions")
            self.rename("primaryclanid", "Primary Clan ID: ", "info", "Does not have a Primary Clan/Private")
            self.rename("timecreated", "Account Age: ", "time", "Could not get time when account was created")
            self.rename("lastlogoff", "Last Logoff: ", "time", "Could not get info about last logoff")

            filename = self.info_json['Persona Name: '][0].replace(".", "_").replace(" ", "_")

            for existing_filename in os.listdir("Data/Info/"):
                try:
                    if existing_filename == "TimeData":
                        continue
                    old_file = open(fr"Data/Info/{existing_filename}").read()
                    existing_steamid = json.loads(old_file)["SteamID: "][0]
                    new_steamid = self.info_json["SteamID: "][0]
                    if existing_steamid == new_steamid:
                        for persona_name in json.loads(old_file)["Persona Name: "]:
                            if persona_name == self.info_json["Persona Name: "][0]:
                                if persona_name in self.info_json["Persona Name: "]:
                                    index = json.loads(old_file)["Persona Name: "].index(
                                        self.info_json["Persona Name: "][0])
                                    if index != 0:
                                        self.info_json["Persona Name: "].insert(index + 1, f"{persona_name}(prev)")
                            else:
                                self.info_json["Persona Name: "].append(persona_name)
                        if json.loads(old_file)["Persona Name: "][0] == self.info_json['Persona Name: '][0]:
                            continue
                        else:
                            os.remove(f"Data/Info/{existing_filename}")
                except json.decoder.JSONDecodeError:
                    pass

            with open(fr"Data/Info/{filename}.json", 'w') as outfile:
                json.dump(self.info_json, outfile)
        except requests.exceptions.ConnectionError:
            print("steam api did not respond, skipping..")
        except IndexError:
            print("Failed to get player info..")

    def trackTime(self):
        cycle_pos = 0
        for pos, filename in enumerate(os.listdir("Data/Info/")):
            try:
                cycle_pos += 1

                file = open(f"Data/Info/{filename}", "r").read()

                day = datetime.today().weekday()

                persona_name = filename.split('.j')[0]
                account_status = json.loads(file)['Account Status: '][0]

                if pos > self.max_pos:
                    self.account_time_tracked[pos] = {}
                    self.max_pos = pos
                self.account_time_tracked[pos] = {day: {}}
                self.curr_day = datetime.today().weekday()
                if self.curr_day != datetime.today().weekday():
                    for loop_pos in range(0, self.max_pos):
                        self.account_time_tracked[loop_pos] = {day: {}}
                    self.curr_day = datetime.today().weekday()

                if persona_name in self.account_time_tracked[pos][day]:
                    pass
                else:
                    self.account_time_tracked[pos][day] = {persona_name: [0, 0, 0]}

                if int(self.account_time_tracked[pos][day][persona_name][1]) == int(account_status):
                    pass
                else:
                    if account_status == 1:
                        self.account_time_tracked[pos][day][persona_name][1] = 1
                        self.account_time_tracked[pos][day][persona_name][2] = int(datetime.now().strftime('%H%M%S'))
                        time_data = open("Data/Info/TimeData/data.json", "w")
                        json.dump(self.account_time_tracked, time_data)
                        time_data.close()
                    if account_status == 0:
                        self.account_time_tracked[pos][day][persona_name][0] = \
                            self.account_time_tracked[pos][day][persona_name][0] + int(
                                datetime.now().strftime('%H%M%S')) - \
                            self.account_time_tracked[pos][day][persona_name][2]
                        self.account_time_tracked[pos][day][persona_name][1] = 0
                        self.account_time_tracked[pos][day][persona_name][2] = 0
                        time_data = open("Data/Info/TimeData/data.json", "w")
                        json.dump(self.account_time_tracked, time_data)
                        time_data.close()

            except IsADirectoryError:
                pass
            except json.decoder.JSONDecodeError:
                pass
