import climage, json, wget, os, threading, requests
from steam.steamid import SteamID

class Console():

    def __init__(self):
        os.system('clear')
        print("-----VACTRACKER SHELL-----")

        console_thread = threading.Thread(target=self.console)
        console_thread.start()

        self.key = open("Data/key.txt", "r").read()
        if self.key == "":
            print("Please add your key in the key.txt file") 
            exit()
        self.commands = {

            "REMOVE": self.REMOVE,
            "ADD": self.ADD,
            "ALL": self.ALL,
            "REBASE": self.REBASE,
            "INFO": self.INFO

        }

    def console(self):
        while True:
            inp = input().split(" ")

            if inp[0] in self.commands:
                try: 
                    inp[1]
                    self.commands[inp[0]](inp[1])
                except IndexError:
                    try: self.commands[inp[0]]()
                    except TypeError: print("INFO must be followed by the name of a .json file")

    def rename(self, old, new):
        try: self.info_json[f"{new}"] = self.info_json.pop(f"{old}")
        except KeyError: self.info_json[f"{new}"] = "Could not get info"

    def ADD(self, steamid):
        try: 
            int(steamid)
            method = "(SteamID)"
        except:
            steamid = SteamID.from_url(f'https://steamcommunity.com/id/{steamid}')
            method = "(CustomID)"

        with open("Data/players.txt", "a+") as players_file:
            if str(steamid) in open("Data/players.txt", "r").read().split(","):
                print("This player is already in your list.")
            else:
                players_file.write(f"{steamid},")
                print(f"Player successfully added to tracklist. {method}")

    def REMOVE(self, steamid):
        try: int(steamid)
        except: steamid = SteamID.from_url(f'https://steamcommunity.com/id/{steamid}')

        with open("Data/players.txt", "w") as players_file:
            for filename in os.listdir("Data/Info/"):
                player_file = open(f"Data/Info/{filename}").read()
                player_json = json.loads(player_file)
                player_id = player_json["SteamID: "]
                try:
                    if int(player_id) == int(steamid):
                        os.remove(f"Data/Info/{player_json['Persona Name: ']}.json")
                    else: players_file.write(f"{player_id},")
                except TypeError: print("That account does not exist, please use steamid"); continue
            players_file.close()

    def ALL(self):
        os.system("clear")
        print("-----VACTRACKER SHELL-----")
        print("JSON:")
        for filename in os.listdir("Data/Info/"):
            file = open(f"Data/Info/{filename}", "r").read()
            print(f"{filename}; \x1b[30;5mPersona: {json.loads(file)['Persona Name: ']}\x1b[m")
        print("TXT: (might take a bit)")
        for player in open(f"Data/players.txt").read().split(","):
            if player == "": pass
            else:
                basic_request = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v1/?key={self.key}&steamids={player}')
                name = json.loads(basic_request.text)['response']['players']['player'][0]['personaname']
                try:
                    info = open(f"Data/Info/{name.replace('.', '_').replace(' ', '_')}.json", "r").read()
                    vac = json.loads(info)['VAC Banned: ']
                    if vac: vac = f"\x1b[31m{vac}\x1b[m" 
                    else: vac = f"\x1b[32m{vac}\x1b[m"
                    com = json.loads(info)['Community Banned: ']
                    if com: com = f"\x1b[31m{com}\x1b[m" 
                    else: com = f"\x1b[32m{com}\x1b[m"
                    game = json.loads(info)['Number of Game Bans: ']
                    if game > 3: game = f"\x1b[31m{game}\x1b[0m"
                    elif game >= 1: game = f"\x1b[33m{game}\x1b[0m"
                    else: game = f"\x1b[32m{game}\x1b[0m"
                    ingame = json.loads(info)['Currently in Game: ']
                    if ingame == "Could not get info": ingame = "\x1b[35m0\x1b[m"
                    else: ingame = "\x1b[34m1\x1b[m"
                    print(f"{name}, VAC-{vac} COM-{com} GAME-{game} INGAME-{ingame}")  
                except: print(f"No data yet for {name}") 
               

    def REBASE(self):
        os.system("clear")
        print("-----VACTRACKER SHELL-----")
        print("Rebasing...")

        with open("Data/players.txt", "w") as players_file:
            for filename in os.listdir("Data/Info/"):
                    player_file = open(f"Data/Info/{filename}").read()
                    player_json = json.loads(player_file)
                    players_file.write(f"{player_json['SteamID: ']},")
        
        os.system("clear")
        print("-----VACTRACKER SHELL-----")
        print("Rebased!")

    def INFO(self, name):
        os.system('clear')

        try: 
            file = open(f"Data/Info/{name}.json").read()
            self.info_json = json.loads(file)
            filename = wget.download(self.info_json["avatar"], bar=None)

            player_info = []
            for info in self.info_json:
                if info == 'avatar' or info == 'avatarmedium' or info == 'avatarfull' or info == 'avatarhash' or info == 'personastateflags' or info == 'gameid': 
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
