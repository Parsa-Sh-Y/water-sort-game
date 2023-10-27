import heapq
from typing import TYPE_CHECKING
import copy

if TYPE_CHECKING:
    from game import Game


class Node:

    def __init__(self, g : int, state : list[list[int]], move : tuple[(int, int)], parent : 'Node') -> None:
        self.g = g
        self.state = state
        self.move = move
        self.parent = parent

    def __lt__(self, other):
        return False


class GameSolution:
    """
        A class for solving the Water Sort game and finding solutions(normal, optimal).

        Attributes:
            ws_game (Game): An instance of the Water Sort game which implemented in game.py file.
            moves (List[Tuple[int, int]]): A list of tuples representing moves between source and destination tubes.
            solution_found (bool): True if a solution is found, False otherwise.

        Methods:
            solve(self, current_state):
                Find a solution to the Water Sort game from the current state.
                After finding solution, please set (self.solution_found) to True and fill (self.moves) list.

            optimal_solve(self, current_state):
                Find an optimal solution to the Water Sort game from the current state.
                After finding solution, please set (self.solution_found) to True and fill (self.moves) list.
    """
    def __init__(self, game: 'Game'):
        """
            Initialize a GameSolution instance.
            Args:
                game (Game): An instance of the Water Sort game.
        """
        self.ws_game = game  # An instance of the Water Sort game.
        self.moves = []  # A list of tuples representing moves between source and destination tubes.
        self.tube_numbers = game.NEmptyTubes + game.NColor  # Number of tubes in the game.
        self.solution_found = False  # True if a solution is found, False otherwise.
        self.visited_tubes = set()  # A set of visited tubes.

    def top(self, tube: list[int]) -> int:

        if len(tube) == 0:
            return 0

        top_color = tube[-1]
        count = 0
        for i in range(len(tube)-1, -1, -1):
            if tube[i] == top_color:
                count += 1
            else:
                break

        return count

    def actions(self, current_state : list[list[int]]) -> list[tuple[int, int]]:

        result = [] 
        for i, tube in enumerate(current_state):
            colors = set(tube) # count distinct colors in the tube
            if len(tube) == self.ws_game.NColorInTube and len(colors) == 1 or len(tube) == 0: # skip the tube if it's already full and sorted or its empty
                continue
            
            flag = False # This flag is used to prevent a tube to be moved to different empty bottles.
            for j, tube2 in enumerate(current_state):
                if j == i:
                    continue
                elif len(colors) == 1 and len(tube2) == 0: # don't move a tube with a single color to an empty tube
                    continue
                elif len(tube2) == 0:
                    if not flag:
                        result.append((i, j))
                        flag = True
                elif tube[-1] == tube2[-1] and len(tube2) < self.ws_game.NColorInTube:
                    result.append((i, j))
            flag = False
        return result
    
    def result(self, state : list[list[int]], action : tuple[int, int]) -> list[list[int]]:
        """Find the next state based on the given state and the action"""
        result : list[list[int]] = copy.deepcopy(state)
        count_top = self.top(result[action[0]])
        color = result[action[0]][-1]

        available_space = self.ws_game.NColorInTube - len(result[action[1]])
        for i in range(min(count_top, available_space )):
            result[action[0]].pop()

        for i in range(min(count_top, available_space)):
            result[action[1]].append(color)
    
        return result

    def solve(self, current_state):
        """
            Find a solution to the Water Sort game from the current state.

            Args:
                current_state (List[List[int]]): A list of lists representing the colors in each tube.

            This method attempts to find a solution to the Water Sort game by iteratively exploring
            different moves and configurations starting from the current state.
        """
        
        if (self.ws_game.check_victory(current_state)):
            self.solution_found = True
            return
                
        actions : list[(int, int)] = self.actions(current_state)

        for action in actions:
            if self.solution_found:
                break
            next_state = self.result(current_state, action)
            next_state_str = str(next_state)
            if next_state_str in self.visited_tubes:
                continue
            self.visited_tubes.add(next_state_str)
            self.moves.append(action)
            self.solve(next_state)
        
        if not self.solution_found and len(self.moves) != 0:
            self.moves.pop()
        else:
            return


    def h(self, state : list[list[int]]) -> int: 
  
        result = 0
        colors_misplaced = {}
        floor = {}


        for tube in state:
            if len(tube) == 0:
                continue
            else:
                prev_color = tube[0]
                if not prev_color in floor:
                    floor[prev_color] = True
                if (prev_color in colors_misplaced):
                    colors_misplaced[prev_color] += 1
                else:
                    colors_misplaced[prev_color] = 1
                for i in range(1, len(tube)):
                    if tube[i] != prev_color:
                        prev_color = tube[i]
                        if (prev_color in colors_misplaced):
                            colors_misplaced[prev_color] += 1
                        else:
                            colors_misplaced[prev_color] = 1
                    
        
        for color in colors_misplaced:
            if color in floor:
                result += (colors_misplaced[color] - 1)
            else:
                result += colors_misplaced[color]

        return result

    def optimal_solve(self, current_state):
        """
            Find an optimal solution to the Water Sort game from the current state.

            Args:
                current_state (List[List[int]]): A list of lists representing the colors in each tube.

            This method attempts to find an optimal solution to the Water Sort game by minimizing
            the number of moves required to complete the game, starting from the current state.
        """
        frontier = []
        # The first elemenet in the q_element is the value of f(n)
        q_element : (int, Node) = (self.h(current_state) ,Node(0, current_state, None, None))
        heapq.heappush(frontier, q_element)

        while frontier:
            q_element : (int, Node) = heapq.heappop(frontier)
            node : Node = q_element[1]
            current_state : list[list[int]] = node.state
            self.visited_tubes.add(str(current_state))
            if self.ws_game.check_victory(current_state):
                self.solution_found = True
                break
            for action in self.actions(current_state):
                next_state = self.result(current_state, action)
                if str(next_state) in self.visited_tubes:
                    continue
                else:
                    new_node = Node(node.g + 1, next_state, action, node)
                    new_h = self.h(next_state)
                    heapq.heappush(frontier, (new_node.g + new_h, new_node))

        if self.solution_found:
            while node.parent != None:
                self.moves.append(node.move)
                node = node.parent
            self.moves.reverse()