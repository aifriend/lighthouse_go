"""
NNet wrapper uses defined nnet model to train and predict

"""

import os

import numpy as np

from lh.config.configuration import Configuration
from lh.keras.LHNNet import LHNNet
from lib.NeuralNet import NeuralNet


class NNetWrapper(NeuralNet):

    def __init__(self, game, config):
        """
        Creates nnet wrapper with game configuration and encoder
        :param game: game
        :param config: configuration
        """
        # default
        super().__init__()
        self.config = config
        self.encoder = self.config.nnet_args.encoder  # encoded that will be used for training and later predictions
        self.nnet = LHNNet(game, self.encoder, self.config)

    def train(self, examples):
        """
        Encodes examples using one of 2 encoders and starts fitting.
        :param examples: list of examples, each example is of form (board, pi, v)
        """
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)

        """
        input_boards = CONFIG.nnet_args.encoder.encode_multiple(input_boards)
        """
        input_boards = self.encoder.encode_multiple(input_boards)

        self.nnet.model.fit(x=input_boards, y=[target_pis, target_vs], batch_size=self.config.nnet_args.batch_size,
                            epochs=self.config.nnet_args.epochs, verbose=Configuration.VERBOSE_MODEL_FIT)

    def predict(self, board, player=None):
        """
        Predicts action.
        It encodes board with encoder, that has been used for learning.

        :param board: specific board
        :param player: specific player
        :return: vector of predicted actions and win prediction (Pi, V)
        """
        board = self.encoder.encode(board)

        # preparing input
        board = board[np.newaxis, :, :]

        # run
        pi, v = self.nnet.model.predict(board)
        return pi[0], v[0]

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Saving checkpoint... ")
        self.nnet.model.save_weights(filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        print("Loading checkpoint... ")
        self.nnet.model.load_weights(filepath)
