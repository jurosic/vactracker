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

    def INFO(self, steamid):
        os.system('clear')

        request = requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v1/?key=FCC3CCD9F0EF902B6D12A08F7A697E0E&steamids={steamid}')

        info_json = json.loads(request.text)["response"]["players"]["player"][0]

        info_json["Persona Name: "] = info_json.pop("personaname")
        info_json["SteamID: "] = info_json.pop("steamid")
        info_json["URL: "] = info_json.pop("profileurl")
        info_json["COuntry Code: "] = info_json.pop("loccountrycode")
        info_json["Account Status: "] = info_json.pop("personastate")
        info_json["Profile Visibility: "] = info_json.pop("communityvisibilitystate")
        info_json["Configured Profile: "] = info_json.pop("profilestate")
        info_json["Comment Permissions: "] = info_json.pop("commentpermission")
        info_json["Primary Clan ID: "] = info_json.pop("primaryclanid")
        info_json["Account Age: "] = info_json.pop("timecreated")
        

        filename = wget.download(info_json["avatar"], bar=None)

        player_info = []
        for info in info_json:
            if info == 'avatar' or info == 'avatarmedium' or info == 'avatarfull' or info == 'avatarhash' or info == 'personastateflags': 
                continue
            player_info.append((info, info_json[info]))

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