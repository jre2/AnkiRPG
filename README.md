AnkiRPG
=======
A turn based, color coded party, monster collecting, rpg for learning and memorization

#### Genre Overview
-------------------
Each turn, you perform a color coded "player test" among a number of options. If successful, members of your party bearing the same color as said option get to attack the enemy. If you fail, you lose your turn. Either way, the enemy then responds in kind during their turn, though computer opponents may have attack cooldowns instead of "player tests".

Progression primarily consists of party members being collected, leveled, evolved, and/or combined.

##### Player Test Types
-----------------------
These are popular types in the genre:

1. Quiz RPG - The test is answering a multiple choice trivia question, and color options are trivia categories.
2. Puzzles & Dragons - The test is creating a match-3 game match, and the color used is the color of the gems matched.

These are supported by AnkiRPG:

1. AnkiTest - The test is reviewing a flashcard in Anki, and the color option is the card's model/deck (ie. "category").
2. NoTest - There is no test performed (ie. test always passes). Color options don't signify anything.
3. CooldownTest - There is no test performed and it's treated as if all colors are always trigged. However, creatures obey cooldowns for attacks. This is what computer opponents use by default.


## How to play
--------------
##### Install
-------------
You need:
* python 2.7
* Anki 2.0.31+

For reference, these external packages are automatically included:
* termcolor (https://pypi.python.org/pypi/termcolor)
* colorama (https://pypi.python.org/pypi/colorama)

AnkiRPGServer.py must be placed into your Anki addons directory. It creates a server to allow Anki to be remotely controlled. The port may be tweaked in the source if needed.

##### Usage
-----------
This is highly subject to change!

main.py invokes the game, which currently caters to running a single adventure with a preset party and then exiting.

With a bit of alteration, you can choose to start the adventure as:
* HumanPlayer: You test yourself with Anki reps and make your own combat decisions. (50% Game, 50% Anki)
* HumanNoTestPlayer: You auto-pass tests and make your own combat decisions. (100% Game)
* HumanCooldownTestPlayer: You attack based on cooldowns instead of color tests and make your own combat decisions. (100% Game)
* AIPlayer: Computer controls your party according to cooldowns. (0% All; Useful for testing AnkiRPG)
* AINoTestPlayer: Computer controls your party according to colors. (0% All; Useful for benchmarking your party's power)
* AIAnkiTestPlayer: You use Anki but the computer makes combat decisions. (100% Anki)

##### Combat
-------------
Each round you may use your creatures' Special Skills (if charged), suggest an enemy for them to target (otherwise they'll use a basic AI to determine their best target), and eventually choose a player test option representing a color and category. Any of your creatures that share that color will attack this round if you pass the test.

At this point, Anki is focused and you are presented with a card to review/learn, which is from a deck and/or model based on the chosen option's category (not implemented yet). If successful, the aforementioned creatures get to attack. Also, all creatures have an Answer Skill that activates automatically when a test is answered particularly well, which in the case of AnkiRPG means the Anki rep was performed very quickly (not implemented yet; Answer skills always fire).

Then the enemy attacks and the next round begins. This cycle continues until one side is completely defeated. If you were successful, you continue the adventure. If you were defeated, you fail the adventure.

## TODO
-------
* Creature collection progression and management
  * Adventures should reward xp for creatures in party or give you new creatures, which can then be combined with others to create new/better/different ones (a la Shin Megami Tensei).
    * This also requires modifying creature stats based on level (perhaps a logarithmic factor) and have creature database describe how evolving/combining works.
  * Allow player to control which creatures are in his active party
  * Persist progress across games. At least collection, but possibly Adventure/Battle state as well.
* Quest hub with various adventures for the player to choose from
  * Random adventure of a user specified difficulty level
  * Handmade sequences of adventures with some element of story and/or progression to them
  * [future] Labyrinth with various encounters and treasures spread throughout. Find 3 keys to unlock boss room and complete.
* [future] Enhanced external interaction with Anki
  * Suggest to Anki to review due card vs learn new card, based on whether Player Test option is double/tri colored
  * Let player configure various decks he wants to use as categories for Player Test options
* [future] Multiplayer - tricky since ultimately we rely on the honor system for Player Test results
  * Head to Head - hot seat multiplayer already somewhat works
  * Tournament against ghosts of recent players / friends
  * Leaderboards
* Combat
  * Allow suggesting targets
  * Add skills for manipulation of colors
