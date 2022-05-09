from climber_gym import ClimberAgent
from stable_baselines3 import PPO

env = ClimberAgent()
results = []
model = PPO('MlpPolicy', env, verbose=1, tensorboard_log='tensorboard')
obs = env.reset()
model.load("models/model1")
for i in range(0, 20):
    obs = env.reset()
    for episode in range(50000):
        action, _state = model.predict(obs, deterministic=False)
        obs, reward, done, info = env.step(-1)
        env.render()
        if done:
            print("no more lives")
            break



