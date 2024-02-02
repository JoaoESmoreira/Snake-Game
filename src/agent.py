import random
import torch
import numpy as np
import matplotlib.pyplot as plt
from snake import Snake, Apple, Game, Direction
from collections import deque
from model import Linear_QNet_Module, QTrainer
from helper import plot


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    def __init__(self) -> None:
        self.n_games = 0
        self.epsilon = 0    # randomness
        self.gamma = 0.9    # discount rate <= 1
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet_Module(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        snake = game.get_snake()
        head = snake.get_head()
        apple = game.get_apple()

        direction_left  = game.direction == Direction.LEFT
        direction_right = game.direction == Direction.RIGHT
        direction_up    = game.direction == Direction.UP
        direction_down  = game.direction == Direction.DOWN

        state = [
            # Danger in front
            direction_left  and game.crash((head[0]-10, head[1])) or
            direction_right and game.crash((head[0]+10, head[1])) or
            direction_up    and game.crash((head[0], head[1]-10)) or
            direction_down  and game.crash((head[0], head[1]+10)),

            # Danger in right
            direction_up    and game.crash((head[0]-10, head[1])) or
            direction_down  and game.crash((head[0]+10, head[1])) or
            direction_left  and game.crash((head[0], head[1]-10)) or
            direction_right and game.crash((head[0], head[1]+10)),

            # Danger in left
            direction_down  and game.crash((head[0]-10, head[1])) or
            direction_up    and game.crash((head[0]+10, head[1])) or
            direction_right and game.crash((head[0], head[1]-10)) or
            direction_left  and game.crash((head[0], head[1]+10)),

            direction_left,
            direction_right,
            direction_up,
            direction_down,

            apple.X < head[0],
            apple.X > head[0],
            apple.Y < head[1],
            apple.Y > head[1],
        ]
        return np.array(state)
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def train_long_memory(self) -> None:
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state) -> list[int]:
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move

def train() -> None:
    plot_scores = []
    plot_means_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    environment = Game()

    while True:
        current_state = agent.get_state(environment)
        final_move = agent.get_action(current_state)
        reward, done, score = environment.make_move(final_move)
        new_state = agent.get_state(environment)

        agent.train_short_memory(current_state, final_move, reward, new_state, done)
        agent.remember(current_state, final_move, reward, new_state, done)

        if done:
            environment.reset()
            agent.n_games += 1
            agent.train_long_memory()
            if score > record:
                record = score
                agent.model.save()
            print("Game: ", agent.n_games, " Score: ", score, " Record ", record)
            # Done plot info
            # plot_scores.append(score)
            # total_score += score
            # mean_score = total_score / agent.n_games
            # plot_means_scores.append(mean_score)
            # plot(plot_scores, plot_means_scores)

if __name__ == '__main__':
    train()