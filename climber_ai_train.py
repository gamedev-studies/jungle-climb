from climber_gym import ClimberAgent
from stable_baselines3 import PPO

env = ClimberAgent()
results = []
model = PPO('MlpPolicy', env, verbose=1, tensorboard_log='tensorboard', gamma=1, seed=123, device='cuda')
model.learn(total_timesteps=1000000) 
obs = env.reset()
model.save("models/model1")



