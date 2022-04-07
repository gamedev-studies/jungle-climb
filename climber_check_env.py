from climber_gym import ClimberAgent

env = ClimberAgent()
for episode in range(10):
    done = False
    obs = env.reset()
    while True:
        random_action = env.action_space.sample()
        obs, reward, done, info = env.step(random_action)
        env.render()
        if done:
            print("Game over! Score: %s" % info['score'])
            break