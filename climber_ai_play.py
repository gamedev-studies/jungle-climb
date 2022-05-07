from climber_gym import ClimberAgent
from stable_baselines3 import PPO

env = ClimberAgent()
obs = env.reset()
model = PPO.load("models/model1", env=env)
for i in range(0, 10):
    obs = env.reset()
    for episode in range(5000):
        action, _state = model.predict(obs, deterministic=False)
        obs, reward, done, info = env.step(action)
        print("action", action)
        env.render()
        if done:
            print("Game over!")
            break
