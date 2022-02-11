import requests, climage, json, wget, os

class Console():

    def __init__(self):
        self.commands = {

            "INFO": self.INFO

        }

    def console(self):
        while True:
            inp = input().split(" ")


            if inp[0] in self.commands:
                self.commands[inp[0]](inp[1])

    def rename(self, old, new):
        try: self.info_json[f"{new}"] = self.info_json.pop(f"{old}")
        except: 
            self.info_json[f"{new}"] = "Could not get info"
            self.info_json.pop(f"{old}")

    def INFO(self, steamid):
        os.system('clear')

        request = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v1/?key=FCC3CCD9F0EF902B6D12A08F7A697E0E&steamids={steamid}')

        self.info_json = json.loads(request.text)["response"]["players"]["player"][0]

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

        for info, line in enumerate(temp):
            for pixels, pixel in enumerate(line):
                print(pixel, end='  ')
                if pixels % 41 == 40:
                    if info >= len(player_info):
                        print("")
                    else:
                        print(f"{player_info[info][0]}{player_info[info][1]}")

Console = Console()