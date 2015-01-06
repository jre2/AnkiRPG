AnkiRPG
=======
A turn based, color coded party, monster collecting, rpg for learning and memorization

#### Genre Overview
-------------------
Each turn, you perform a color coded "player test" among a number of options. If successful, members of your party bearing the same color as said option get to attack the enemy. If you fail, you lose your turn. Either way, the enemy responds in kind during their turn, though computer opponents have attack cooldowns instead of "player tests".

In addition, progression primarily consists of party members being collected, leveled, evolved, and/or combined.

##### Player Test Types
-----------------------
These are popular types in the genre:

1. Quiz RPG - The test is answering a multiple choice trivia question, and color options are trivia categories.
2. Puzzles & Dragons - The test is creating a match-3 game match, and the color used is the color of the gems matched.

These are supported by AnkiRPG:

1. AnkiRPG - The test is reviewing a flashcard in Anki, and the color option is the card's model/deck (ie. "category").
2. NoTest - There is no player performed test/color and instead party members use simple cooldowns for attacks. This is what computer opponents use.

##### Install
-------------
You need:
* python2.7
* termcolor (https://pypi.python.org/pypi/termcolor)
* colorama (https://pypi.python.org/pypi/colorama) [Only on Windows and only if you want color]

## TODO
-------
* External interaction with Anki
  * Tell Anki server plugin to do card rep and reply with user's selected ease, which will be used as Player Test result
  * [future] Suggest to Anki to review due card vs learn new card, based on whether Player Test option is double/tri colored
  * [future] Let player configure various decks he wants to use as categories for Player Test options
* Creature collection progression and management
  * Adventures should reward xp for creatures in party or give you new creatures, which can then be combined with others to create new/better/different ones (a la Shin Megami Tensei)
  * Allow player to control which creatures are in his active party
  * Persist player information across games
* Quest hub with various adventures for the player to choose from
  * Random adventure of a user specified difficulty level
  * Handmade sequences of adventures with some element of story and/or progression to them
* [future] Multiplayer - tricky since ultimately we rely on the honor system for Player Test results
  * Head to Head
  * Tournament against ghosts of recent players / friends
  * Leaderboards
