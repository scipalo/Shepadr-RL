from math import inf, sqrt
from gym_shepherd.envs.shepherd_env import ShepherdEnv
import gym
import random
import numpy as np
import time

#from IPython.display import clear_output

"""Training the agent""" 

from gym import envs
#print(envs.registry.all())

env = gym.make('gym_shepherd:Shepherd-v0')
#print(env)
env.render()

#q_table = np.zeros([env.observation_space.n, env.action_space.n])
q_table = np.zeros([128, 8])
q_normalize = np.ones([128, 8])

# Hyperparameters

alpha = 0.2
gamma = 0.6 #
epsilon = 0.97
eps = epsilon

# For plotting metrics

info = {'success':False}
all_epochs = []
all_penalties = []

for i in range(100):

    start_time = time.time()

    print("EPISODE",i-1,"Epsilon", eps, info["success"])

    state = env.reset()
   
    epochs, penalties, reward, = 0, 0, 0
    epsilon = epsilon*0.97
    done = False
    count = 0

    while not done:
        
        eps = epsilon
        if i < 65:
            eps = sqrt(epsilon)

        if random.uniform(0, 1) < eps:
            action = random.randint(0,7) # Explore action space
        else:
            action = np.argmax(q_table[state]/q_normalize[state]) # Exploit learned values

        #print("ACTION",action)
        action, next_state, reward, done, info = env.step(action) 
        # print intuitive state (translate number to sth)
        
        #print(info)
        
        old_value = q_table[state, action]/q_normalize[state, action]
        next_max = np.max(q_table[next_state]/q_normalize[next_state])
        
        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        q_table[state, action] = new_value
        q_normalize[state, action] += 1
        #print("Action", action, q_table[state])

        if reward == -10:
            penalties += 1

        state = next_state
        epochs += 1

        # render
        count += 1
        if count % 999 == 0:
            env.render()

    print(time.time() - start_time)           

print(q_table)
print(q_normalize)
print(q_table/q_normalize)

np.savetxt('test/qtable.txt', q_table, delimiter=',')
np.savetxt('test/qtable_normalized.txt', q_table/q_normalize, delimiter=',')

print("Training finished.\n")