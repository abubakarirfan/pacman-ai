import random
from utils import translate_to_screen, translate_to_maze, Direction
from agent import Ghost, Pacman
from path import Path
from world import World, Dot, Wall, Powerup, GhostBehaviour


class GameEngine:
    def __init__(self):
        self.ascii_maze = [
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "XP     O     XX     O      X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X                      O   X",
            "X XXXX XX XXXXXXXX XX XXXX X",
            "X XXXX XX XXXXXXXX XX XXXX X",
            "X      XXO   XX    XX      X",
            "XXXXXX XXXXX XX XXXXX XXXXXX",
            "XXXXXX XXXXX XX XXXXX XXXXXX",
            "XXXXXX XX          XX XXXXXX",
            "XXXXXX XX XXX  XXX XX XXXXXX",
            "XXXXXX XX X   G  X XX XXXXXX",
            "X         X G    X         X",
            "XXXXXX XX X   G  X XX XXXXXX",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        ]

        self.numpy_maze = []
        self.dot_spaces = []
        self.powerup_spaces = []
        self.reachable_spaces = []
        self.ghost_spawns = []
        self.size = (0, 0)
        self.convert_maze_to_numpy()
        self.p = Path(self.numpy_maze)

    def request_new_random_path(self, ghost: Ghost):
        random_space = random.choice(self.reachable_spaces)
        current_maze_coord = translate_to_maze(ghost.get_position())

        path = self.p.get_path(current_maze_coord[0], current_maze_coord[1], random_space[0],
                               random_space[1])

        if path is None:
            print("No path found")
        else:
            test_path = [translate_to_screen(item) for item in path]
            ghost.set_new_path(test_path)

    def convert_maze_to_numpy(self):
        for x, row in enumerate(self.ascii_maze):
            self.size = (len(row), x + 1)
            binary_row = []
            for y, column in enumerate(row):
                if column == "G":
                    self.ghost_spawns.append((y, x))

                if column == "X":
                    binary_row.append(0)
                else:
                    binary_row.append(1)
                    self.dot_spaces.append((y, x))
                    self.reachable_spaces.append((y, x))
                    if column == "O":
                        self.powerup_spaces.append((y, x))

            self.numpy_maze.append(binary_row)


if __name__ == "__main__":
    unified_size = 32
    pacman_game = GameEngine()
    size = pacman_game.size
    world = World(size[0] * unified_size, size[1] * unified_size)

    for y, row in enumerate(pacman_game.numpy_maze):
        for x, column in enumerate(row):
            if column == 0:
                world.add_wall(Wall(world, x, y, unified_size))

    for cookie_space in pacman_game.dot_spaces:
        translated = translate_to_screen(cookie_space)
        cookie = Dot(world, translated[0] + unified_size / 2, translated[1] + unified_size / 2)
        world.add_cookie(cookie)

    for powerup_space in pacman_game.powerup_spaces:
        translated = translate_to_screen(powerup_space)
        powerup = Powerup(world, translated[0] + unified_size / 2, translated[1] + unified_size / 2)
        world.add_powerup(powerup)

    for i, ghost_spawn in enumerate(pacman_game.ghost_spawns):
        translated = translate_to_screen(ghost_spawn)
        ghost = Ghost(world, translated[0], translated[1], unified_size, pacman_game)
        world.add_ghost(ghost)

    pacman = Pacman(world, unified_size, unified_size, unified_size, pacman_game)
    world.add_pacman(pacman)
    world.set_current_mode(GhostBehaviour.CHASE)
    world.tick(120)
