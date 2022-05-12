import time
import datetime
import csv
import time
import json
import os
from stable_baselines3 import PPO

from climber_game import ClimberGame, Observer
from climber_gym import ClimberAgent

models_dir = f"models"
logs_dir = f"logs"
results_dir = f"results"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

if not os.path.exists(results_dir):
    os.makedirs(results_dir)

def _save_results(row):
    with open(''.join([results_dir,'/results.csv']), 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')        
        writer.writerow(row)

with open("config_train.json") as config_file:
    data = json.loads(config_file.read())

for run in data["run"]:
    
    if data["session"] == "human":                

        for test in data["tests"]:            
            best_score = 0
            best_climb_count = 0
            t_end = time.time() + data['time']
            while time.time() < t_end: 
                game = ClimberGame(shift_speed=test['shift_speed'], max_gaps=test['max_gaps'], buildno=test['id'])
                myObserver = Observer()
                game.attach(myObserver)
                ClimberGame.main(game)
                while True:
                    ClimberGame.render(game)
                    if ClimberGame.run_logic(game, -1) >= 0:
                        if myObserver.event.score > best_score:
                            best_score = myObserver.event.score

                        if myObserver.event.climb_count > best_climb_count:
                            best_climb_count = myObserver.event.climb_count
                        break              
            
            # save the results only after warming up
            if not data["warmup"]:
                _save_results([str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')), data['time'], run, data['session'], data['skill'], test['shift_speed'], test['max_gaps'], best_score, best_climb_count])


    if data["session"] == "ai-train":

        # no need to train twice
        if run == 2:
            break

        for test in data["tests"]:
            # only train the first and last build
            if (test['train']):         

                env = ClimberAgent(shift_speed=test['shift_speed'], 
                    max_gaps=test['max_gaps'])

                myObserver = Observer()
                env.game.attach(myObserver)

                env.reset()

                if data["skill"] == "novice":
                    TIMESTEPS = 100000
                if data["skill"] == "pro":
                    TIMESTEPS = 1000000                

                model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logs_dir)
                model.learn(total_timesteps=TIMESTEPS)
                model.save(''.join([models_dir,"/",data["skill"],'-',test["id"]]))


    if data["session"] == "ai-play":

        for test in data["tests"]:

            env = ClimberAgent(shift_speed=test['shift_speed'], max_gaps=test['max_gaps'], buildno=test["id"])
            myObserver = Observer()
            env.game.attach(myObserver)
            best_score = 0
            best_climb_count = 0

            obs = env.reset()

            if data["skill"] != "random":
                if test["train"]:
                    model_name = ''.join([models_dir,"/",data["model"],"-",data["skill"],'-',test["id"]])                    
                else:
                    model_name = ''.join([models_dir,"/",data["model"],"-",data["skill"],'-build-1'])

                model = PPO.load(model_name, env=env)

            t_end = time.time() + data['time']
            while time.time() < t_end:

                if data["skill"] == "random":
                    random_action = env.action_space.sample()
                    observation, reward, done, info = env.step(random_action)             
                else:
                    action, _state = model.predict(obs)
                    obs, reward, done, info = env.step(action)

                if myObserver.event.score > best_score:
                    best_score = myObserver.event.score

                if myObserver.event.climb_count > best_climb_count:
                    best_climb_count = myObserver.event.climb_count

                env.render()

                if done:
                    env.reset()

            print(best_score, best_climb_count)
            _save_results([str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')), data['time'], run, data['session'], data['skill'], test['shift_speed'], test['max_gaps'], best_score, best_climb_count])

            env.reset()