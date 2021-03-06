from steam.steamid import SteamID
from termgraph import termgraph as tg
from datetime import datetime

import smtplib
import ssl
import json
import os
import threading
import wget
import climage
import requests
import time


class Console:

    def __init__(self):
        os.system('clear')
        print("-----VACTRACKER SHELL-----")

        try:
            console_thread = threading.Thread(target=self.console)
            console_thread.start()
        except KeyboardInterrupt:
            print("Exiting..")
            exit()

        self.key = open("Data/key.txt", "r").readline(32)
        if self.key == "":
            print("Please add your key in the key.txt file")
            exit()

        self.tg_len_categories = 2
        self.tg_args = {'filename': '', 'title': None, 'width': 50,
                        'format': '{:<5.2f}', 'suffix': '', 'no_labels': False,
                        'color': None, 'vertical': False, 'stacked': True,
                        'different_scale': False, 'calendar': False,
                        'start_dt': None, 'custom_tick': '', 'delim': '',
                        'verbose': False, 'version': False}
        self.tg_colors = [91, 92, 90, 94]

        self.commands = {

            "REMOVE": {"method": self.REMOVE,
                       "description": """Removes an accounts .json file and removes them from the players.txt file\
which in result stops the player from being updated."""},

            "ADD": {"method": self.ADD,
                    "description": """Adds an account to the players.txt file and when the core calls\
a refresh a .json file of this account will be created."""},

            "DELETE" : {"method": self.DELETE,
                        "description": "Deletes the json file specified, if you want it to get reset"},

            "ALL": {"method": self.ALL,
                    "description": "Shows all accounts and their .json file"},

            "REBASE": {"method": self.REBASE,
                       "description": "Collects SteamIDs from .json files and adds them to the players.txt file"},

            "FROMFILE": {"method": self.FROMFILE,
                         "description": "Adds players from a file of SteamIDs or CustomIDs, separated by commas"},

            "INFO": {"method": self.INFO,
                     "description": """Shows detailed info about an account, the command parameter has to be the\
name of a .json file"""},

            "CLEAR": {"method": self.CLEAR,
                      "description": "Clears the terminal"},

            "LOGIN": {"method": self.LOGIN,
                      "description": """Logs the program into the email you specified to send notifications, \
syntax is 'LOGIN email password recv_email'"""},

            "FRIENDLIST": {"method": self.FRIENDLIST,
                           "description": "Shows the specified accounts friends"},

            "HELP": {"method": self.HELP,
                     "description": "Shows help"}

        }

    def console(self):
        while True:
            inp = input().split(" ")

            if inp[0] in self.commands:
                try:
                    self.commands[inp[0]]["method"](inp[1], inp[2], inp[3])
                except IndexError:
                    try:
                        self.commands[inp[0]]["method"](inp[1], inp[2])
                    except IndexError:
                        try:
                            self.commands[inp[0]]["method"](inp[1])
                        except IndexError:
                            try:
                                self.commands[inp[0]]["method"]()
                            except TypeError:
                                print("Invalid syntax!")
            else:
                print(f"The command '{inp[0]}' does not exist")

    @staticmethod
    def CLEAR():
        os.system('clear')
        print("-----VACTRACKER SHELL-----")

    def HELP(self):
        for command in self.commands:
            print(f"{command}: {self.commands[command]['description']}")

    @staticmethod
    def LOGIN(account, password, user, smtp_server="smtp.gmail.com", port=587):
        context = ssl.create_default_context()
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(account, password)
            server.sendmail(account, user, "Successfully logged in!")
            notif_config = open("Data/notif.json", "w+")
            config = {
                "active": True,
                "account": account,
                "password": password,
                "user": user,
                "server": smtp_server,
                "port": port
            }
            json.dump(config, notif_config)
            notif_config.close()
        except Exception as e:
            print(e)
        finally:
            server.quit()

    @staticmethod
    def ADD(steamid):
        try:
            int(steamid)
            method = "(SteamID)"
        except ValueError:
            steamid = SteamID.from_url(f'https://steamcommunity.com/id/{steamid}')
            method = "(CustomID)"

        with open("Data/players.txt", "a+") as players_file:
            if str(steamid) in open("Data/players.txt", "r").read().split(","):
                print("This player is already in your list.")
            else:
                if steamid is not None:
                    players_file.write(f"{steamid},")
                    print(f"Player successfully added to track list. {method}")
                else:
                    print("This player does not exist!")

    @staticmethod
    def REMOVE(steamid):
        try:
            int(steamid)
        except ValueError:
            steamid = SteamID.from_url(f'https://steamcommunity.com/id/{steamid}')

        with open("Data/players.txt", "w") as players_file:
            for filename in os.listdir("Data/Info/"):
                player_file = open(f"Data/Info/{filename}").read()
                player_json = json.loads(player_file)
                player_id = player_json["SteamID: "][0]
                try:
                    if int(player_id) == int(steamid):
                        os.remove(f"Data/Info/{player_json['Persona Name: '][0]}.json")
                    else:
                        players_file.write(f"{player_id},")
                except TypeError:
                    print("That account does not exist, please use SteamID")
                    continue
            players_file.close()

    @staticmethod
    def DELETE(filename):
        with open(f"Data/Info/{filename}", "r") as file:
            name = json.loads(file.read())["Persona Name: "][0]
        if input(f"Are you sure you want to delete {name} [y/N]").lower() == "y":
            os.remove(f"Data/Info/{filename}")
        else:
            print("Cancelling..")

    def ALL(self):
        os.system("clear")
        print("-----VACTRACKER SHELL-----")

        print("\x1b[37m\x1b[1mJSON:\x1b[m")
        for filename in os.listdir("Data/Info/"):
            try:
                file = open(f"Data/Info/{filename}", "r").read()
                print(f"{filename}; \x1b[30;5mPersona: {json.loads(file)['Persona Name: ']}\x1b[m")
            except IsADirectoryError:
                pass
        print("\n\x1b[37m\x1b[1mTXT:\x1b[m (might take a bit)")
        for player in open(f"Data/players.txt").read().split(","):
            if player == "":
                pass
            else:
                try:
                    basic_request = requests.get(
                        f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v1/?key={self.key}&steamids={player}')
                    name = json.loads(basic_request.text)['response']['players']['player'][0]['personaname']
                    info = open(f"Data/Info/{name.replace('.', '_').replace(' ', '_')}.json", "r").read()

                    vac = json.loads(info)['VAC Banned: '][0]
                    if vac:
                        vac = f"\x1b[31m{vac}\x1b[m"
                    else:
                        vac = f"\x1b[32m{vac}\x1b[m"

                    com = json.loads(info)['Community Banned: '][0]
                    if com:
                        com = f"\x1b[31m{com}\x1b[m"
                    else:
                        com = f"\x1b[32m{com}\x1b[m"

                    game = json.loads(info)['Number of Game Bans: '][0]
                    if game > 3:
                        game = f"\x1b[31m{game}\x1b[0m"
                    elif game >= 1:
                        game = f"\x1b[33m{game}\x1b[0m"
                    else:
                        game = f"\x1b[32m{game}\x1b[0m"

                    ingame = json.loads(info)['Currently in Game: '][0]
                    if ingame == "Currently Not in any Game":
                        ingame = "\x1b[35m0\x1b[m"
                    else:
                        ingame = "\x1b[34m1\x1b[m"
                    online = json.loads(info)['Account Status: '][0]

                    print(f"{name}, VAC-{vac} COM-{com} GAME-{game} INGAME-{ingame} STATUS-{online}")

                except FileNotFoundError:
                    print(f"No data yet for {name}")
                except json.decoder.JSONDecodeError:
                    print("Failed to read from response, please try again, check if your key is correct")
                except requests.exceptions.ConnectionError:
                    print("Steam api did not respond for this player, try again")

        print("\n\x1b[37m\x1b[1mCHEAT SHEET:\x1b[m\nSTATUS: 0-OFF 1-ON 2-BUSY 3-AWAY 4-SNOOZE 5-LTT 6-LTP")

    @staticmethod
    def REBASE():
        os.system("clear")
        print("-----VACTRACKER SHELL-----")
        print("Rebasing...")

        with open("Data/players.txt", "w") as players_file:
            for filename in os.listdir("Data/Info/"):
                player_file = open(f"Data/Info/{filename}").read()
                player_json = json.loads(player_file)
                print(f"Rebased: {player_json['Persona Name: '][0]}, {player_json['SteamID: '][0]}")
                players_file.write(f"{player_json['SteamID: '][0]},")
        print("Rebasing finished!")

    def FROMFILE(self, filename):
        os.system("clear")
        print("-----VACTRACKER SHELL-----")

        with open(filename, "r") as file:
            with open("Data/players.txt", "a+") as players_file:
                for line in file:
                    for player in line.split(","):
                        if player != "" or player != "\n":
                            try:
                                int(player)
                                method = "(SteamID)"
                            except ValueError:
                                player = SteamID.from_url(f'https://steamcommunity.com/id/{player}')
                                method = "(CustomID)"

                            basic_request = requests.get(
                                f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v1/?key={self.key}&steamids={player}')
                            name = json.loads(basic_request.text)['response']['players']['player'][0]['personaname']

                            if str(player) in open("Data/players.txt", "r").read().split(","):
                                print(f"{name} is already in your list. {player}, {method}")

                            else:
                                players_file.write(f"{player},")
                                print(f"Added: {name}, {player}, {method}")

    def FRIENDLIST(self, steamid):
        os.system("clear")
        print("-----VACTRACKER SHELL-----")
        try:
            int(steamid)
        except ValueError:
            for filename in os.listdir("Data/Info/"):
                account = open(f"Data/Info/{filename}", "r").read()
                account = json.loads(account)
                if account["Persona Name: "][0] == steamid:
                    steamid = account["SteamID: "][0]
        friends_request = requests.get(
            f'''https://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={self.key}&steamid={steamid}&relationship=friend''')
        try:
            friends = json.loads(friends_request.text)["friendslist"]["friends"]

            for friend in range(len(friends)):
                friend_steamid = friends[friend]["steamid"]
                friend_since = time.strftime("%d.%m %Y", time.localtime(friends[friend]["friend_since"]))
                print(
                    f"SteamID: {[friend_steamid]}, URL: [https://steamcommunity.com/profiles/{[friend_steamid][0]}], Friends Since: {[friend_since]}")

        except json.decoder.JSONDecodeError:
            print("Could not get friend list, please try again or make sure the account isn't private")

    def INFO(self, name):
        os.system('clear')

        try:
            file = open(f"Data/Info/{name}.json").read()
            info_json = json.loads(file)
            filename = wget.download(info_json["avatar"], bar=None)

            player_info = []
            for info in info_json:
                if info == 'avatar' or info == 'avatarmedium' or info == 'avatarfull' or info == 'avatarhash' or info == 'personastateflags' or info == 'gameid' or info == 'lobbysteamid':
                    continue
                elif info == "Online For: ":
                    day = str(datetime.today().weekday())
                    player_info.append((info, [f"""TT-O: {round((info_json[info][0][day][0] / 3600) +
                                                                (info_json[info][0][day][1] / 3600), 3)}H""",
                                               f"TS-O: {round(info_json[info][0][day][1] / 3600, 3)}H",
                                               f"""TT-BASLL: {round((info_json[info][0][day][2] / 3600) +
                                                                    (info_json[info][0][day][3] / 3600), 3)}H""",
                                               f"TS-BASLL: {round(info_json[info][0][day][3] / 3600, 3)}H"]))

                elif info == "Time in Game: ":
                    day = str(datetime.today().weekday())
                    player_info.append((info, [f"""TT-IG: {round((info_json[info][0][day][0] / 3600) +
                                                                 (info_json[info][0][day][1] / 3600), 3)}H""",
                                               f"TS-IG: {round(info_json[info][0][day][1] / 3600, 3)}H"]))

                else:
                    player_info.append((info, info_json[info]))

            img = climage.convert(filename).split("\n")
            temp = []
            for i in img:
                i = i.split('  ')
                temp.append(i)
            os.remove(filename)

            temp.pop(len(temp) - 1)

            for info, line in enumerate(temp):
                for pixels, pixel in enumerate(line):
                    print(pixel, end='  ')
                    if pixels % 41 == 40:
                        if info >= len(player_info):
                            print("")
                        else:
                            print(f"{player_info[info][0]}{player_info[info][1]}")

            self._drawGraph(name)

        except FileNotFoundError:
            os.system('clear')
            print("-----VACTRACKER SHELL-----")
            print("That user does not exist")

        except KeyError:
            print(f"No time data for {name}, please wait.")

    def _drawGraph(self, name):
        print("Online Time Graph for Multiple Days in Hours: ")
        print("-" * 80)
        player_file = open(f"Data/Info/{name}.json", "r").read()
        player_time = json.loads(player_file)["Online For: "][0]

        labels = []
        data = []
        normal_data = []

        for key, value in player_time.items():
            labels.append(key)
            data.append([(value[0] / 3600), (value[2] / 3600), (value[3] / 3600), (value[1] / 3600)])
            normal_data.append([((value[0] / 3600) * 6), ((value[2] / 3600) * 6), ((value[3] / 3600) * 6),
                                ((value[1] / 3600) * 6)])

        tg.stacked_graph(labels, data, normal_data, self.tg_len_categories, self.tg_args, self.tg_colors)

        print("\nIn Game Time Graph for Multiple Days in Hours: ")
        print("-" * 80)
        player_file = open(f"Data/Info/{name}.json", "r").read()
        player_time = json.loads(player_file)["Time in Game: "][0]

        labels = []
        data = []
        normal_data = []

        for key, value in player_time.items():
            labels.append(key)
            data.append([(value[0] / 3600), (value[1] / 3600)])
            normal_data.append([((value[0] / 3600) * 6), ((value[1] / 3600) * 6)])

        tg.stacked_graph(labels, data, normal_data, self.tg_len_categories, self.tg_args, self.tg_colors)


if __name__ == "__main__":
    print("Please run this as an import and initialize the class")
