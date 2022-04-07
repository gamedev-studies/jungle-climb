from stable_baselines3 import PPO

import gym
import numpy as np
from gym import spaces
from climber_game import ClimberGame
from climber_game import Observer

class ClimberAgent(gym.Env):
  """Custom Environment that follows gym interface"""
  metadata = {'render.modes': ['human']}
  
  # Action Constants
  LEFT = 0
  RIGHT = 1
  JUMP = 2

  def __init__(self):
    super(ClimberAgent, self).__init__()
    number_of_actions = 10
    number_of_observations = 4
    self.action_space = spaces.Discrete(number_of_actions)
    self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(number_of_observations,), dtype=np.float32)
    self.game = ClimberGame()
    self.observer = Observer()
    self.prevXPos = 0
    self.prevYPos = 0
    self.game.attach(self.observer)

  def step(self, action):
    self.game.run_logic(action)

    reward = 0
    event = self.observer.event
    done = (self.observer.event.alive == False)
    info = {'score': self.observer.event.score}
    print(self.observer.event.score)
    print(self.observer.event.player_x)
    print(self.observer.event.player_y)
    print(self.observer.event.alive)

    # avoid being too close to the wall
    if self.observer.event.player_x > 100 and self.observer.event.player_x <= 700:
      reward += 1
    else:
      reward -= 1

    # go up!
    if self.observer.event.player_y > self.prevYPos:
      reward += 1
      self.prevYPos = self.observer.event.player_y
    
    obs = [event.player_x, event.player_y, event.score, event.alive]
    return np.array(obs, dtype=np.float32), reward, done, info

  def reset(self):
    self.game.main()
    return np.array([0, 0, 0, True], dtype=np.float32)

  def render(self, mode='human'):
    self.game.render()
