import math

from utils import Direction, ScoreType, GhostBehaviour, translate_to_maze, translate_to_screen
import pygame
from world import GameElement

THRESHOLD_DISTANCE = 80


class SpriteManager:
    def __init__(self):
        self.sprites = {
            "pacman_open": pygame.image.load("assets/pacman_state_1.png"),
            "pacman_closed": pygame.image.load("assets/pacman_state_2.png"),
            "ghost_fright": pygame.image.load("assets/ghost_run_mode.png"),
            "ghost": pygame.image.load('assets/ghost_1.png'),
        }

    def get_sprite(self, sprite_name):
        return self.sprites[sprite_name]


sprite_manager = SpriteManager()


class Agent(GameElement):
    def __init__(self, screen, x, y, size: int, color=(255, 0, 0), circle: bool = False):
        super().__init__(screen, x, y, size, color, circle)
        self.current_direction = Direction.NONE
        self.direction_buffer = Direction.NONE
        self.last_working_direction = Direction.NONE
        self.location_queue = []
        self.next_target = None
        self.image = sprite_manager.get_sprite('ghost')

    def get_next_location(self):
        return None if len(self.location_queue) == 0 else self.location_queue.pop(0)

    def set_direction(self, direction):
        self.current_direction = direction
        self.direction_buffer = direction

    def collides_with_wall(self, position):
        collision_rect = pygame.Rect(position[0], position[1], self.size, self.size)
        collides = False
        walls = self.world.get_walls()
        for wall in walls:
            collides = collision_rect.colliderect(wall.get_shape())
            if collides: break
        return collides

    def check_collision_in_direction(self, direction: Direction):
        desired_position = (0, 0)
        if direction == Direction.NONE: return False, desired_position
        if direction == Direction.UP:
            desired_position = (self.x, self.y - 1)
        elif direction == Direction.DOWN:
            desired_position = (self.x, self.y + 1)
        elif direction == Direction.LEFT:
            desired_position = (self.x - 1, self.y)
        elif direction == Direction.RIGHT:
            desired_position = (self.x + 1, self.y)

        return self.collides_with_wall(desired_position), desired_position

    def automatic_move(self, direction: Direction):
        pass

    def tick(self):
        self.reached_target()
        self.automatic_move(self.current_direction)

    def reached_target(self):
        pass

    def draw(self):
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.screen.blit(self.image, self.get_shape())


