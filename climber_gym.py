from stable_baselines3 import PPO

import gym
import math
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
    number_of_actions = 4
    number_of_observations = 9
    self.action_space = spaces.Discrete(number_of_actions)
    self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(number_of_observations,), dtype=np.float32)
    self.game = ClimberGame()
    self.observer = Observer()
    self.prev_player_x = 0
    self.prev_player_y = 0
    self.prev_on_ground = True
    self.prev_score = 0
    self.player_y_before_jump = 0
    self.player_climbed_once = False
    self.last_actions = []
    self.game.attach(self.observer)

  def get_negative_reward(self, event):
    #return 0
    return event.time_elapsed * 5 if event.score == 0 else 0

  def step(self, action):
    self.game.run_logic(action)

    reward = 0
    event = self.observer.event
    done = (event.alive == False)
    info = {}

    large_reward = 100
    medium_reward = 20
    small_reward = 10
    tiny_reward = 1

    cur_dist_gap1 = abs(event.gap_x1 - event.player_x)
    cur_dist_gap2 = event.gap_x2 - event.player_x 
    prev_dist_gap1 = abs(event.gap_x1 - self.prev_player_x)

    if event.player_x < event.gap_x1 or event.player_x > event.gap_x1 + 50: #print("bad: NOT under the gap")
      if cur_dist_gap1 < prev_dist_gap1:
        #print("good: going to gap")
        reward += large_reward
      else:
        #print("bad: going away from gap")
        reward -= small_reward 
        reward -= self.get_negative_reward(event)
    else: #print("good: under the gap")
      if event.facing_side == 0 and cur_dist_gap2 < 0:
        #print("good: facing left, 2nd gap left")
        reward += large_reward
      elif event.facing_side == 1 and cur_dist_gap2 > 0:
        #print("good: facing right, 2nd gap right")
        reward += large_reward
      else:
        #print("bad: under the 1st gap, but facing away from the 2nd gap")
        reward -= large_reward

    self.prev_on_ground = event.on_ground
    self.prev_player_x = event.player_x
    self.prev_player_y = event.player_y
    self.prev_score = event.score

    if not event.alive:
      #print("DIED ================================")
      reward -= large_reward

    obs = [event.player_x, event.player_y, event.gap_x1, event.gap_x2, event.alive, event.on_ground, event.facing_side, event.score, event.time_elapsed]
    print(obs, "reward =", reward)
    return np.array(obs, dtype=np.float32), reward, done, info

  def reset(self):
    self.game.main()
    return np.array([0, 0, 400, 400, True, True, 1, 0, 0], dtype=np.float32)

  def render(self, mode='human'):
    self.game.render()
