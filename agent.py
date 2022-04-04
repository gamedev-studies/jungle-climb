from stable_baselines3 import PPO

import gym
import numpy as np
from gym import spaces
from game import ClimberGame
import objects

class ClimberAgent(gym.Env):
  """Custom Environment that follows gym interface"""
  metadata = {'render.modes': ['human']}
  
  # Action Constants
  UP = 0
  DOWN = 1
  LEFT = 2
  RIGHT = 3
  JUMP = 4

  def __init__(self):
    super(ClimberAgent, self).__init__()
    number_of_actions = 4
    number_of_observations = 2
    self.action_space = spaces.Discrete(number_of_actions)
    self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(number_of_observations,), dtype=np.float32)
    self.game = ClimberGame()
    self.observer = objects.Observer()
    self.prevScore = 0
    self.game.attach(self.observer)

  def step(self, action):
    self.game.game(action)

    reward = 0
    done = (self.observer.event.lives == 0)
    info = {}

    # todo: check events to reward
    # return obs
    x = 0
    y = 0
    obs = [x, y]
    return np.array(obs, dtype=np.float32), reward, done, info

  def reset(self):
    self.game.initGame()
    x = 0
    y = 0
    obs = [x, y]
    return np.array(obs, dtype=np.float32)

  def render(self, mode='human'):
    self.game.render()
