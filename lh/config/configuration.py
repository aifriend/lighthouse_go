import os
from typing import List, Tuple

import numpy as np

from lh.config.encoders import OneHotEncoder
from lib.utils import dotdict

# ####################################################################################
# ###################### INITIAL CONFIGS AND OUTPUTS #################################
# ####################################################################################

# specifically choose TF cpu if needed. This will have no effect if GPU is not present
USE_TF_CPU = True

# helper path so model weights are imported and exported correctly when transferring project
PATH = os.path.dirname(os.path.realpath(__file__))

# Show initial TF configuration when TF is getting initialized
SHOW_TENSORFLOW_GPU = False

# Disable TF warnings
DISABLE_TENSORFLOW_WARNING = True

# Show initial Pygame welcome message when Pygame is getting initialized
SHOW_PYGAME_WELCOME = False

# If keras should output while fitting data
VERBOSE_MODEL_FIT = 1  # 0 = silent, 1 = progress bar, 2 = one line per epoch.

# Maximum number of fps Pygame will render game at. Only relevant when running with verbose > 3
FPS = 1000

# ##################################
# ########### ENCODERS #############
# ##################################

# Defining number of encoders
NUM_ENCODERS = 11

# Setting indexes to each encoder
ISLAND_IDX = 0
P_NAME_IDX = 1
A_TYPE_IDX = 2
ENERGY_W1_IDX = 3
ENERGY_W2_IDX = 4
LH_ENERGY_IDX = 5
LH_OWNER_IDX = 6
LH_KEY_IDX = 7
LH_CONN_IDX = 8
LH_TRI_IDX = 9
TIME_IDX = 10

# ##################################
# ########### ACTORS ###############
# ##################################

# Dictionary for actors
d_a_type = dotdict({
    'Work': 1,  # work
    'Lighthouse': 2,  # lighthouse
})

# Reverse dictionary for actors
d_type_rev = dotdict({
    1: 'Work',
    2: 'Lighthouse',
})

# ##################################
# ########## ACTIONS ###############
# ##################################

# Dictionary for actions and which actor can execute them
d_acts = dotdict({
    1: ["pass", "up", "down", "right", "left", "upright", "upleft", "downright", "downleft", "attack", "connect"],
    # Work
    2: [],  # Lighthouse
})

# Reverse dictionary for actions
d_acts_int = dotdict({
    1: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # Work
    2: [],  # Lighthouse
})

# Defining all actions
ACTS = {
    "pass": 0,

    "up": 1,
    "down": 2,
    "right": 3,
    "left": 4,
    "upright": 5,
    "upleft": 6,
    "downright": 7,
    "downleft": 8,

    "attack10": 9,
    "attack30": 10,
    "attack60": 11,
    "attack80": 12,
    "attack100": 13,

    "connect0": 14,
    "connect1": 15,
    "connect2": 16,
    "connect3": 17,
    "connect4": 18,
}

# Reverse dictionary for all actions
ACTS_REV = {
    0: "pass",

    1: "up",
    2: "down",
    3: "right",
    4: "left",
    5: "upright",
    6: "upleft",
    7: "downright",
    8: "downleft",

    9: "attack10",
    10: "attack30",
    11: "attack60",
    12: "attack80",
    13: "attack100",

    14: "connect0",
    15: "connect1",
    16: "connect2",
    17: "connect3",
    18: "connect4",
}

# Count of all actions
NUM_ACTS = len(ACTS)

# ####################################################################################
# ################################## PLAYING #########################################
# ####################################################################################

# User shortcuts that player can use using Pygame
d_user_shortcuts = dotdict({
    ' ': 0,  # idle
    'w': 1,  # up
    's': 2,  # down
    'd': 3,  # right
    'a': 4,  # left
    'q': 5,  # mine_resources
    'e': 6,  # return_resources
    '1': 7,  # attack_up
    '2': 8,  # attack_down
    '3': 9,  # attack_right
    '4': 10,  # attack_left
    '6': 11,  # npc_up
    '7': 12,  # npc_down
    '8': 13,  # npc_right
    '9': 14,  # npc_left
    'f': 19,  # barracks_up
    'g': 20,  # barracks_down
    'h': 21,  # barracks_right
    'j': 22,  # barracks_left
    'b': 27,  # heal_up
    'n': 28,  # heal_down
    'm': 29,  # heal_right
    ',': 30,  # heal_left
})