class Pacman(Agent):

    def __init__(self, screen, x, y, size: int, game_controller):
        super().__init__(screen, x, y, size, (255, 255, 0), False)
        self.game_controller = game_controller
        self.last_non_colliding_position = (0, 0)
        self.open = sprite_manager.get_sprite("pacman_open")
        self.closed = sprite_manager.get_sprite("pacman_closed")
        self.image = self.open
        self.current_direction = Direction.NONE
        self.mouth_open = True

    def tick(self):
        self.last_non_colliding_position = self.get_position()

        if self.next_target is None or self.reached_target():
            self.request_best_path()

        # Once the new direction is calculated, move pacman in that direction
        self.automatic_move(self.calculate_direction_to_next_target())

        if self.collides_with_wall((self.x, self.y)):
            self.set_position(self.last_non_colliding_position[0], self.last_non_colliding_position[1])

        self.handle_cookie_pickup()
        self.handle_ghosts()

    # Check if the target has been reached. If it has, then update the next target.
    def reached_target(self):
        if (self.x, self.y) == self.next_target:
            self.next_target = self.get_next_location()

    # Move to the desired direction
    def automatic_move(self, in_direction: Direction):
        self.current_direction = in_direction
        if in_direction == Direction.UP:
            self.set_position(self.x, self.y - 1)
        elif in_direction == Direction.DOWN:
            self.set_position(self.x, self.y + 1)
        elif in_direction == Direction.LEFT:
            self.set_position(self.x - 1, self.y)
        elif in_direction == Direction.RIGHT:
            self.set_position(self.x + 1, self.y)

    def handle_cookie_pickup(self):
        collision_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        cookies = self.world.get_cookies()
        powerups = self.world.get_powerups()
        game_objects = self.world.get_game_objects()
        cookie_to_remove = None
        for cookie in cookies:
            collides = collision_rect.colliderect(cookie.get_shape())
            if collides and cookie in game_objects:
                game_objects.remove(cookie)
                self.world.add_score(ScoreType.DOT)
                cookie_to_remove = cookie

        if cookie_to_remove is not None:
            cookies.remove(cookie_to_remove)

        if len(self.world.get_cookies()) == 0:
            self.world.set_won()

        for powerup in powerups:
            collides = collision_rect.colliderect(powerup.get_shape())
            if collides and powerup in game_objects:
                if not self.world.is_power_active():
                    game_objects.remove(powerup)
                    self.world.add_score(ScoreType.POWERUP)
                    self.world.activate_power()

    def set_new_path(self, in_path):
        for item in in_path:
            self.location_queue.append(item)
        self.next_target = self.get_next_location()

    def calculate_direction_to_next_target(self) -> Direction:
        if self.next_target is None:
            self.request_best_path()
            return Direction.NONE

        diff_x = self.next_target[0] - self.x
        diff_y = self.next_target[1] - self.y
        if diff_x == 0:
            return Direction.DOWN if diff_y > 0 else Direction.UP
        if diff_y == 0:
            return Direction.LEFT if diff_x < 0 else Direction.RIGHT

        if diff_x != 0 and diff_y != 0:
            # handle diagonal case, e.g. prioritize moving horizontally
            return Direction.LEFT if diff_x < 0 else Direction.RIGHT

        self.request_best_path()
        return Direction.NONE

    def get_nearest(self, objects, current_position):
        nearest_object = None
        min_distance = math.inf

        for obj in objects:
            obj_position = obj.get_position()
            distance = self.calculate_distance(current_position, obj_position)

            if distance < min_distance:
                min_distance = distance
                nearest_object = obj

        return nearest_object

    def calculate_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def move_away_from_ghost(self, current_position, ghost_position):
        dx, dy = current_position[0] - ghost_position[0], current_position[1] - ghost_position[1]
        new_target = (current_position[0] + dx, current_position[1] + dy)

        # Keep the new target within the boundaries of the game.
        new_target = (max(0, min(self.world.width, new_target[0])),
                      max(0, min(self.world.height, new_target[1])))

        return new_target

    def request_best_path(self):
        current_position = self.get_position()
        nearest_cookie = self.get_nearest(self.world.get_cookies(), current_position)
        nearest_powerup = self.get_nearest(self.world.get_powerups(), current_position)
        nearest_ghost = self.get_nearest(self.world.get_ghosts(), current_position)

        cookie_distance = self.calculate_distance(current_position, nearest_cookie.get_position())
        powerup_distance = self.calculate_distance(current_position, nearest_powerup.get_position())
        ghost_distance = 0 if nearest_ghost is None else self.calculate_distance(current_position,
                                                                                 nearest_ghost.get_position())
        ghost_nearby = nearest_ghost and ghost_distance <= THRESHOLD_DISTANCE

        # If power is active or a powerup is close and there are ghosts nearby, we should go for it.
        if self.world.is_power_active() or (ghost_nearby and powerup_distance < THRESHOLD_DISTANCE):
            if nearest_ghost is not None:
                best_target = nearest_ghost.get_position()
            elif nearest_powerup is not None:
                best_target = nearest_powerup.get_position()
            else:  # If all ghosts are eaten or no ghosts nearby, go for the nearest cookie
                best_target = nearest_cookie.get_position()
        else:  # If power is not active
            if ghost_nearby:  # If ghost is near
                best_target = self.move_away_from_ghost(current_position, nearest_ghost.get_position())
            else:  # If ghost is not near, we chase the nearest cookie.
                best_target = nearest_cookie.get_position()

        # Now that we have our target, we request the path.
        target_position = translate_to_maze(best_target)
        current_maze_coord = translate_to_maze(current_position)
        path = self.game_controller.p.get_path(current_maze_coord[0], current_maze_coord[1], target_position[0],
                                               target_position[1])
        if path is None:
            print('No Path Found')
        else:
            new_path = [translate_to_screen(item) for item in path]
            self.set_new_path(new_path)

    def handle_ghosts(self):
        collision_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        ghosts = self.world.get_ghosts()
        game_objects = self.world.get_game_objects()
        for ghost in ghosts:
            collides = collision_rect.colliderect(ghost.get_shape())
            if collides and ghost in game_objects:
                if self.world.is_power_active():
                    game_objects.remove(ghost)
                    self.world.add_score(ScoreType.GHOST)
                else:
                    if not self.world.get_won():
                        if self.world.pacman:
                            self.world.kill_pacman()

    def direction_to_angle(self, direction):
        if direction == Direction.UP:
            return 90
        elif direction == Direction.DOWN:
            return 270
        elif direction == Direction.LEFT:
            return 180
        elif direction == Direction.RIGHT:
            return 0
        else:  # Direction.NONE
            return 0  # or any other default angle

    def draw(self):
        self.image = self.open if self.mouth_open else self.closed
        self.image = pygame.transform.rotate(self.image, self.direction_to_angle(self.current_direction))
        super(Pacman, self).draw()


