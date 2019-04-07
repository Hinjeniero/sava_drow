#### TODO CURRENT:
- [ ] Complete the update character in the network_board
- [ ] Parse text to have decents numbers and letters instead of shitty indexes
- [ ] Set tutorial
- [ ] Make simple IA based on the alpha-beta proning.
- [ ] Keep and drop servers based in a keep/alive fashion
- [ ] Bug when moving char besides enemy pawn, since in the destinies is not this cell cuz of closer to enemies restriction.
- [ ] Test recent changes

#### TODO WHENEVER:
- [ ] Effect when chars colliding with each other.
- [ ] Bar of taunts below, the cursor turns into whatever and sends the position to the rest of the clients.
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
- [X] Manage threads to avoid overpopulation of them. Create them ahead of time to save the creating time.
- [X] Connect the fitness result with cells in a graphical fashion
- [X] Check the creation of overlays and value texts in board to think a way to do it only once per turn.
- [X] Center the values on the cell and add a button maybe? Or some sort of texture below it.
- [X] Add dict of cells to not being processing fitnesses again when useless.
- [X] Make fitness value texture work.
- [X] The dice crashes teh game when hovering it after shuffling once
- [X] Position the dice.
- [X] Game infoboard in the right side.
- [X] Add HolyChampion behavior in promotion cells.
- [X] When player gets a 6, can move enemy piece that can capture anything, except the matron mother (Orcs both sides as hostile). Else loses a turn.
- [X] Add a blocked postiions array, due to shit from turncoats
- [X] Check set_canvas_size with the fitness sprites.
- [X] Probability in dice modified to turns and number of throws. Do this in the arch dice, or make dice for each player?