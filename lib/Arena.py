import time

from lib.progress.average import AverageMeter
from lib.progress.bar import Bar


class Arena:
    """
    An Arena class where any 2 agents can be pit against each other.
    """

    def __init__(self, player1, player2, game, view=None):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            view: a function that takes board as input and prints it. Is necessary for verbose mode.
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.view = view

    def playGame(self, verbose=False):
        """
        Executes one episode of a game.

        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """
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
                print("Turn ", str(it), "Player ", str(cur_player))
                self.view.display(board)
            action = players[cur_player + 1](self.game.getCanonicalForm(board, cur_player))
            valids = self.game.getValidMoves(self.game.getCanonicalForm(board, cur_player), 1)
            if valids[action] == 0:
                print(action)
                assert valids[action] > 0

            board, cur_player = self.game.getNextState(board, cur_player, action)

        if verbose:
            assert self.view
            print("Game over: Turn ", str(it), "Result ", str(self.game.getGameEnded(board, 1)))
            self.view.display(board)

        return self.game.getGameEnded(board, 1)

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """
        eps_time = AverageMeter()
        bar = Bar('Arena.playGames', max=num)
        end = time.time()
        eps = 0
        maxeps = int(num)

        num = int(num / 2)
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
            bar.suffix = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps + 1,
                                                                                                       maxeps=maxeps,
                                                                                                       et=eps_time.avg,
                                                                                                       total=bar.elapsed_td,
                                                                                                       eta=bar.eta_td)
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
            bar.suffix = '({eps}/{maxeps}) Eps Time: {et:.3f}s | Total: {total:} | ETA: {eta:}'.format(eps=eps + 1,
                                                                                                       maxeps=num,
                                                                                                       et=eps_time.avg,
                                                                                                       total=bar.elapsed_td,
                                                                                                       eta=bar.eta_td)
            bar.next()

        bar.finish()

        return oneWon, twoWon, draws
