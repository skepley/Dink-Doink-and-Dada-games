# Rain Worms EV calculator
Are you tired of losing to your kids at Rain Worms? Do you want to smash their beautiful smug little faces and silence their mocking laughs? Do you love them, but want to also crush their dreams? Then this is for you. 

This is a simple Python calculator for navigating a single turn in the game Rain Worms / Pickomino. Each round of a turn consists of rolling the remaining dice and choosing which face to set aside. This calculator computes the expected number of worms for every possible choice so you can always choose the maximal EV. It continues to evaluate the optimal play after each later decision, even if its not the optimal/maximal choice. 

## Run it

Use Python 3.10 or newer and simply run the following in a terminal:

```
python rain_worms_ev.py --interactive
```

Commands are entered at the `EV>` prompt for examples:

```text
start
pool -21
mine 24
opponent 29
roll 1 2 2 3 4 5 5 6
pick 5
roll 1 2 3 4 6 6
quit
```
Descriptions of each command are as follows:

Use `pool <tile>` to add a tile to the free pool, such as `pool 25`. Using a minus allows you to remove a tile from the free pool instead e.g. `pool -25`. The command reports an error if an addition or removal cannot be made. 

Setting `mine <tile>` or `opponent <tile>` sets the exposed tile for you or your opponent respectively. It also automatically removes that tile from the pool if present. Use `mine none` or `opponent none` when a player has no exposed tile. 

Once the free pool and at-risk player tiles are updated, use `start` to begin your turn. 
Roll the dice (in the real game) and then type `roll <faces>` to input the roll into the software. Allowed inputs are integers 1-5 for normal digits and a 6 for worms. After each roll, the program prints the EV of each legal face choice and recommends a face. It calculates the EV by simulating each choice and then checking every possible subsequent roll, its probability of occuring, and the net change in worms which occurs for each branch. 

Enter `pick <face>` to record your choice. After picking, the software compares the EV of stopping with the EV of rolling the remaining dice and
recommends an action. Enter the next `roll` or use `stop` if you decide not to roll. 

Use `status` to display the current game state and typing `help` lists all commands. 

After stopping or busting, update the free pool and exposed tiles as needed before
starting the next turn. 

*Note* After resolving a turn, the program reports its outcome but does not update the free pool or exposed tiles of the players. These should be updated using the above commands before entering the next turn. You can easily do this on your child's turn if you aren't busy consoling them, drying their tears, or mocking them for getting wrecked so hard. 

The original JSON request mode is also available. Send one request on standard
input:

```
@'
{
  "game_state": {
    "free_tiles": [21, 22, 23, 25, 26, 27, 28, 30, 31, 32, 33, 34, 35, 36],
    "opponent_top": 29,
    "own_top": 24
  },
  "kept_counts": [0, 0, 0, 0, 0, 0],
  "current_roll": [1, 2, 2, 3, 4, 5, 5, 6]
}
'@ | python rain_worms_ev.py
```

`kept_counts` lists the number of previously set-aside dice for faces 1–6. `current_roll` lists
the dice in the current roll, so its length must be eight minus the number
already kept. Use `null` for `opponent_top` or `own_top` if there is no tile.
`free_tiles` contains the tile values currently available in the pool.

The output gives each legal face choice's score, EV if stopping, EV if rolling
again, overall EV under the better of those two actions, and the recommended
next action. EV is net worms added to your stack: a pool tile is worth its
printed worm count; stealing is worth twice that count (gain plus opponent
loss); busting loses the worms on your exposed tile. If there is no exposed
tile, busting has value zero. A failed stop or a roll with no unused face is a
bust.

The recursive roll calculation enumerates every distinct dice-count outcome
and weights it by its exact multiplicity among the `6**n` ordered rolls.
Displayed EVs are floating-point values.

## Scope and limitations

This calculator only calculates optimal play for a single turn. This should not be mistaken for an AI which players optimally. For instance, if you are behind it is often necessary to take risks with lower EV but higher net worms (i.e. high risk, high reward strategies) in order to have a chance at coming back. These are decisions you have to make yourself. But the program does still offer the EV for each choice so you can decide if a suboptimal EV strategy (a hail mary) is necessary in a given situation. As another example, after a bust, the returned tile and flipped pool tile affect later turns, but those future-turn consequences are outside the scope of this calculator. 

Finally, the computed EV is based on a 2 player game which means the net worms computed for stealing the opponents exposed tile is double its face value. This makes stealing tiles a much more powerful strategy than it might be in a 3+ player game. As an example, suppose a 3 player game where you are player 2, player 1 is winning, and you have a choice between stealing the exposed tile of player 3 (worth 2 worms) or taking a tile from the free pool. The calculator will advise stealing in this case because of its limitation to 2 players. Obviously however you should take the 3 worm tile from the free pool instead. These are moments you have to notice yourself or if you are ambitious, modify the code to deal with multiple players. But this adds a great deal of complexity so I haven't done so. 

Enjoy the calculator and those tasty tasty kid tears!
