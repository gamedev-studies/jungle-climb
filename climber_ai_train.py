from climber_gym import ClimberAgent
from stable_baselines3 import PPO

env = ClimberAgent()
results = []
model = PPO('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=100000) 
obs = env.reset()
model.save("models/model1")
for i in range(0, 10):
    obs = env.reset()
    for episode in range(5000):
        action, _state = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        env.render()
        if done:
            print("no more lives")
            break



