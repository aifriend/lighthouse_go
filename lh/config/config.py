from lh.config.LHConfig import LHConfig

# ############################### Basic config #####################################
# CONFIG = Configuration()

# ###########################   Example learning   #################################
CONFIG = LHConfig(board_file_path=('./config/maps/', 'island.txt'),
                  num_iters=5,  # iteration of episodes
                  num_mcts_sims=15,  # MCTS open nodes
                  num_eps=3,  # episode of self-playing game
                  epochs=100,  # complete whole dataset (in batches) for nnet to learn
                  cpuct=1.0,  # exploration MCTS parameter
                  temp_threshold=200,
                  timeout_player=200,
                  arena_compare=4,
                  num_iters_for_train_examples_history=3,
                  update_threshold=8,
                  load_train_examples=False,
                  load_train_folder_file=('./temp/', 'checkpoint_train_'),
                  load_model=False,
                  load_model_folder_file=('./temp/', 'best.pth.tar'))

# ###########################   Learning Pit   #################################
"""
CONFIG = LHConfig(timeout_player=200,
                  num_games=2,  # even
                  num_iters_for_train_examples_history=3,
                  player1_type='human',
                  player2_type='random')

CONFIG = LHConfig(timeout_player=200,
                  num_games=2,  # even
                  num_iters_for_train_examples_history=3,
                  player1_type='human',
                  player2_type='nnet',
                  player2_config={'numMCTSSims': 5, 'cpuct': 2.0},
                  player2_model_file='best.pth.tar')
"""
# ################################### Run 1 #########################################
"""
CONFIG = Configuration(num_iters=100,
                       num_iters_for_train_examples_history=30,
                       num_eps=4,
                       num_mcts_sims=5,
                       arena_compare=7,
                       epochs=10,
                       initial_gold_player1=10,
                       initial_gold_player2=10)
"""
# Description
"""
* Num iterations: Increased to 100, so graphing can be done correctly and multiple comparisons between models are done.
* Train examples history: Increased to 30, because of high number of iterations. After 30 iterations, learning process 
becomes quite slow but efficient
* Num eps: Decreased to 4, so multiple iterations can be triggered faster
* Num mcts sims: Decreased to 5, because game is not played to end, it doesnt really contribute that much
* Arena compare: 7 so comparisons between old and new model are quick but not resulting in overwriting better model
* Epochs: Increased to 100, because of GPU, where learning is done relatively fast even with such a number
* Initial gold: Increased for both players to 10. This is most important parameter change here, because it gives players 
enough money to start constructing different actors, which results in non-tie games and forces players to keep creating 
new actors.
"""
# Results
"""
Workers are very frequently gathering gold when near that actor. 
Random movement has been greatly decreased over learning period, resulting in less time wasted.
Hunting for enemy actors doesn't occur, where player would try to annihilate enemy player.
Players mostly gather gold and construct new actors with occasional attacks.
"""

# ###################### Pit with different board setup ##############################
"""
CONFIG = Configuration(num_iters=100,
                       num_iters_for_train_examples_history=30,
                       num_eps=4,
                       num_mcts_sims=5,
                       arena_compare=7,
                       epochs=100,
                       player1_type='random',
                       player2_type='random')
"""
# Description
"""
Initial board config
"""
# Results
"""
Players start game by constructing as much actors as they can with provided gold.
Players continue to successfully gather gold when they get near gold minerals, but randomly walk around when they are not.
Attacking units continue to damage and destroy enemy units when nearby, but attacks on enemy base are not initiated, 
resulting in annihilation
"""
