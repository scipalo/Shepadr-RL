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
q_table = np.zeros([128, 8])

# Hyperparameters

alpha = 0.1
gamma = 0.6 #
epsilon = 0.95

# For plotting metrics

done = False
all_epochs = []
all_penalties = []

for i in range(1000):

    if i % 100 == 0:
        print("EPISODE",i-1,"Epsilon", epsilon, done)

    state = env.reset()
   
    epochs, penalties, reward, = 0, 0, 0
    done = False
    epsilon = epsilon*0.9978
    count = 0
    
    while not done:
        
        if random.uniform(0, 1) < epsilon:
            action = random.randint(0,7) # Explore action space
        else:
            action = np.argmax(q_table[state]) # Exploit learned values

        #print("ACTION",action)
        action, next_state, reward, done, info = env.step(action) 
        # print intuitive state (translate number to sth)
        
        #print(info)
        
        old_value = q_table[state, action]
        next_max = np.max(q_table[next_state])
        
        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        q_table[state, action] = new_value

        if reward == -10:
            penalties += 1

        state = next_state
        epochs += 1

        # render
        count += 1
        if count % 1000 == 0:
            env.render()            
        


print(q_table)
np.savetxt('test/qtable.txt', q_table, delimiter=',')

print("Training finished.\n")