"""
Defined NNet model used for game TD2020

"""

import os

from tensorflow.python.keras import Input, Model
from tensorflow.python.keras.layers import Conv2D, BatchNormalization, Activation, Dense, Dropout, Flatten, Reshape
from tensorflow.python.keras.optimizers import Adam

from lh.config.config import CONFIG
from lh.config.configuration import Configuration

if Configuration.USE_TF_CPU:
    print("Using TensorFlow CPU")
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
if not Configuration.SHOW_TENSORFLOW_GPU:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
elif Configuration.DISABLE_TENSORFLOW_WARNING:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class LHNNet:
    def __init__(self, game, encoder):
        """
        NNet model, copied from Othello NNet, with reduced fully connected layers fc1 and fc2 and reduced nnet_args.num_channels
        :param game: game configuration
        :param encoder: Encoder, used to encode game boards
        """

        # game params
        self.board_x, self.board_y, _ = game.getBoardSize()
        self.num_encoders = encoder.num_encoders
        self.action_size = game.getActionSize()

        self.model = self._h4()

    def _h4(self):
        # Neural Net
        input_boards = Input(
            shape=(self.board_x, self.board_y, self.num_encoders))  # s: batch_size x board_x x board_y x num_encoders

        x_board = Reshape((self.board_x, self.board_y, self.num_encoders))(
            input_boards)  # batch_size  x board_x x board_y x num_encoders

        h_conv1 = Activation('relu')(BatchNormalization(axis=3)(
            Conv2D(CONFIG.nnet_args.num_channels, (3, 3), padding='same', use_bias=False)(
                x_board)))  # batch_size  x board_x x board_y x num_channels

        h_conv2 = Activation('relu')(BatchNormalization(axis=3)(
            Conv2D(CONFIG.nnet_args.num_channels, (3, 3), padding='same', use_bias=False)(
                h_conv1)))  # batch_size  x board_x x board_y x num_channels

        h_conv3 = Activation('relu')(BatchNormalization(axis=3)(
            Conv2D(CONFIG.nnet_args.num_channels, (3, 3), padding='valid', use_bias=False)(
                h_conv2)))  # batch_size  x (board_x-2) x (board_y-2) x num_channels

        h_conv4_flat = Flatten()(h_conv3)

        s_fc1 = Dropout(CONFIG.nnet_args.dropout)(Activation('relu')(BatchNormalization(axis=1)(
            Dense(256, use_bias=False)(h_conv4_flat))))  # batch_size x 1024

        s_fc2 = Dropout(CONFIG.nnet_args.dropout)(Activation('relu')(BatchNormalization(axis=1)(
            Dense(128, use_bias=False)(s_fc1))))  # batch_size x 1024

        pi = Dense(self.action_size, activation='softmax', name='pi')(s_fc2)  # batch_size x self.action_size
        v = Dense(1, activation='tanh', name='v')(s_fc2)  # batch_size x 1

        model = Model(inputs=input_boards, outputs=[pi, v])
        model.compile(loss=['categorical_crossentropy', 'mean_squared_error'], optimizer=Adam(CONFIG.nnet_args.lr))

        return model
