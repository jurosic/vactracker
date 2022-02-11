import climage, json, wget, os, threading
from steam.steamid import SteamID

class Console():

    def __init__(self):
        os.system('clear')
        print("-----VACTRACKER SHELL-----")

        console_thread = threading.Thread(target=self.console)
        console_thread.start()

        self.commands = {

            "REMOVE": self.REMOVE,
            "ADD": self.ADD,
            "ALL": self.ALL,
            "INFO": self.INFO

        }

    def console(self):
        while True:
            inp = input().split(" ")

            if inp[0] in self.commands:
                try: 
                    trash = inp[1]
                    self.commands[inp[0]](inp[1])
                except IndexError:
                    self.commands[inp[0]]()

    def rename(self, old, new):
        try: self.info_json[f"{new}"] = self.info_json.pop(f"{old}")
        except KeyError: self.info_json[f"{new}"] = "Could not get info"

    def ADD(self, steamid):
        try: int(steamid)
        except: steamid = SteamID.from_url(f'https://steamcommunity.com/id/{steamid}')

        with open("Data/players.txt", "a+") as players_file:
            players_file.write(f"{steamid},")
        
        print("Player successfully added to tracklist.")

    def REMOVE(self, steamid):
        try: int(steamid)
        except: steamid = SteamID.from_url(f'https://steamcommunity.com/id/{steamid}')

        with open("Data/players.txt", "w") as players_file:
            for filename in os.listdir("Data/Info/"):
                player_file = open(f"Data/Info/{filename}").read()
                player_json = json.loads(player_file)
                player_id = player_json["SteamID: "]
                print(steamid)
                print(player_json["SteamID: "])
                if player_id == steamid:
                    os.remove(f"Data/Info/{player_json['Persona Name: ']}.json")
                else: players_file.write(f"{player_id},")
            players_file.close()
            print("closed")

    def ALL(self):
        os.system("clear")
        print("-----VACTRACKER SHELL-----")
        for filename in os.listdir("Data/Info/"):
            file = open(f"Data/Info/{filename}", "r").read()
            print(json.loads(file)["Persona Name: "])

    def REBASE(self):
        os.system("clear")
        print("-----VACTRACKER SHELL-----")
        print("Rebasing...")

        with open("Data/players.txt", "w") as players_file:
            for filename in os.listdir("Data/Info/"):
                    player_file = open(f"Data/Info/{filename}").read()
                    player_json = json.loads(player_file)
                    players_file.write(f"{player_json['SteamID: ']},")

    def INFO(self, name):
        os.system('clear')

        try: 
            file = open(f"Data/Info/{name}.json").read()
            self.info_json = json.loads(file)
            filename = wget.download(self.info_json["avatar"], bar=None)

            player_info = []
            for info in self.info_json:
                if info == 'avatar' or info == 'avatarmedium' or info == 'avatarfull' or info == 'avatarhash' or info == 'personastateflags': 
                    continue
                player_info.append((info, self.info_json[info]))

            img = climage.convert(filename).split("\n")
            temp = []
            for i in img:
                i = i.split('  ')
                temp.append(i)
            os.remove(filename)

            temp.pop(len(temp)-1)

            for info, line in enumerate(temp):
                for pixels, pixel in enumerate(line):
                    print(pixel, end='  ')
                    if pixels % 41 == 40:
                        if info >= len(player_info):
                            print("")
                        else:
                            print(f"{player_info[info][0]}{player_info[info][1]}")
        except FileNotFoundError: 
            os.system('clear')
            print("-----VACTRACKER SHELL-----")
            print("This user does not exist")

Console = Console()