from lh.LHGame import LHGame
from lh.LHView import LHView
from lh.config.config import CONFIG_LEARN as CONFIG
from lh.keras.NNet import NNetWrapper
from lib.Coach import Coach

if __name__ == "__main__":
    """
    Teaches neural network playing of specified game configuration using self play
    This configuration needs to be kept seperate, as different nnet and game configs are set

    """
    CONFIG.set_runner('learn')

    # Create nnet for this game
    g = LHGame(CONFIG)
    v = LHView(g, CONFIG)

    # Create network
    nnet = NNetWrapper(g, CONFIG)

    # If training examples should be loaded from file
    if CONFIG.learn_args.load_model:
        print("Loading model...")
        nnet.load_checkpoint(CONFIG.learn_args.load_model_folder_file[0], CONFIG.learn_args.load_model_folder_file[1])

    # Create coach instance that starts teaching nnet on newly created game using self-play
    c = Coach(g, nnet, CONFIG, v)
    if CONFIG.learn_args.load_train_examples:
        print("Loading trainExamples from file...")
        c.loadTrainExamples(1)
    c.learn()
