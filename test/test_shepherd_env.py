from math import inf
from gym_shepherd.envs.shepherd_env import ShepherdEnv
import gym
import random
import numpy as np

#from IPython.display import clear_output

"""Training the agent""" 

from gym import envs
#print(envs.registry.all())

env = gym.make('gym_shepherd:Shepherd-v0')
#print(env)
env.render()

#q_table = np.zeros([env.observation_space.n, env.action_space.n])
q_table = np.zeros([64, 4])

# Hyperparameters

alpha = 0.1
gamma = 0.6
epsilon = 0.8

# For plotting metrics

all_epochs = []
all_penalties = []

for i in range(1):

    state = env.reset()
   
    epochs, penalties, reward, = 0, 0, 0
    done = False
    count = 0
    
    while not done:
        #epsilon = epsilon*0.95
        
        if random.uniform(0, 1) < epsilon:
            action = env.action_space.sample() # Explore action space
        else:
            action = np.argmax(q_table[state]) # Exploit learned values

        action, next_state, reward, done, info = env.step(action) 
        # print intuitive state (translate number to sth)
        print(info)
        
        old_value = q_table[state, action]
        next_max = np.max(q_table[next_state])
        
        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        q_table[state, action] = new_value

        if reward == -10:
            penalties += 1

        state = next_state
        epochs += 1

        # render
        env.render()

        count += 1
        if count%100 == 0:
            print("Epsilon", epsilon)
        
    if i % 100 == 0:
        #clear_output(wait=True)
        print(f"Episode: {i}")

print(q_table)

print("Training finished.\n")