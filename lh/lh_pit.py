"""
Compares 2 players against each other and outputs num wins p1/ num wins p2/ draws

"""
from lh.LHGame import LHGame
from lh.LHView import LHView
from lh.config.config import CONFIG
from lib import Arena

CONFIG.set_runner('pit')

g = LHGame()
v = LHView(g)

player1, player2 = CONFIG.pit_args.create_players(g)

arena = Arena.Arena(player1, player2, g, CONFIG.learn_args, v)
results = arena.playRecordGames(CONFIG.pit_args.num_games, verbose=CONFIG.visibility)
print("Final arena ranking: ([1]=>%d, [-1]=>%d, [0]=>%d)" % results)