# Reverse dictionary for user shortcuts
d_user_shortcuts_rev = dotdict({
    0: ' ',  # idle

    1: 'w',  # up
    2: 's',  # down
    3: 'd',  # right
    4: 'a',  # left

    5: 'q',  # mine_resources
    6: 'e',  # return_resources

    7: '1',  # attack_up
    8: '2',  # attack_down
    9: '3',  # attack_right
    10: '4',  # attack_left

    11: '6',  # npc_up
    12: '7',  # npc_down
    13: '8',  # npc_right
    14: '9',  # npc_left

    19: 'f',  # barracks_up
    20: 'g',  # barracks_down
    21: 'h',  # barracks_right
    22: 'j',  # barracks_left

    27: 'b',  # heal_up
    28: 'n',  # heal_down
    29: 'm',  # heal_right
    30: ',',  # heal_left
})

# Colors of actors displayed in Pygame
d_a_color = dotdict({
    1: (230, 0, 50),  # Gold : red
    2: (0, 165, 208),  # Work : blue
    3: (255, 156, 255),  # Barr : pink
})


# ###########################################################################
# ###################### MAIN CONFIGURATION #################################
# ###########################################################################


class Configuration:
    class _NNetArgs:
        def __init__(self,
                     lr,
                     dropout,
                     epochs,
                     batch_size,
                     cuda,
                     num_channels):
            self.lr = lr  # learning rate
            self.dropout = dropout
            self.epochs = epochs  # times training examples are iterated through learning process
            self.batch_size = batch_size  # how many train examples are taken together for learning
            self.cuda = cuda  # this is only relevant when using TF GPU
            self.num_channels = num_channels  # used by nnet conv layers
            self.encoder = OneHotEncoder()

    class _GameConfig:
        def __init__(self,
                     money_increment,
                     initial_gold,
                     maximum_gold,
                     sacrificial_heal,
                     heal_amount,
                     heal_cost,
                     damage,
                     destroy_all,
                     a_max_health,
                     a_cost,
                     acts_enabled,
                     score_function,
                     timeout):
            self.encoder = OneHotEncoder()

            # ##################################
            # ############# GOLD ###############
            # ##################################

            # how much money is returned when returned resources
            self.MONEY_INC = money_increment

            # how much initial gold do players get at game begining
            self.INITIAL_GOLD = initial_gold

            # Maximum gold that players can have - It is limited to 8 bits for one-hot onehot_encoder
            self.MAX_GOLD = maximum_gold

            # ##################################
            # ############# HEAL ###############
            # ##################################

            # Game mechanic where actors can damage themselves to heal friendly unit. This is only used when player doesn't have any money to pay for heal action
            self.SACRIFICIAL_HEAL = sacrificial_heal

            # How much friendly unit is healed when executing heal action
            self.HEAL_AMOUNT = heal_amount
            # how much money should player pay when heal action is getting executed.

            self.HEAL_COST = heal_cost

            # ##################################
            # ########### TIMEOUT ##############
            # ##################################

            # If timeout should be used. This causes game to finish after TIMEOUT number of actions.
            # Check if timeout is being used. Alternatively Kill function is used
            # how many turns until game end - this gets reduced when each turn is executed
            self.TIMEOUT = timeout

            # ##################################
            # ########## ATTACKING #############
            # ##################################

            # how much damage is dealt to attacked actor
            self.DAMAGE = damage

            # when attacking, all enemy units are destroyed, resulting in victory for the attacking player
            if destroy_all:
                self.DAMAGE = 10000

            # Maximum health that actor can have - this is also initial health that actor has.
            self.a_max_health = dotdict(a_max_health or {
                1: 10,  # Gold
                2: 10,  # Work
                3: 20,  # Barr
            })

            # Cost of actor to produce (key - actor type, value - number of gold coins to pay)
            self.a_cost = dotdict(a_cost or {
                1: 0,  # Gold
                2: 1,  # Work
                3: 4,  # Barr
            })

            self.acts_enabled = dotdict(acts_enabled or {
                "pass": True,
                "up": True,
                "down": True,
                "right": True,
                "left": True,
                "upright": True,
                "upleft": True,
                "downright": True,
                "downleft": True,
                "attack": True,
                "connect": True
            })

            self.score_function = score_function

    class _PitArgs:
        def __init__(self,
                     player1_type,
                     player2_type,
                     player1_config,
                     player2_config,
                     player1_model_file,
                     player2_model_file,
                     num_games):

            self.player1_type = player1_type
            self.player2_type = player2_type
            self.player1_model_file = player1_model_file
            self.player2_model_file = player2_model_file
            self.player1_config = player1_config or {'numMCTSSims': 2, 'cpuct': 1.0}
            self.player2_config = player2_config or {'numMCTSSims': 2, 'cpuct': 1.0}
            self.num_games = num_games

        def create_players(self, game):
            return self._create_player(game, self.player1_type, self.player1_config,
                                       self.player1_model_file), self._create_player(game, self.player1_type,
                                                                                     self.player1_config,
                                                                                     self.player2_model_file)

        def _create_player(self,
                           game,
                           player_type: str,
                           player_config: dict,
                           player_model_file: str):
            from lh.LHPlayers import RandomPlayer, GreedyLHPlayer, HumanLHPlayer

            if player_type == 'nnet':
                if player_config is None:
                    print("Invalid pit configuration. Returning")
                    exit(1)
                return self._PitNNetPlayer(game, player_config, player_model_file).play
            if player_type == 'random':
                return RandomPlayer(game).play
            if player_type == 'greedy':
                return GreedyLHPlayer(game).play
            if player_type == 'human':
                return HumanLHPlayer(game).play
            print("Invalid player type. Returning")
            exit(1)

        class _PitNNetPlayer:
            def __init__(self,
                         g,
                         player_config,
                         player_model_file):
                from lh.keras.NNet import NNetWrapper as NNet
                from lib.MCTS import MCTS

                n1 = NNet(g, OneHotEncoder())
                n1.load_checkpoint('temp/', player_model_file)
                args1 = dotdict(player_config or {'numMCTSSims': 2, 'cpuct': 1.0})
                mcts1 = MCTS(g, n1, args1)
                self.play = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

    class _LearnArgs:
        def __init__(self,
                     num_iters,
                     num_eps,
                     temp_threshold,
                     update_threshold,
                     maxlen_of_queue,
                     num_mcts_sims,
                     arena_compare,
                     cpuct,
                     checkpoint,
                     load_model,
                     load_folder_file,
                     num_iters_for_train_examples_history,
                     save_train_examples,
                     load_train_examples):
            self.numIters = num_iters  # total number of games played from start to finish is numIters * numEps
            self.numEps = num_eps  # How may game is played in this episode
            self.tempThreshold = temp_threshold
            self.updateThreshold = update_threshold  # Percentage that new model has to surpass by win rate to replace old model
            self.maxlenOfQueue = maxlen_of_queue
            self.numMCTSSims = num_mcts_sims  # How many MCTS tree searches are performing (mind that this MCTS doesnt use simulations)
            self.arenaCompare = arena_compare  # How many comparisons are made between old and new model
            self.cpuct = cpuct  # search parameter for MCTS

            self.checkpoint = checkpoint
            self.load_model = load_model  # Load training examples from file - WARNING - this is disabled in LHPlayers.py because of memory errors received when loading data from file
            self.load_folder_file = load_folder_file
            self.numItersForTrainExamplesHistory = num_iters_for_train_examples_history  # maximum number of 'iterations' that game episodes are kept in queue. After that last is popped and new one is added.

            self.save_train_examples = save_train_examples
            self.load_train_examples = load_train_examples

    class BoardTile:
        def __init__(self,
                     player: int,
                     x: int,
                     y: int,
                     a_type: str):
            self.player = player
            self.x = x
            self.y = y
            self.a_type = a_type  # 'Gold'...

    def __init__(self,
                 learn_visibility=0,
                 pit_visibility=4,

                 money_increment_player1: int = 3,
                 initial_gold_player1: int = 1,
                 maximum_gold_player1: int = 255,
                 sacrificial_heal_player1: bool = False,
                 heal_amount_player1: int = 5,
                 heal_cost_player1: int = 1,
                 damage_player1: int = 20,
                 destroy_all_player1: bool = False,
                 a_max_health_player1: dict = None,
                 a_cost_player1: dict = None,
                 acts_enabled_player1: dict = None,
                 score_function_player1: int = 3,
                 timeout_player1: int = 200,
                 player1_model_file: str = "best_player1.pth.tar",

                 money_increment_player2: int = 3,
                 initial_gold_player2: int = 1,
                 maximum_gold_player2: int = 255,
                 sacrificial_heal_player2: bool = False,
                 heal_amount_player2: int = 5,
                 heal_cost_player2: int = 1,
                 damage_player2: int = 20,
                 destroy_all_player2: bool = False,
                 a_max_health_player2: dict = None,
                 a_cost_player2: dict = None,
                 acts_enabled_player2: dict = None,
                 score_function_player2: int = 3,
                 timeout_player2: int = 200,
                 player2_model_file: str = "best_player2.pth.tar",

                 num_iters: int = 4,
                 num_eps: int = 4,
                 temp_threshold: int = 15,
                 update_threshold: float = 0.6,
                 maxlen_of_queue: int = 6400,
                 num_mcts_sims: int = 10,
                 arena_compare: int = 10,
                 cpuct: float = 1,
                 checkpoint: str = 'temp/',
                 load_model: bool = False,
                 load_folder_file: Tuple[str, str] = ('temp/', 'checkpoint_0.pth.tar'),
                 num_iters_for_train_examples_history: int = 8,
                 save_train_examples: bool = False,
                 load_train_examples: bool = False,

                 player1_type: str = 'nnet',
                 player2_type: str = 'nnet',
                 player1_config: dict = None,
                 player2_config: dict = None,
                 num_games: int = 4,

                 lr: float = 0.01,
                 dropout: float = 0.3,
                 epochs: int = 30,
                 batch_size: int = 256,
                 cuda: bool = True,
                 num_channels: int = 128,

                 initial_board_config: List[BoardTile] = None):
        """
        :param learn_visibility: How much console should output while running learn. If visibility.verbose > 3, Pygame is shown
        :param pit_visibility: How much console should output while running pit. If visibility.verbose > 3, Pygame is shown
        :param board_config_file: Board configuration from file

        :param money_increment_player1: How much money player should gain when worker returns gold coins
        :param initial_gold_player1: How much initial gold should player have
        :param maximum_gold_player1: Maximum gold for player (max allowed value is 255)
        :param sacrificial_heal_player1: If actors can sacrifice their health to heal other actors if player doesn't have enough gold
        :param heal_amount_player1: how much should action 'heal' heal other actor
        :param heal_cost_player1: how much should action 'heal' cost gold coins. If sacrificial_heal is enabled, this is the amount that actors health will be reduced if player doesn't have enough gold
        :param damage_player1: How much damage is inflicted upon action 'attack' on other actor
        :param destroy_all_player1: If by executing action 'attack', all opponents actors are destroyed
        :param a_max_health_player1: dictionary of maximum amount of healths for each actor. See its default values to override
            ``
            Example: {
                1: 10,  # Gold
                2: 10,  # Work
                3: 20,  # Barr
            }
            ``
        :param a_cost_player1: dictionary of costs for each actor. See its default values to override
            ``
            Example: {
                1: 0,  # Gold
                2: 1,  # Work
                3: 4,  # Barr
            }
            ``
        :param acts_enabled_player1: dictionary of which actions are enabled for player. See its default values to override.
            ``
            Example: {
                "idle": False,
                "up": True,
                "down": True,
                "right": True,
                "left": True,
                "mine_resources": True,
                "return_resources": True,
                "attack": True,
                "npc": True,
                "barracks": True,
                "heal": True
            }
            ``
        :param score_function_player1: which function to use (1, 2 or 3)
        :param timeout_player1: After what time game will timeout if 'useTimeout' is set to true
        :param player1_model_file: Filename in temp folder that player 1 nnet player uses

        :param money_increment_player2: How much money player should gain when worker returns gold coins
        :param initial_gold_player2: How much initial gold should player have
        :param maximum_gold_player2: Maximum gold for player (max allowed value is 255)
        :param sacrificial_heal_player2: If actors can sacrifice their health to heal other actors if player doesn't have enough gold
        :param heal_amount_player2: how much should action 'heal' heal other actor
        :param heal_cost_player2: how much should action 'heal' cost gold coins. If sacrificial_heal is enabled, this is the amount that actors health will be reduced if player doesn't have enough gold
        :param damage_player2: How much damage is inflicted upon action 'attack' on other actor
        :param destroy_all_player2: If by executing action 'attack', all opponents actors are destroyed
        :param a_max_health_player2: dictionary of maximum amout of healths for each actor. See its default values to override
            ``
            Example: {
                1: 10,  # Gold
                2: 10,  # Work
                3: 20,  # Barr
            }
            ``
        :param a_cost_player2: dictionary of costs for each actor. See its default values to override
            ``
            Example: {
                1: 0,  # Gold
                2: 1,  # Work
                3: 4,  # Barr
            }
            ``
        :param acts_enabled_player2: dictionary of which actions are enabled for player. See its default values to override
            ``
            Example: {
                "idle": False,
                "up": True,
                "down": True,
                "right": True,
                "left": True,
                "mine_resources": True,
                "return_resources": True,
                "attack": True,
                "npc": True,
                "barracks": True,
                "heal": True
            }
            ``
        :param score_function_player2: which function to use (1, 2 or 3)
        :param timeout_player2: After what time game will timeout if 'useTimeout' is set to true
        :param player2_model_file: Filename in temp folder that player 2 nnet player uses


        :param num_iters: How many iterations of games it should be played
        :param num_eps: How many episodes in each game iteration it should be played
        :param temp_threshold: Used by coach. "It uses a temp=1 if episodeStep < tempThreshold, and thereafter uses temp=0."
        :param update_threshold: Percentage of how much wins should newer model have to be accepted
        :param maxlen_of_queue: How many train examples can be stored in each iteration
        :param num_mcts_sims: How many MCTS sims are executed in each game episode while learning
        :param arena_compare: How many comparations of newer and older model should be made before evaluating which is better
        :param cpuct: Exploration parameter for MCTS
        :param checkpoint: folder where checkpoints should be saved while learning
        :param load_model: If model is loaded from checkpoint on learning start
        :param load_folder_file: tuple(folder, file) where model is loaded from
        :param num_iters_for_train_examples_history: How many iterations of train examples should be kept for learning. If this number is exceeded, oldest iteration of train exaples is removed from queue
        :param save_train_examples: If train examples should be saved to file (Caution if choosing this, because of memory error)
        :param load_train_examples: If train examples should be loaded from file (Caution if choosing this, because of memory error)

        :param player1_type: What type should player 1 be ("nnet", "random", "greedy", "human")
        :param player2_type: What type should player 2 be ("nnet", "random", "greedy", "human")
        :param player1_config: If "nnet" player is chosen, config can be provided {'numMCTSSims': 2, 'cpuct': 1.0}
        :param player2_config: If "nnet" player is chosen, config can be provided {'numMCTSSims': 2, 'cpuct': 1.0}
        :param num_games: How many games should be played for pit config

        :param lr: Learning rate of model
        :param dropout: Dropout in NNet Model config
        :param epochs: How many epochs should learning take
        :param batch_size: How big batches of learning examples there should be while learning
        :param cuda: Whether to use cuda if tensorflow gpu is installed and GPU supports cuda operations
        :param num_channels: Number of channels in NNet Model config

        :param initial_board_config: Configuration of initial non-empty tiles for actors. See its default values to override.
            ``Example: initial_board_config=[
                Configuration.BoardTile(1,4,4,'Gold'),
                Configuration.BoardTile(-1,4,5,'Gold'),
            ``
        """

        # output for game stats during playing games (game_episode, game iteration, player name, action executed, action_name, action_direction, player_score...
        self.config_file_pit = "temp/config_pit.csv"
        self.config_file_learn = "temp/config_learn.csv"

        self.board_file_path = "maps/island.txt"

        self.visibility = 4
        self._pit_visibility = pit_visibility
        self._learn_visibility = learn_visibility

        self.player1_config = self._GameConfig(
            money_increment=money_increment_player1,
            initial_gold=initial_gold_player1,
            maximum_gold=maximum_gold_player1,
            sacrificial_heal=sacrificial_heal_player1,
            heal_amount=heal_amount_player1,
            heal_cost=heal_cost_player1,
            damage=damage_player1,
            destroy_all=destroy_all_player1,
            a_max_health=a_max_health_player1,
            a_cost=a_cost_player1,
            acts_enabled=acts_enabled_player1,
            score_function=score_function_player1,
            timeout=timeout_player1)

        self.player2_config = self._GameConfig(
            money_increment=money_increment_player2,
            initial_gold=initial_gold_player2,
            maximum_gold=maximum_gold_player2,
            sacrificial_heal=sacrificial_heal_player2,
            heal_amount=heal_amount_player2,
            heal_cost=heal_cost_player2,
            damage=damage_player2,
            destroy_all=destroy_all_player2,
            a_max_health=a_max_health_player2,
            a_cost=a_cost_player2,
            acts_enabled=acts_enabled_player2,
            score_function=score_function_player2,
            timeout=timeout_player2)

        self.learn_args = self._LearnArgs(
            num_iters=num_iters,
            num_eps=num_eps,
            temp_threshold=temp_threshold,
            update_threshold=update_threshold,
            maxlen_of_queue=maxlen_of_queue,
            num_mcts_sims=num_mcts_sims,
            arena_compare=arena_compare,
            cpuct=cpuct,
            checkpoint=checkpoint,
            load_model=load_model,
            load_folder_file=load_folder_file,
            num_iters_for_train_examples_history=num_iters_for_train_examples_history,
            save_train_examples=save_train_examples,
            load_train_examples=load_train_examples)

        self.pit_args = self._PitArgs(
            player1_type=player1_type,
            player2_type=player2_type,
            player1_config=player1_config,
            player2_config=player2_config,
            player1_model_file=player1_model_file,
            player2_model_file=player2_model_file,
            num_games=num_games
        )

        self.nnet_args = self._NNetArgs(
            lr=lr,
            dropout=dropout,
            epochs=epochs,
            batch_size=batch_size,
            cuda=cuda,
            num_channels=num_channels
        )

        if initial_board_config:
            self.initial_board_config = []
            for board_tile in initial_board_config:
                self.initial_board_config.append(dotdict({
                    'x': board_tile.x,
                    'y': board_tile.y,
                    'player': board_tile.player,
                    'a_type': d_a_type[board_tile.a_type],
                    'health': self.player1_config.a_max_health[
                        d_a_type[board_tile.a_type]] if board_tile.player == 1 else self.player2_config.a_max_health[
                        d_a_type[board_tile.a_type]],
                    'carry': 0,
                    'gold': self.player1_config.INITIAL_GOLD if board_tile.player == 1 else self.player2_config.INITIAL_GOLD,
                    'timeout': self.player1_config.TIMEOUT if board_tile.player == 1 else self.player2_config.TIMEOUT
                }))
        else:
            self.initial_board_config = initial_board_config or [
                dotdict({
                    'x': int(self.grid_size / 2) - 1,
                    'y': int(self.grid_size / 2),
                    'player': 1,
                    'a_type': d_a_type['Gold'],
                    'health': self.player1_config.a_max_health[d_a_type['Gold']],
                    'carry': 0,
                    'gold': self.player1_config.INITIAL_GOLD,
                    'timeout': self.player1_config.TIMEOUT
                }),
                dotdict({
                    'x': int(self.grid_size / 2),
                    'y': int(self.grid_size / 2),
                    'player': -1,
                    'a_type': d_a_type['Gold'],
                    'health': self.player2_config.a_max_health[d_a_type['Gold']],
                    'carry': 0,
                    'gold': self.player2_config.INITIAL_GOLD,
                    'timeout': self.player2_config.TIMEOUT
                }),
            ]

    def set_runner(self, runner: str):
        if runner == 'pit':
            self.visibility = self._pit_visibility
        elif runner == 'learn':
            self.visibility = self._learn_visibility
        else:
            print("Unrecognised runner. Returning")
            exit(1)

    def set_board(self, path_to_board=None):
        self.board_file_path = path_to_board
