More of a server-like tool that runs on two python threads that tracks info about steam accounts you've added, like VACBans CommunityBans, GameBans, PFPs, and so on.. Of course there still are bugs, but i dont think they're anything game breaking, im working on it, dw :), please create issues about bugs so i know what stuff is wrong because some errors might not happen to me.

```
COMMANDS: ADD [custom account id/steamid of account] (Adds account)
          REMOVE [custom account id/steamid uf account] (Removes account)
          REBASE (Takes appids from every .json file and replaces the players.txt with them)
          INFO [name of .json file] (Shows detailed info about the account of which the .json file was selected)
          ALL (Lists persona name of every account in the players.txt file, and names of all .json files, also lists VAC, COM and GAME bans)
```

TODO: set start time to 0 at end of day and add it to the day total or else it will be buggy, finish friendslist thingie, in game time for graph not getting game time sometime same goes for game time seems that if player plays through midnight it glitches, make shortcuts here and there in timetracker to optimise it, fix issue with steam api not responding due to lot of packets being sent, transfer online time past midnignt, optimise email sending, oh yeah, and make it FUCKING CLEANER, store what id the user was added with(cust uid), remove os.mkdir("Data/Info/TimeData"), ~~track time between multiple days (make player_file["Today Online For: "] a dictionary)~~, ~~add another int for online time in other modes (away, idle, etc.) and add support for them~~, ~~graph accounts online time for days~~, ~~add time online rn to time total~~, ~~save more info to something like extra info json~~[time, so far], ~~add online rn for to data.json~~, ~~change filenotfound to /his time file~~, ~~add a detailed view~~, ~~notify of wrong command~~, ~~add 'HELP' command~~, ~~Save info about player from time of add~~, ~~trace changes of accounts~~, ~~make a better refreshing function because banned list is sometimes empty~~, ~~get csgo play time~~, ~~fix random crashes~~, ~~make a "notification" system~~,

HARD TO DO: make gui more lively, fix error messages after KeyboardInterrupt, get group names and shiz like that, get friends list,

BUGS/ANNOYANCES: load in data.json after reboot, fix trackTime getting run in a for loop, in a for loop, fix time tracker for status 23456, make time data erase if player removed, some players are in game but arent recognized by VACTracker

