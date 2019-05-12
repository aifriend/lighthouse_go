"""
Teaches neural network playing of specified game configuration using self play
This configuration needs to be kept seperate, as different nnet and game configs are set

"""

from lib.Coach import Coach
from rts.NNet import NNetWrapper as Nnm
# from rts.configurations.ConfigWrapper import LearnArgs
from rts.RTSGame import RTSGame as Game
from rts.config.config import CONFIG

if __name__ == "__main__":

    CONFIG.set_runner('learn')  # set visibility as learn

    # create nnet for this game
    g = Game()
    nnet = Nnm(g, CONFIG.nnet_args.encoder)

    # If training examples should be loaded from file
    if CONFIG.learn_args.load_model:
        nnet.load_checkpoint(CONFIG.learn_args.load_folder_file[0], CONFIG.learn_args.load_folder_file[1])

    # Create coach instance that starts teaching nnet on newly created game using self-play
    c = Coach(g, nnet, CONFIG.learn_args)
    if CONFIG.learn_args.load_model:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
