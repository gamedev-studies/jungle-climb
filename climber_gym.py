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
    number_of_actions = 10
    number_of_observations = 7
    self.action_space = spaces.Discrete(number_of_actions)
    self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(number_of_observations,), dtype=np.float32)
    self.game = ClimberGame()
    self.observer = Observer()
    self.prev_player_x = 0
    self.prev_player_y = 0
    self.prev_on_ground = True
    self.player_y_before_jump = 0
    self.game.attach(self.observer)

  def step(self, action):
    self.game.run_logic(action)

    reward = 0
    event = self.observer.event
    done = (event.alive == False)
    info = {'score': event.score}

    left_bound = 0
    right_bound = 750
    gap_padding = 10

    large_reward = 100
    medium_reward = 20
    small_reward = 10
    tiny_reward = 1

    cur_dist_gap = abs(event.gap_x - event.player_x)
    prev_dist_gap = abs(event.gap_x - self.prev_player_x)
    #print("cur_dist_gap vs. prev_dist_gap", cur_dist_gap, prev_dist_gap)

    if event.player_x < left_bound or event.player_x > right_bound:
      #print("bad: going out bounds")
      reward -= tiny_reward * abs(event.player_x - 400)
    else:
      if event.player_x < event.gap_x or event.player_x > event.gap_x + 50:
        if cur_dist_gap < prev_dist_gap:
          #print("good: going to gap")
          reward += large_reward - math.log10(cur_dist_gap)
        else:
          #print("bad: going away from gap")
          reward -= medium_reward + math.log10(cur_dist_gap)
      else:
        if not event.on_ground:
          reward += medium_reward
        else:
          reward -= tiny_reward

      if not event.on_ground and self.prev_on_ground: # if player went from ground to air
        #print("GROUND: Player just jumped!")
        self.player_y_before_jump = event.player_y
      elif not event.on_ground and not self.prev_on_ground: # if player is on air
        #print("GROUND: Player is on air!")
        pass
      elif event.on_ground and not self.prev_on_ground: # if player came from air to ground
        #print("GROUND: Player is back on the ground!")
        #print(event.player_y, self.player_y_before_jump)
        if event.player_y < self.player_y_before_jump and abs(event.player_y - self.player_y_before_jump) > 100: # if player is one platform up
          #print("GROUND: WENT UP! ========================")
          reward += large_reward
        self.player_y_before_jump = event.player_y
      else: # if player stayed on the ground
        pass


    self.prev_on_ground = event.on_ground
    self.prev_player_x = event.player_x
    self.prev_player_y = event.player_y
    self.last_action = action
    #print(self.prev_player_x, event.player_x)
    print(reward)
    print(reward)
    print(reward)

    obs = [event.player_x, event.player_y, event.score, event.alive, event.has_jumped, event.gap_x, event.facing_right]
    return np.array(obs, dtype=np.float32), reward, done, info

  def reset(self):
    self.game.main()
    return np.array([0, 0, 0, True, False, 0, False], dtype=np.float32)

  def render(self, mode='human'):
    self.game.render()
