# foe_bot

A Python bot using selenium to automate certain actions in the game Forge of Empire.  
This bot requires the username and password to be stored in the `config.json` file. Upon running, it automatically opens a browser window, logs into your account, and performs a series of actions on your behalf.

The bot is still in the early stages, so manual intervention and supervision are required. I currently use the bot once a day to collect all buildings at once, as both the 100PF limit and the "collect all" cost of 5 diamonds can be a hassle.

## Features
- Collects all productions
- Collects the top 15 buildings that generate the most Forge Points (useful for the Blue Galaxy)

## Untested Features  
(These are features that I’ve added but haven't rigorously tested yet)
- Start production in supplies, goods and military buildings
- Collect silver from the tavern when it’s full
- Polish friends' / guild members' / neighbors' buildings
- Sit in friends' taverns
- Collect hidden rewards (currently buggy)
- Collect quests

## TO-DO
- Improve the collection process for buildings (currently requires too much manual input)
- Investigate if Blue Galaxy collection can be shortened to one request instead of two
- Test untested features
- Improve the browser load speed (currently slow due to using seleniumwire)
- Automate Guild Battlegrounds and Expedition Battles
- Investigate how to perform actions using only the UserKey, SID, and URL instead of the username and password
