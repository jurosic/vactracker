More of a server-like tool that runs on two python threads that tracks info about steam accounts you've added, like VACBans CommunityBans, GameBans, PFPs, and so on.. Of course there still are bugs, but i dont think they're anything game breaking, im working on it, dw :)

```
COMMANDS: ADD [custom account id/steamid of account] (Adds account)
          REMOVE [custom account id/steamid uf account] (Removes account)
          REBASE (Takes appids from every .json file and replaces the players.txt with them)
          INFO [name of .json file] (Shows detailed info about the account of which the .json file was selected)
          ALL (Lists persona name of every account in the players.txt file, and names of all .json files, also lists VAC, COM and GAME bans)
```

TODO: transfer online time past midnignt, track time between multiple days (make player_file["Today Online For: "] a dictionary), add time online rn to time total, optimise email sending, oh yeah, and make it FUCKING CLEANER, store what id the user was added with(cust uid), get friends list, graph accounts online time for days, ~~save more info to something like extra info json~~[time, so far], add online rn for to data.json, change filenotfound to /his time file, ~~add a detailed view~~, ~~notify of wrong command~~, ~~add 'HELP' command~~, ~~Save info about player from time of add~~, ~~trace changes of accounts~~, ~~make a better refreshing function because banned list is sometimes empty~~, ~~get csgo play time~~, ~~fix random crashes~~, ~~make a "notification" system~~,

HARD TO DO: make gui more lively, fix error messages after KeyboardInterrupt, get group names and shiz like that,

BUGS/ANNOYANCES: load in data.json after reboot, fix trackTime getting run in a for loop, in a for loop, fix time tracker for status 23456, make time data erase if player removed, some players are in game but arent recognized by VACTracker

