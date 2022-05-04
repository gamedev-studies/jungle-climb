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
    number_of_actions = 3
    number_of_observations = 8
    self.action_space = spaces.Discrete(number_of_actions)
    self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(number_of_observations,), dtype=np.float32)
    self.game = ClimberGame()
    self.observer = Observer()
    self.prev_player_x = 0
    self.prev_player_y = 0
    self.prev_on_ground = True
    self.prev_score = 0
    self.player_y_before_jump = 0
    self.game.attach(self.observer)

  def step(self, action):
    self.game.run_logic(action)

    reward = 0
    event = self.observer.event
    done = (event.alive == False)
    info = {}

    left_bound = 0
    right_bound = 750
    gap_padding = 10

    large_reward = 100
    medium_reward = 20
    small_reward = 10
    tiny_reward = 1

    cur_dist_gap1 = abs(event.gap_x1 - event.player_x)
    cur_dist_gap2 = event.gap_x2 - event.player_x 
    prev_dist_gap1 = abs(event.gap_x1 - self.prev_player_x)
    log_dist = math.log10(1 if cur_dist_gap1 <= 0 else cur_dist_gap1)
    #print("cur_dist_gap vs. prev_dist_gap", cur_dist_gap, prev_dist_gap)
    #print("cur_dist_gap2", cur_dist_gap2)
    #print("event.facing_side", event.facing_side)

    if event.score == 0:
      reward -= tiny_reward
    else:
      reward += math.log10(event.score)

    if event.player_x < left_bound or event.player_x > right_bound:
      #print("bad: going out bounds")
      reward -= tiny_reward * abs(event.player_x - 400)
    else:
      if event.player_x < event.gap_x1 or event.player_x > event.gap_x1 + 50:
        if cur_dist_gap1 < prev_dist_gap1:
          #print("good: going to gap")
          reward += large_reward - log_dist
        else:
          #print("bad: going away from gap")
          reward -= medium_reward + log_dist
      else: # under the gap
        if not event.on_ground and not self.prev_on_ground: # if player is on air
          #print("JUMP: Player is on air!")
          if cur_dist_gap2 == 0:
            reward += tiny_reward 
          elif event.facing_side == 0 and cur_dist_gap2 < 0:
            reward += large_reward
          elif event.facing_side == 1 and cur_dist_gap2 > 0:
            reward += large_reward
          else:
            reward -= medium_reward 

    if not event.on_ground and self.prev_on_ground: # if player went from ground to air
      #print("JUMP: Player just jumped!")
      self.player_y_before_jump = event.player_y
    elif event.on_ground and not self.prev_on_ground: # if player came from air to ground
      #print("JUMP: Player is back on the ground!")
      if event.player_y < self.player_y_before_jump and abs(event.player_y - self.player_y_before_jump) > 70: # if player is one platform up
        # can't be 85, movement makes this value less certain
        print("JUMP: WENT UP! ========================")
        reward += large_reward
      self.player_y_before_jump = event.player_y

    self.prev_on_ground = event.on_ground
    self.prev_player_x = event.player_x
    self.prev_player_y = event.player_y
    self.last_action = action
    self.prev_score = event.score
    #print(self.prev_player_x, event.player_x)
    print(reward)

    obs = [event.player_x, event.player_y, event.gap_x1, event.gap_x2, event.alive, event.on_ground, event.facing_side, event.score]
    return np.array(obs, dtype=np.float32), reward, done, info

  def reset(self):
    self.game.main()
    return np.array([0, 0, 400, 400, True, True, 1, 0], dtype=np.float32)

  def render(self, mode='human'):
    self.game.render()
