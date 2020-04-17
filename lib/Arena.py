import os
import time
from collections import deque
from pickle import Pickler

import numpy as np

from lib.progress.average import AverageMeter
from lib.progress.bar import ShadyBar


class Arena:
    """
    An Arena class where any 2 agents can be pit against each other.
    """

    def __init__(self, player1, player2, game, args, view=None):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            args: learning configuration
            view: a function that takes board as input and prints it. Is necessary for verbose mode.
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.args = args
        self.view = view

    def playGame(self, verbose=False, pit=False):
        """
        Executes one episode of a game.

        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """
        train_examples = []
        players = [self.player2, None, self.player1]
        cur_player = 1
        board = self.game.getInitBoard()
        if verbose:
            assert self.view
            self.view.initView(board)

        it = 0
        while self.game.getGameEnded(board, cur_player) == 0:
            it += 1
            if verbose:
                assert self.view
                self.view.display(board)

            action = players[cur_player + 1](self.game.getCanonicalForm(board, cur_player))
            valids = self.game.getValidMoves(self.game.getCanonicalForm(board, cur_player), 1)
            if valids[action] == 0:
                print(action)
                assert valids[action] > 0

            if pit:
                sum_valids = np.sum(valids) + 1
                if sum_valids > 0:
                    valids = list(map(lambda a: a / sum_valids, valids))
                    valids[action] += 1 / sum_valids
                    if np.sum(valids) == 1:
                        sym = self.game.getSymmetries(self.game.getCanonicalForm(board, cur_player), valids)
                        for b, p in sym:
                            train_examples.append([b, cur_player, p, None])

            board, cur_player = self.game.getNextState(board, cur_player, action)

        if verbose:
            assert self.view
            self.view.display(board)

        r = self.game.getGameEnded(board, 1)
        if pit:
            return r, [(x[0], x[2], r * ((-1) ** (x[1] != cur_player))) for x in train_examples]
        else:
            return r

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """
        eps_time = AverageMeter()
        bar = ShadyBar('Arena.playGames', max=num)
        end = time.time()
        eps = 0
        maxeps = int(num)

        num = int(round(num / 2))
        oneWon = 0
        twoWon = 0
        draws = 0
        for _ in range(num):
            game_result = self.playGame(verbose=verbose)
            if game_result == 1:
                oneWon += 1
            elif game_result == -1:
                twoWon += 1
            else:
                draws += 1
            # bookkeeping + plot progress
            eps += 1
            eps_time.update(time.time() - end)
            end = time.time()
            bar.suffix = 'P1/P2 ({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:} | RET: {ret:})' \
                .format(eps=eps, maxeps=maxeps, et=eps_time.avg, total=bar.elapsed_td, eta=bar.eta_td, ret=game_result)
            bar.next()

        self.player1, self.player2 = self.player2, self.player1

        for _ in range(num):
            game_result = self.playGame(verbose=verbose)
            if game_result == -1:
                oneWon += 1
            elif game_result == 1:
                twoWon += 1
            else:
                draws += 1
            # bookkeeping + plot progress
            eps += 1
            eps_time.update(time.time() - end)
            end = time.time()
            bar.suffix = 'P2/P1 ({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:} | RET: {ret:})' \
                .format(eps=eps, maxeps=maxeps, et=eps_time.avg, total=bar.elapsed_td, eta=bar.eta_td, ret=game_result)
            bar.next()

        bar.finish()

        return oneWon, twoWon, draws

    def playRecordGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """
        train_examples_history = []
        iteration_train_examples = deque([], maxlen=self.args.maxlenOfQueue)

        eps_time = AverageMeter()
        bar = ShadyBar('Arena.record.playGames', max=num)
        end = time.time()
        eps = 0
        maxeps = int(num)

        num = int(round(num / 2))
        oneWon = 0
        twoWon = 0
        draws = 0
        for _ in range(num):
            game_result, training_example = self.playGame(verbose=verbose, pit=True)
            if game_result == 1:
                oneWon += 1
            elif game_result == -1:
                twoWon += 1
            else:
                draws += 1
            # bookkeeping + plot progress
            eps += 1
            eps_time.update(time.time() - end)
            end = time.time()
            bar.suffix = 'P1/P2 ({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:} | RET: {ret:})' \
                .format(eps=eps, maxeps=maxeps, et=eps_time.avg, total=bar.elapsed_td, eta=bar.eta_td, ret=game_result)
            bar.next()

            iteration_train_examples += training_example

        self.player1, self.player2 = self.player2, self.player1

        for _ in range(num):
            game_result, training_example = self.playGame(verbose=verbose, pit=True)
            if game_result == -1:
                oneWon += 1
            elif game_result == 1:
                twoWon += 1
            else:
                draws += 1
            # bookkeeping + plot progress
            eps += 1
            eps_time.update(time.time() - end)
            end = time.time()
            bar.suffix = 'P2/P1 ({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:} | RET: {ret:})' \
                .format(eps=eps, maxeps=maxeps, et=eps_time.avg, total=bar.elapsed_td, eta=bar.eta_td, ret=game_result)
            bar.next()

            iteration_train_examples += training_example

        bar.finish()

        train_examples_history.append(iteration_train_examples)
        self._saveTrainExamples(train_examples_history)

        return oneWon, twoWon, draws

    def _saveTrainExamples(self, examples):
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, 'checkpoint_train_1.pth.tar' + ".examples")
        if os.path.isfile(filename):
            os.remove(filename)
        with open(filename, "wb+") as f:
            Pickler(f).dump(examples)

    def _saveMultipleTrainExamples(self, examples):
        import random
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        while True:
            iteration = random.randint(1, 1000000000000)
            filename = os.path.join(folder, 'checkpoint_human_' + str(iteration) + '.pth.tar' + ".examples")
            if not os.path.isfile(filename):
                with open(filename, "wb+") as f:
                    Pickler(f).dump(examples)
                break
