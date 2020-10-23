from lib.Coach import Coach
from lib.utils import dotdict
from tictactoe.NNet import NNetWrapper as nnw
from tictactoe.TicTacToeGame import TicTacToeGame as Game

args = dotdict({
    'numIters': 1000,
    'numEps': 10,
    'tempThreshold': 15,
    'updateThreshold': 0.6,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 25,
    'arenaCompare': 40,
    'cpuct': 1,
    'checkpoint': 'temp/',
    'load_model': False,
    'load_folder_file': ('tictactoe/pretrained_models', 'best_model.pth.tar'),
    'numItersForTrainExamplesHistory': 20,
})

if __name__ == "__main__":
    g = Game()
    nnet = nnw(g)

    if args.load_model:
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])

    c = Coach(g, nnet, args)
    if args.load_model:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    c.learn()
