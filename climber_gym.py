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
    number_of_observations = 7
    self.action_space = spaces.Discrete(number_of_actions)
    self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(number_of_observations,), dtype=np.float32)
    self.game = ClimberGame()
    self.observer = Observer()
    self.prev_player_x = 0
    self.prev_player_y = 0
    self.game.attach(self.observer)

  def step(self, action):
    self.game.run_logic(action)

    reward = 0
    event = self.observer.event
    done = (event.alive == False)
    info = {'score': event.score}

    left_bound = 100
    right_bound = 800

    large_reward = 100
    medium_reward = 20
    small_reward = 10
    tiny_reward = 1

    # reward agent for trying to "escape" the edges
    # punish agent for staying in the edges
    if (event.player_x < left_bound and not event.facing_right) or (event.player_x > right_bound and event.facing_right):
      reward -= large_reward
    elif (event.player_x < left_bound and event.facing_right) or (event.player_x > right_bound and not event.facing_right):
      reward += medium_reward
    elif (event.player_x > left_bound and event.facing_right) or (event.player_x < right_bound and not event.facing_right):  
      # reward for jumping when under the gap
      # punish lightly for not jumping
      if event.player_x > event.gap_x and event.player_x < event.gap_x + 100:
        if event.has_jumped:
          reward += medium_reward
        else:
          reward -= tiny_reward
      else:
        # if not under the gap
        # reward for going towards the gap
        # punish for going away from the gap
        if abs(event.gap_x - event.player_x) < abs(event.gap_x - self.prev_player_x):
          reward += small_reward
        else:
          reward -= small_reward

        self.prev_player_x = event.player_x

    obs = [event.player_x, event.player_y, event.score, event.alive, event.has_jumped, event.gap_x, event.facing_right]
    return np.array(obs, dtype=np.float32), reward, done, info

  def reset(self):
    self.game.main()
    return np.array([0, 0, 0, True, False, 0, False], dtype=np.float32)

  def render(self, mode='human'):
    self.game.render()
