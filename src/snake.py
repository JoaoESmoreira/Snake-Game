
import pygame, math, random
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
        return math.sqrt((head[0]-self.X)** 2 + (head[1]-self.Y)** 2) < 10

class Snake:
    def __init__(self, game):
        self.snake_pos = [(400, 400), (410, 400), (420, 400)]
        self.game = game

    def update_body(self, direction:str=None, fedding:str=False) -> None:
        increment_x = -10
        increment_y = 0
        if direction == State.UP:
            increment_x = 0
            increment_y = -10
        elif direction == State.DOWN:
            increment_x = 0
            increment_y = 10
        elif direction == State.RIGHT:
            increment_x = 10
            increment_y = 0
        elif direction == State.LEFT:
            increment_x = -10
            increment_y = 0
        self.snake_pos.insert(0, 
            (self.snake_pos[0][0]+increment_x,self.snake_pos[0][1]+increment_y))
        if not fedding:
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

class State:
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class Game:
    def __init__(self):
        pygame.init()
        self.screen = self._init_screen()
        self.clock = pygame.time.Clock()
        self.control = True
        self.direction = State.LEFT

        self.s = Snake(self)
        self.apple = Apple(self)
        self.score = 0

        self.main()

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

    def _get_event(self) -> State:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.control = False
            elif event.type == KEYDOWN:
                if event.key == pygame.K_q:
                    self.control = False
                elif event.key == pygame.K_UP and self.direction != State.DOWN:
                    return State.UP
                elif event.key == pygame.K_DOWN and self.direction != State.UP:
                    return State.DOWN
                elif event.key == pygame.K_RIGHT and self.direction != State.LEFT:
                    return State.RIGHT
                elif event.key == pygame.K_LEFT and self.direction != State.RIGHT:
                    return State.LEFT
        return self.direction

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

    def _crash(self) -> bool:
        distance = lambda head, pos: math.sqrt((head[0]-pos[0])** 2 + (head[1]-pos[1])** 2) < 10

        head = self.s.get_head()
        for pos in self.s.get_boddy():
            if distance(pos, head):
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
            if self._crash():
                break

            self.s.display()
            self.apple.display()

            pygame.display.update()

        while self.control:
            self.direction = self._get_event()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
