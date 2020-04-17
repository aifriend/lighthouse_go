"""
Contains 4 players
(lighthouse player, human player, random player, greedy player
(if searching for nnet player, it is defined by pre-learnt model)
Human player has defined input controls for Pygame and console

"""
import sys

import numpy as np
import pygame

from lh.config.configuration import Configuration
from lh.gamer.lightgo import LightGo
from lh.logic.board.board import Board


class RandomLHPlayer:
    def __init__(self, game, config):
        self.game = game
        self.config = config

    def play(self, board):
        print("RP|", end="")
        action = np.random.randint(self.game.getActionSize())
        valid = self.game.getValidMoves(board, 1)
        while valid[action] != 1:
            # select random action on present state
            action = np.random.randint(self.game.getActionSize())

        return action


class GoLHPlayer:
    def __init__(self, game, config):
        self.game = game
        self.logic = self.game.logic
        self.lightgo = LightGo()
        self.player = None
        state = {
            "player_num": 1,
            "player_count": 1,
            "position": (13, 11),
            "map": self.logic.board.island.island_map,
            "lighthouses": list(self.logic.board.lighthouses.keys()),
        }
        self.lightgo.initialize(state)

    def play(self, board):
        print("LH|", end="")

        # update board status
        self.logic.from_array(board)

        # player
        self.player = self.logic.board.player_by(1)
        # on-the-fly pre-round game update
        self.logic.board.pre_round()
        # player game update
        self.logic.board.pre_player_update(1)

        # light-go logic
        lighthouses = []
        for lh in self.logic.board.lighthouses.values():
            connections = [next(l for l in c if l != lh.pos)
                           for c in self.logic.board.connection.conns if lh.pos in c]
            lighthouses.append({
                "position": lh.pos,
                "owner": lh.owner,
                "energy": lh.energy,
                "connections": connections,
                "have_key": lh.pos in self.player.keys,
            })
        state = {
            "position": self.player.pos,
            "score": self.player.score,
            "energy": self.player.energy,
            "view": self.logic.board.island.get_view(self.player.pos, self.logic.board.island.energy),
            "lighthouses": lighthouses,
        }
        move = self.lightgo.play(state)

        # select valid action
        action = 0
        n_actions = 0
        for row in range(self.logic.board.size[0]):
            for col in range(self.logic.board.size[1]):
                if (col, row) == self.player.pos:
                    if move["command"] == "move":
                        motion = (move["x"], move["y"])
                        n_actions += self._get_move_id(motion)
                        action = n_actions
                    elif move["command"] == "attack":
                        energy = move["energy"]
                        n_actions += self._get_attack_id(self.player, energy)
                        action = n_actions
                    elif move["command"] == "connect":
                        possible_connections = Board.POSSIBLE_CONNECTIONS.copy()
                        key, _ = possible_connections.popitem()
                        n_actions += key
                        action = n_actions

                else:
                    n_actions += Configuration.NUM_ACTS

            if action != 0:
                break

        return action

    def _get_move_id(self, d_move):
        cx, cy = self.player.pos
        op_player = self.logic.board.player_by(-1)
        for key, mov in Board.POSSIBLE_MOVES.items():
            if d_move == mov:
                if op_player.pos != (cx + d_move[0], cy + d_move[1]):
                    return key
        return 0

    def _get_attack_id(self, player, attack_energy):
        if player.pos in self.logic.board.lighthouses.keys():
            attack_energy_100 = int(round(player.energy * Board.POSSIBLE_ATTACK[13]))
            if attack_energy_100 == attack_energy:
                return 13
            else:
                attack_energy_80 = int(round(player.energy * Board.POSSIBLE_ATTACK[12]))
                if attack_energy_80 == attack_energy:
                    return 12
                else:
                    attack_energy_60 = int(round(player.energy * Board.POSSIBLE_ATTACK[11]))
                    if attack_energy_60 == attack_energy:
                        return 11
                    else:
                        attack_energy_30 = int(round(player.energy * Board.POSSIBLE_ATTACK[10]))
                        if attack_energy_30 == attack_energy:
                            return 10
                        else:
                            attack_energy_10 = int(round(player.energy * Board.POSSIBLE_ATTACK[9]))
                            if attack_energy_10 == attack_energy:
                                return 9


class GreedyLHPlayer:
    def __init__(self, game, config):
        self.game = game
        self.config = config

    def play(self, board):
        valid = self.game.getValidMoves(board, 1)

        print("GP|", end="")
        print("GP > sum valids: %s", sum(valid), end="")
        candidates = []
        for a in range(self.game.getActionSize()):
            if valid[a] == 0:
                continue
            next_board, _ = self.game.getNextState(board, 1, a)
            score = self.game.logic.board.player_by(1).score
            candidates += [(-score, a)]

        # select best action on present state
        candidates.sort()
        action = candidates[0][1]

        return action


class HumanLHPlayer:
    def __init__(self, game, config) -> None:
        self.game = game
        self.config = config

    def play(self, board: np.ndarray):
        print("HM|", end="")
        tup = tuple()
        valid = self.game.getValidMoves(board, 1)
        valid_pose = self._display_valid_moves(board, valid)
        while True:
            if self.config.args.visibility > 3:
                a = HumanLHPlayer._manage_input()
                action_index = a
            else:
                a = (input('type one of above actions in "action_name" format\n')).split(" ")
                action_index = Configuration.ACTS[a]

            # parse input
            try:
                tup = (int(valid_pose[1]), int(valid_pose[0]), int(action_index))
                a = np.ravel_multi_index(tup, (board.shape[0], board.shape[1], Configuration.NUM_ACTS))
            except Exception as exc:
                print("Could not parse action")

            # convert to action index in valids array
            if valid[a]:
                break
            else:
                print('This action is invalid!')
                self._display_valid_moves(board, valid)

        return a

    @staticmethod
    def _display_valid_moves(board, valid):
        valid_pose = set()
        valid_actions = dict()
        for i in range(len(valid)):
            if valid[i]:
                y, x, action_index = np.unravel_index(i, [board.shape[0], board.shape[1], Configuration.NUM_ACTS])
                name_action = Configuration.ACTS_REV[action_index]
                shortcut_action = Configuration.d_user_shortcuts_rev[action_index]
                valid_actions[shortcut_action] = name_action
                valid_pose.add((x, y))
        print(', '.join([str(v) + "(" + str(k) + ")" for k, v in valid_actions.items()]))
        assert len(valid_pose) == 1
        return valid_pose.pop()

    @staticmethod
    def _manage_input():
        while True:
            for event in pygame.event.get():
                # print(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit(0)
                if event.type == pygame.KEYDOWN:
                    try:
                        return Configuration.d_user_shortcuts[event.unicode]
                    except Exception as exc:
                        print("shortcut '" + event.unicode + "' not supported.")
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(1)
