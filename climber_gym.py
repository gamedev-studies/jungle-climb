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
    right_bound = 750
    gap_padding = 10

    large_reward = 100
    medium_reward = 20
    small_reward = 10
    tiny_reward = 1

    cur_dist_gap = abs(event.gap_x - event.player_x)
    prev_dist_gap = abs(event.gap_x - self.prev_player_x)
    print("cur_dist_gap vs. prev_dist_gap", cur_dist_gap, prev_dist_gap)

    if event.player_x < left_bound or event.player_x > right_bound:
      print("bad: going out bounds")
      reward -= large_reward
    else:
      if event.player_x < event.gap_x or event.player_x > event.gap_x + 100:
        if cur_dist_gap < prev_dist_gap:
          print("good: going to gap")
          reward += large_reward
        else:
          print("bad: going away from gap")
          reward -= medium_reward
      else:
        print("good: under the gap")
        reward += tiny_reward
        if event.player_y < self.prev_player_y:
          reward += large_reward
          print("good: going up")
        elif event.player_y >= self.prev_player_y:
          reward -= small_reward
          print("bad: going down or staying at the same level")

    self.prev_player_x = event.player_x
    self.prev_player_y = event.player_y
    self.last_action = action
    print(self.prev_player_x, event.player_x)

    obs = [event.player_x, event.player_y, event.score, event.alive, event.has_jumped, event.gap_x, event.facing_right]
    return np.array(obs, dtype=np.float32), reward, done, info

  def reset(self):
    self.game.main()
    return np.array([0, 0, 0, True, False, 0, False], dtype=np.float32)

  def render(self, mode='human'):
    self.game.render()
