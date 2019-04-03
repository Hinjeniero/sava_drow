#### TODO CURRENT:
- [ ] Connect the dice to some random choice
- [ ] Game infoboard in the right side. WIP ~20%
- [ ] Keep and drop servers based in a keep/alive fashion
- [ ] Connect the fitness result with cells in a graphical fashion 
- [ ] Set tutorial 

#### TODO WHENEVER:
- [ ] Effect when chars colliding with each other.
- [ ] Bar of taunts below, the cursor turns into whatever and sends the position to the rest of the clients.
- [ ] Add HolyChampion behavior in promotion cells.
- [ ] Add some animations and shit to promotion of a char, like stars or particles or something

#### DONE:
- [X] Implement spider dice + sprite. Needs to randomize the game a little bit.
- [X] MAKE SELECTABLE Table
- [X] Test Selectable Table
- [X] Change my_master in class Character to be the uuid instead of a lousy name. This could bring trouble if the name of both players its the same.
- [X] Set aliases of characters in settings. They have no fuckin use in the program flow anyway.
- [X] Maybe move all the registration part to the goddamn board_server? Yes.
- [X] Improve node server to not accept servers with the same UUID
- [X] Send another field in the json that is TOTAL_PLAYERS. Another one with NAME.
- [X] Fix bug of the fucken aliases.
- [X] UUID seems to be created in each start of the game. Fixed
- [X] Connect board server to the update_method.
- [X] Connect board server to the delete_method