class Ghost(Agent):
    def __init__(self, screen, x, y, size: int, game_controller, sprite_path="assets/ghost_1.png"):
        super().__init__(screen, x, y, size)
        self.game_controller = game_controller
        self.sprite_normal = pygame.image.load(sprite_path)
        self.sprite_fright = sprite_manager.get_sprite("ghost_fright")

    def reached_target(self):
        if (self.x, self.y) == self.next_target:
            self.next_target = self.get_next_location()
        self.current_direction = self.calculate_direction_to_next_target()

    def set_new_path(self, in_path):
        for item in in_path:
            self.location_queue.append(item)
        self.next_target = self.get_next_location()

    def calculate_direction_to_next_target(self) -> Direction:
        if self.next_target is None:
            if self.world.get_current_mode() == GhostBehaviour.CHASE and not self.world.is_power_active():
                self.request_path_to_player(self)
            else:
                self.game_controller.request_new_random_path(self)
            return Direction.NONE

        diff_x = self.next_target[0] - self.x
        diff_y = self.next_target[1] - self.y
        if diff_x == 0:
            return Direction.DOWN if diff_y > 0 else Direction.UP
        if diff_y == 0:
            return Direction.LEFT if diff_x < 0 else Direction.RIGHT

        if self.world.get_current_mode() == GhostBehaviour.CHASE and not self.world.is_power_active():
            self.request_path_to_player(self)
        else:
            self.game_controller.request_new_random_path(self)
        return Direction.NONE

    def request_path_to_player(self, in_ghost):
        player_position = translate_to_maze(in_ghost.world.get_pacman_position())
        current_maze_coord = translate_to_maze(in_ghost.get_position())
        path = self.game_controller.p.get_path(current_maze_coord[0], current_maze_coord[1], player_position[0],
                                               player_position[1])
        if path is None:
            print('No Path Found')
        else:
            new_path = [translate_to_screen(item) for item in path]
            in_ghost.set_new_path(new_path)

    def automatic_move(self, in_direction: Direction):
        if in_direction == Direction.UP:
            self.set_position(self.x, self.y - 1)
        elif in_direction == Direction.DOWN:
            self.set_position(self.x, self.y + 1)
        elif in_direction == Direction.LEFT:
            self.set_position(self.x - 1, self.y)
        elif in_direction == Direction.RIGHT:
            self.set_position(self.x + 1, self.y)

    def draw(self):
        self.image = self.sprite_fright if self.world.is_power_active() else self.sprite_normal
        super(Ghost, self).draw()
