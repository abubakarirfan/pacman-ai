import pygame
from utils import Direction, GhostBehaviour, ScoreType


class GameElement:
    def __init__(self, world, x, y, size: int, color=(255, 0, 0), shape: bool = False):
        self.size = size
        self.world: World = world
        self.screen = world.screen
        self.y = y
        self.x = x
        self.color = color
        self.circle = shape
        self.shape = pygame.Rect(self.x, self.y, size, size)

    def draw(self):
        if self.circle:
            pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.size)
        else:
            rect_object = pygame.Rect(self.x, self.y, self.size, self.size)
            pygame.draw.rect(self.screen, self.color, rect_object, border_radius=3)

    def tick(self):
        pass

    def get_shape(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return self.x, self.y


class Dot(GameElement):
    def __init__(self, screen, x, y):
        super().__init__(screen, x, y, 2, (255, 255, 0), True)


class Powerup(GameElement):
    def __init__(self, screen, x, y):
        super().__init__(screen, x, y, 8, (255, 255, 255), True)


class Wall(GameElement):
    def __init__(self, screen, x, y, size: int, color=(0, 100, 255)):
        super().__init__(screen, x * size, y * size, size - 2, color)


class World:
    def __init__(self, width: int, height: int):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Pacman')

        self.clock = pygame.time.Clock()

        self.done = False
        self.won = False

        self.game_objects = []
        self.walls = []
        self.cookies = []

        from agent import Pacman
        self.pacman: Pacman = None

        self.powerups = []
        self.ghosts = []
        self.lives = 3
        self.score = 0

        self.score_dot_pickup = 10
        self.score_ghost_eaten = 400
        self.score_powerup_pickup = 50

        self.power_active = False
        self.ghost_mode = GhostBehaviour.PATROL

        self.mode_switch_event = pygame.USEREVENT + 1
        self.power_active_end_event = pygame.USEREVENT + 2
        self.pacman_mode = pygame.USEREVENT + 3

        self.modes = [
            (7, 20),
            (7, 20),
            (5, 20),
            (5, 100000)
        ]
        self.current_phase = 0

    def tick(self, fps: int):
        black = (0, 0, 0)

        self.handle_mode_switch()
        pygame.time.set_timer(self.pacman_mode, 200)  # open close mouth
        while not self.done:
            for game_object in self.game_objects:
                game_object.tick()
                game_object.draw()

            self.display_text(f"Score: {self.score},  Lives: {self.lives}")

            if self.check_all_dots_collected():
                self.win_game()

            if self.pacman is None:
                self.display_text("GAME OVER", (self.width / 2 - 256, self.height / 2 - 256), 75)
            if self.won:
                self.display_text("GAME WON", (self.width / 2 - 256, self.height / 2 - 256), 75)
            pygame.display.flip()

            self.clock.tick(fps)
            self.screen.fill(black)
            self.handle_events()

        print("Game over")

    def check_all_dots_collected(self):
        return len(self.cookies) <= 0

    def win_game(self):
        self.won = True
        self.display_text("YOU WON", (self.width / 2 - 256, self.height / 2 - 256), 100)

    def handle_mode_switch(self):
        current_phase_timings = self.modes[self.current_phase]

        print(f"Current phase: {str(self.current_phase)}, current_phase_timings: {str(current_phase_timings)}")
        scatter_timing = current_phase_timings[0]
        chase_timing = current_phase_timings[1]

        if self.ghost_mode == GhostBehaviour.CHASE:
            self.current_phase += 1
            self.set_current_mode(GhostBehaviour.PATROL)
        else:
            self.set_current_mode(GhostBehaviour.CHASE)

        used_timing = scatter_timing if self.ghost_mode == GhostBehaviour.PATROL else chase_timing
        pygame.time.set_timer(self.mode_switch_event, used_timing * 1000)

    def start_power_active_timeout(self):
        pygame.time.set_timer(self.power_active_end_event, 15000)

    def add_game_object(self, obj: GameElement):
        self.game_objects.append(obj)

    def add_cookie(self, obj: GameElement):
        self.game_objects.append(obj)
        self.cookies.append(obj)

    def add_ghost(self, obj: GameElement):
        self.game_objects.append(obj)
        self.ghosts.append(obj)

    def add_powerup(self, obj: GameElement):
        self.game_objects.append(obj)
        self.powerups.append(obj)

    def activate_power(self):
        self.power_active = True
        self.set_current_mode(GhostBehaviour.PATROL)
        self.start_power_active_timeout()

    def set_won(self):
        self.won = True

    def get_won(self):
        return self.won

    def add_score(self, score: ScoreType):
        self.score += score.value

    def get_pacman_position(self):
        return self.pacman.get_position() if self.pacman is not None else (0, 0)

    def set_current_mode(self, mode: GhostBehaviour):
        self.ghost_mode = mode

    def get_current_mode(self):
        return self.ghost_mode

    def end_game(self):
        if self.pacman in self.game_objects:
            self.game_objects.remove(self.pacman)
        self.pacman = None

    def kill_pacman(self):
        self.lives -= 1
        self.pacman.set_position(32, 32)
        self.pacman.set_direction(Direction.NONE)
        if self.lives == 0:
            self.end_game()

    def display_text(self, text, position=(32, 0), in_size=30):
        font = pygame.font.SysFont('Arial', in_size)
        text_surface = font.render(text, False, (255, 255, 255))
        self.screen.blit(text_surface, position)

    def is_power_active(self):
        return self.power_active

    def add_wall(self, obj: Wall):
        self.add_game_object(obj)
        self.walls.append(obj)

    def get_walls(self):
        return self.walls

    def get_cookies(self):
        return self.cookies

    def get_ghosts(self):
        return self.ghosts

    def get_powerups(self):
        return self.powerups

    def get_game_objects(self):
        return self.game_objects

    def add_pacman(self, pacman):
        self.add_game_object(pacman)
        self.pacman = pacman

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            if event.type == self.mode_switch_event:
                self.handle_mode_switch()

            if event.type == self.power_active_end_event:
                self.power_active = False

            if event.type == self.pacman_mode:
                if self.pacman is None: break
                self.pacman.mouth_open = not self.pacman.mouth_open

        if self.pacman is None:
            return

