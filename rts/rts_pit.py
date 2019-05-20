"""
Compares 2 players against each other and outputs num wins p1/ num wins p2/ draws

"""

from lib import Arena
from rts.RTSGame import RTSGame
from rts.RTSView import RTSView
from rts.config.config import CONFIG

CONFIG.set_runner('pit')  # set visibility as pit

g = RTSGame()
v = RTSView(g)

player1, player2 = CONFIG.pit_args.create_players(g)

arena = Arena.Arena(player1, player2, g, v)
print(arena.playGames(CONFIG.pit_args.num_games, verbose=CONFIG.visibility))
