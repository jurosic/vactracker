from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import ssl
import smtplib
import json
import os
import requests
import threading
import time


class Core:
    def __init__(self):

        self.game_json = None
        self.account = None
        self.send_mail = None
        self.game_list = None
        self.ban_json = None
        self.info_json = None
        self.user = None
        self.server = None

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
        logged_in = False
        os.system('clear')
        while True:
            try:
                if not logged_in:
                    notif_config = json.loads(open("Data/notif.json", "r").read())
                    self.send_mail = notif_config["active"]
                    if self.send_mail:
                        server = notif_config["server"]
                        port = notif_config["port"]
                        self.account = notif_config["account"]
                        password = notif_config["password"]
                        self.user = notif_config["user"]

                        context = ssl.create_default_context()
                        self.server = smtplib.SMTP(server, port)
                        self.server.ehlo()
                        self.server.starttls(context=context)
                        self.server.ehlo()
                        self.server.login(self.account, password)
                        logged_in = True

            except FileNotFoundError:
                pass

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
            basic_request = requests.get(
                f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v1/?key={self.key}&steamids={steamid}')
            time.sleep(1)
            ban_request = requests.get(
                f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={self.key}&steamids={steamid}')
            time.sleep(1)
            game_request = requests.get(
                f'''https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={self.key}&steamid={steamid}&format=json''')

            basic_request.raise_for_status()
            ban_request.raise_for_status()
            game_request.raise_for_status()

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
            self.rename({}, "Time in Game: ", "add")
            self.rename("gameserverip", "IP of Current Game Server: ", "info", "Currently Not in any Server/NA")
            if not game_json_failed:
                for game in self.game_json:
                    if game["appid"] == 730:
                        self.game_list = game
                        self.rename("playtime_2weeks", "CS:GO PlayTime 2W: ", "gametime", "Could not get PlayTime")
                        self.rename("playtime_forever", "CS:GO PlayTime Forever: ", "gametime",
                                    "Cound not get PlayTime")
            else:
                self.rename("Account Private", "CS:GO PlayTime 2W: ", "add")
                self.rename("Account Private", "CS:GO PlayTime Forever: ", "add")
            self.rename("loccountrycode", "Country Code: ", "info", "Does not have a Country Code set")
            self.rename("personastate", "Account Status: ", "info", "Could not get Account Status")
            self.rename({}, "Online For: ", "add")
            self.rename("communityvisibilitystate", "Profile Visibility: ", "info", "Could not get Profile Visibility")
            self.rename("profilestate", "Configured Profile: ", "info", "Could not get Configured Profile")
            self.rename("commentpermission", "Comment Permissions: ", "info", "Could not get comment permissions")
            self.rename("primaryclanid", "Primary Clan ID: ", "info", "Does not have a Primary Clan/Private")
            self.rename("timecreated", "Date Created: ", "time", "Could not get time when account was created")
            self.rename("lastlogoff", "Last Logoff: ", "time", "Could not get info about last logoff")

            filename = self.info_json['Persona Name: '][0].replace(".", "_").replace(" ", "_")

            try:
                self.trackTime(filename)
            except FileNotFoundError:
                pass

            # Fix this son of a bitch and make it nicer please, and fix the emails ffs >_<
            try:
                for existing_filename in os.listdir("Data/Info/"):
                    try:
                        old_file = open(fr"Data/Info/{existing_filename}").read()
                        existing_steamid = json.loads(old_file)["SteamID: "][0]
                        new_steamid = self.info_json["SteamID: "][0]
                        old_json = json.loads(old_file)
                        if existing_steamid == new_steamid:
                            for persona_name in json.loads(old_file)["Persona Name: "]:
                                if persona_name == self.info_json["Persona Name: "][0]:
                                    if persona_name in self.info_json["Persona Name: "]:
                                        index = json.loads(old_file)["Persona Name: "].index(
                                            self.info_json["Persona Name: "][0])
                                        if index != 0:
                                            self.info_json["Persona Name: "].insert(index + 1,
                                                                                    f"{persona_name}(prev)")
                                else:
                                    self.info_json["Persona Name: "].append(persona_name)

                            if json.loads(old_file)["VAC Banned: "][0] != self.info_json["VAC Banned: "][0]:
                                self.info_json["VAC Banned: "].append(json.loads(old_file)["VAC Banned: "][0])
                                if self.send_mail:
                                    if old_json["VAC Banned: "][0] != self.info_json["VAC Banned: "][0]:
                                        message = MIMEMultipart("alternative")
                                        message["Subject"] = "An accounts info has recently changed!"
                                        message["From"] = self.account
                                        message["To"] = self.user

                                        html = f"""\
                                                    <html>
                                                        <body>
                                                            <p>The player {self.info_json['Persona Name: '][0]} has recently\
                                                             been VAC Banned! </p>
                                                            <img src={self.info_json['avatarfull']}>
                                                        </body>
                                                    </html>"""
                                        part = MIMEText(html, "html")
                                        message.attach(part)

                                        self.server.sendmail(self.account, self.user, message.as_string())

                            if json.loads(old_file)["Persona Name: "][0] != self.info_json['Persona Name: '][0]:
                                os.remove(f"Data/Info/{existing_filename}")

                            if self.send_mail:

                                if old_json["Community Banned: "][0] != self.info_json["Community Banned: "][0]:
                                    message = MIMEMultipart("alternative")
                                    message["Subject"] = "An accounts info has recently changed!"
                                    message["From"] = self.account
                                    message["To"] = self.user

                                    html = f"""\
                                                <html>
                                                    <body>
                                                        <p>The player {self.info_json['Persona Name: '][0]} has recently been COMMUNITY Banned! </p>
                                                        <img src={self.info_json['avatarfull']}>
                                                    </body>
                                                </html>"""

                                    part = MIMEText(html, "html")
                                    message.attach(part)

                                    self.server.sendmail(self.account, self.user, message.as_string())

                                if old_json["Number of Game Bans: "][0] != \
                                        self.info_json["Number of Game Bans: "][0]:
                                    message = MIMEMultipart("alternative")
                                    message["Subject"] = "An accounts info has recently changed!"
                                    message["From"] = self.account
                                    message["To"] = self.user

                                    html = f"""\
                                                <html>
                                                    <body>
                                                        <p>The player {self.info_json['Persona Name: '][0]} has recently been GAME Banned! </p>
                                                        <img src={self.info_json['avatarfull']}>
                                                    </body>
                                                </html>"""

                                    part = MIMEText(html, "html")
                                    message.attach(part)

                                    self.server.sendmail(self.account, self.user, message.as_string())

                                if old_json["Persona Name: "][0] != self.info_json["Persona Name: "][0]:
                                    message = MIMEMultipart("alternative")
                                    message["Subject"] = "An accounts info has recently changed!"
                                    message["From"] = self.account
                                    message["To"] = self.user

                                    html = f"""\
                                                <html>
                                                    <body>
                                                        <p>The player {json.loads(old_file)["Persona Name: "][0]} has changed his persona name to {self.info_json["Persona Name: "][0]}</p>
                                                        <img src={self.info_json['avatarfull']}>
                                                    </body>
                                                </html>"""

                                    part = MIMEText(html, "html")
                                    message.attach(part)

                                    self.server.sendmail(self.account, self.user, message.as_string())

                    except json.decoder.JSONDecodeError:
                        pass
            except FileNotFoundError:
                pass

            with open(fr"Data/Info/{filename}.json", 'w') as outfile:
                json.dump(self.info_json, outfile)
        except requests.exceptions.ConnectionError:
            print("steam api did not respond, skipping..")
        except requests.exceptions.HTTPError:
            print("steam api threw internal server error, skipping...")
        except IndexError:
            print("Failed to get player info..")

    def trackTime(self, filename):

        player_file = json.loads(open(f"Data/Info/{filename}.json", "r").read())
        raw_time = datetime.now().strftime('%H:%M:%S').split(":")
        time_now = (int(raw_time[0]) * 3600) + (int(raw_time[1]) * 60) + (int(raw_time[2]))
        day = str(datetime.today().weekday())

        if day not in player_file["Online For: "][0]:
            player_file["Online For: "][0][day] = [0, 0, 0, 0, 0, False]
        if day not in player_file["Time in Game: "][0]:
            player_file["Time in Game: "][0][day] = [0, 0, 0, False]

        latest_key = 0
        for key, value in player_file.items():
            latest_key = key

        if latest_key == 6 and day == 0:
            pass
        else:
            self.info_json["Online For: "][0] = player_file["Online For: "][0]
            self.info_json["Time in Game: "][0] = player_file["Time in Game: "][0]

        if player_file["Currently in Game: "][0] != self.info_json["Currently in Game: "][0]:
            if self.info_json["Currently in Game: "][0] != "Currently Not in any Game":
                self.info_json["Time in Game: "][0][day][2] = time_now
            else:
                self.info_json["Time in Game: "][0][day][0] = (time_now -
                                                               player_file["Time in Game: "][0][day][2] +
                                                               player_file["Time in Game: "][0][day][0])
                self.info_json["Time in Game: "][0][day][2] = 0

        if player_file["Account Status: "][0] != self.info_json["Account Status: "][0]:
            if self.info_json["Account Status: "][0] == 1:
                if player_file["Account Status: "][0] > 1:
                    self.info_json["Online For: "][0][day][2] = (time_now - player_file["Online For: "][0][day][4] +
                                                                 player_file["Online For: "][0][day][2])
                self.info_json["Online For: "][0][day][4] = time_now

            if self.info_json["Account Status: "][0] > 1:
                self.info_json["Online For: "][0][day][0] = (time_now - player_file["Online For: "][0][day][4] +
                                                             player_file["Online For: "][0][day][0])
                self.info_json["Online For: "][0][day][4] = time_now

            if self.info_json["Account Status: "][0] == 0:
                if player_file["Account Status: "][0] > 1:
                    self.info_json["Online For: "][0][day][2] = (time_now - player_file["Online For: "][0][day][4] +
                                                                 player_file["Online For: "][0][day][2])
                else:
                    self.info_json["Online For: "][0][day][0] = (time_now - player_file["Online For: "][0][day][4] +
                                                                 player_file["Online For: "][0][day][0])
                self.info_json["Online For: "][0][day][4] = 0

        if self.info_json["Currently in Game: "][0] != "Currently Not in any Game":
            if not self.info_json["Time in Game: "][0][day][3]:
                self.info_json["Time in Game: "][0][day][2] = time_now
                player_file["Time in Game: "][0][day][3] = True

            self.info_json["Time in Game: "][0][day][1] = (time_now -
                                                           player_file["Time in Game: "][0][day][2])

        if self.info_json["Account Status: "][0] == 1:
            if not player_file["Online For: "][0][day][5]:
                self.info_json["Online For: "][0][day][4] = time_now
                player_file["Online For: "][0][day][5] = True

            self.info_json["Online For: "][0][day][1] = time_now - player_file["Online For: "][0][day][4]
        else:
            self.info_json["Online For: "][0][day][1] = 0

        if self.info_json["Account Status: "][0] > 1:
            if not player_file["Online For: "][0][day][5]:
                self.info_json["Online For: "][0][day][4] = time_now
                player_file["Online For: "][0][day][5] = True

            self.info_json["Online For: "][0][day][3] = time_now - player_file["Online For: "][0][day][4]
        else:
            self.info_json["Online For: "][0][day][3] = 0


if __name__ == "__main__":
    print("Please run this as an import and initialize the class")
