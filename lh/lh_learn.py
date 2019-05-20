"""
Teaches neural network playing of specified game configuration using self play
This configuration needs to be kept seperate, as different nnet and game configs are set

"""
import sys

import pygame

from lh.LHGame import LHGame
from lh.config.config import CONFIG
from lh.config.gameconfig import GameConfig
from lh.gamer.lightgo import LightGo
from lh.keras.NNet import NNetWrapper
from lh.logic.botplayer import BotPlayer, Board
from lib.Coach import Coach

if __name__ == "__main__":

    #################### CONFIG LG ###################
    cfg_file = "lh/config/maps/island.txt"
    DEBUG = False
    # Load board
    config = GameConfig(cfg_file)
    board = Board(config, 1)  # Board
    botPlayer = BotPlayer(board, 0, LightGo(), debug=DEBUG)  # Actor

    #################### CONFIG NN ###################
    # Set visibility as learn
    CONFIG.set_runner('learn')
    # Create nnet for this game
    g = LHGame()
    # botPlayer.init_player()  # Initialize
    # botPlayer.turn_by_player()  # GameConfig?  # Turn

    ##################### ROUND #####################
    # Create network
    nnet = NNetWrapper(g, CONFIG.nnet_args.encoder)
    # If training examples should be loaded from file
    if CONFIG.learn_args.load_model:
        nnet.load_checkpoint(CONFIG.learn_args.load_folder_file[0], CONFIG.learn_args.load_folder_file[1])
    # Create coach instance that starts teaching nnet on newly created game using self-play
    c = Coach(g, nnet, CONFIG.learn_args)
    if CONFIG.learn_args.load_train_examples:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()

    ##################### SCORE LG ####################
    # Score
    score = "P%d: %d " % (0, game.players[0].score)
    print("SCORE: %s" % score)

    # Wait to close
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
