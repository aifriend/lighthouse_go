from lighthouses_aicontest.gamer.p_lightgo.lightgo import LightGo
from lighthouses_aicontest.gamer.p_pegasus.pegasus import Pegasus
from lighthouses_aicontest.gamer.p_random.randbot import RandBot
from lighthouses_aicontest.nengine.botplayer import BotPlayer
from lighthouses_aicontest.nengine.config import GameConfig
from lighthouses_aicontest.nengine.game import Game
from lighthouses_aicontest.nengine.view import GameView

cfg_file = "lighthouses_aicontest/maps/island.txt"
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
