
import pygame, random
from pygame.locals import *


class Apple:
    def __init__(self, game):
        self.game = game
        self.X = random.randint(100, 491)
        self.X -= (self.X % 10)
        self.Y = random.randint(100, 491)
        self.Y -= (self.Y % 10)
        self.i = 0

    def display(self) -> None:
        dimention = (5+self.i%6, 5+self.i%6)
        appear = pygame.Surface(dimention)
        appear.fill((255, 0, 0))
        self.game.screen.blit(appear, (self.X, self.Y))
        self.i += 1
    
    def feeding(self, head: tuple[int, int]) -> bool:
        return head == (self.X, self.Y)


class Snake:
    def __init__(self, game):
        self.snake_pos = [(400, 400), (410, 400), (420, 400)]
        self.game = game

    def update_body(self, direction:str, feeding:str=False) -> None:
        if feeding:
            self.snake_pos.append(self.snake_pos[-1])
        if direction == Direction.UP:
            self.snake_pos.insert(0, (self.snake_pos[0][0], self.snake_pos[0][1]-10))
            self.snake_pos.pop()
        elif direction == Direction.DOWN:
            self.snake_pos.insert(0, (self.snake_pos[0][0], self.snake_pos[0][1]+10))
            self.snake_pos.pop()
        elif direction == Direction.RIGHT:
            self.snake_pos.insert(0, (self.snake_pos[0][0]+10, self.snake_pos[0][1]))
            self.snake_pos.pop()
        elif direction == Direction.LEFT:
            self.snake_pos.insert(0, (self.snake_pos[0][0]-10, self.snake_pos[0][1]))
            self.snake_pos.pop()

    def display(self) -> None:
        head = pygame.Surface((10, 10))
        skin = pygame.Surface((10, 10))
        head.fill((47,79,79))    
        skin.fill((0, 255, 0))
        
        for pos in self.snake_pos:
            self.game.screen.blit(skin, pos)
        self.game.screen.blit(head, self.snake_pos[0])
    
    def get_head(self) -> tuple[int, int]:
        return self.snake_pos[0]
    
    def get_boddy(self) -> list[tuple[int, int]]:
        return self.snake_pos[1:]

class Direction:
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    STOP = None

class Game:
    def __init__(self):
        pygame.init()
        self.screen = self._init_screen()
        self.clock = pygame.time.Clock()
        self.control = True
        self.direction = Direction.LEFT
        self.frame_iteration = 0

        self.s = Snake(self)
        self.apple = Apple(self)
        self.score = 0

    def get_snake(self) -> Snake:
        return self.s

    def get_apple(self) -> Apple:
        return self.apple
    
    def _set_direction(self, move: tuple[int, int, int]) -> None:
        if self.direction == Direction.UP:
            if move[1] == 1:
                self.direction = Direction.RIGHT
            elif move[2] == 1:
                self.direction = Direction.LEFT
        elif self.direction == Direction.DOWN:
            if move[1] == 1:
                self.direction = Direction.LEFT
            elif move[2] == 1:
                self.direction = Direction.RIGHT
        elif self.direction == Direction.LEFT:
            if move[1] == 1:
                self.direction = Direction.UP
            elif move[2] == 1:
                self.direction = Direction.DOWN
        elif self.direction == Direction.RIGHT:
            if move[1] == 1:
                self.direction = Direction.DOWN
            elif move[2] == 1:
                self.direction = Direction.UP
    
    def make_move(self, move):
        self.clock.tick(20)
        self._board()
        self._score_table()

        reward = 0
        done = False
        self.frame_iteration += 1

        # self.direction = self._get_event()
        self._get_event()
        self._set_direction(move=move)

        if self.apple.feeding(self.s.get_head()):
            self.s.update_body(self.direction, True)
            self.apple = Apple(self)
            self.score += 1
            reward = 10
        else:
            self.s.update_body(self.direction)
        if self.crash() or self.frame_iteration > 100*len(self.s.get_boddy()):
            #self.reset()
            self.frame_iteration = 0
            done = True
            reward = -10
            return reward, done, self.score

        self.s.display()
        self.apple.display()

        pygame.display.update()

        return reward, done, self.score
    
    def reset(self) -> None:
        self.control = True
        self.direction = Direction.LEFT

        self.s = Snake(self)
        self.apple = Apple(self)
        self.score = 0

    def _init_screen(self) -> pygame.Surface:
        screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption("Jogo da Cobrinha")
        icon = pygame.image.load("anaconda.png")
        pygame.display.set_icon(icon)
        self.font = pygame.font.Font("freesansbold.ttf", 32)
        return screen

    def _score_table(self) -> None:
        score_written = self.font.render("Score:"+ str(self.score), True, (0, 0, 0))
        self.screen.blit(score_written, (10, 10))

    def _get_event(self) -> Direction:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.control = False
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.control = False
                    pygame.quit()
                    quit()
                # elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                #     return Direction.UP
                # elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                #     return Direction.DOWN
                # elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                #     return Direction.RIGHT
                # elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                #     return Direction.LEFT
        # return self.direction
        # return None

    def _board(self) -> None:
        self.screen.fill((204, 255, 229))

        limit_1 = pygame.Surface((20, 20))
        limit_1.fill((46,139,87))

        positions = [(80, 80 + i * 20) for i in range(22)]
        positions.extend([(500, 80 + i * 20) for i in range(22)])
        positions.extend([(80 + i * 20, 80) for i in range(22)])
        positions.extend([(80 + i * 20, 500) for i in range(22)])
        for pos in positions:
            self.screen.blit(limit_1, pos)

    def crash(self, head=None) -> bool:
        if head is None:
            head = self.s.get_head()
        if head in self.s.get_boddy():
            return True
        if head[0] < 100 or head[0] >= 500 or head[1] < 100 or head[1] >= 500:
            return True
        return False

    def main(self) -> None:
        while self.control:
            self.clock.tick(13)
            self._board()
            self._score_table()

            self.direction = self._get_event()

            if self.apple.feeding(self.s.get_head()):
                self.s.update_body(self.direction, True)
                self.apple = Apple(self)
                self.score += 1
            else:
                self.s.update_body(self.direction)
            if self.crash():
                self.reset()

            self.s.display()
            self.apple.display()

            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = Game().main()
