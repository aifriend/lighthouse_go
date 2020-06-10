from engine.botplayer import BotPlayer
from engine.config import GameConfig
from engine.game import Game
from engine.view import GameView
from gamer.p_lightgo.lightgo import LightGo
from aicontest_go.gamer.p_pegasus.pegasus import Pegasus
from aicontest_go.gamer.p_random.randbot import RandBot

cfg_file = "maps/island.txt"
bots = [0, 1, 2]
DEBUG = False

config = GameConfig(cfg_file)
game = Game(config, len(bots))

actors = [
    BotPlayer(game, 0, RandBot(), debug=DEBUG),
    BotPlayer(game, 1, LightGo(), debug=DEBUG),
    BotPlayer(game, 2, Pegasus(), debug=DEBUG)
]
for actor in actors:
    actor.initialize()

view = GameView(game)

coach = 0
while True:
    if view.closeEvent():
        break
    game.pre_round()
    view.update()
    for gamer in actors:
        gamer.turn()
        view.update()
    game.post_round()
    score = ""
    for i in range(len(bots)):
        score += "P%d: %d " % (i, game.players[i].score)
    print("########### ROUND %d SCORE: %s" % (coach, score))
    coach += 1

view.update()
