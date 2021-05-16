import random
import sys
import numpy as np
from gym import spaces

def init_sheep_table (sheep_num, field_size):

    sheep_x = random.sample(range(1, field_size), sheep_num)
    sheep_y = random.sample(range(1, field_size), sheep_num)
    herd = zip(sheep_x, sheep_y)
    dog = (0,0)

    #print(herd)
    return herd, dog
    
init_sheep_table(10, 20)

observation_high = np.array([
          np.finfo(np.float32).max,
          np.finfo(np.float32).max,
          np.finfo(np.float32).max,
          np.finfo(np.float32).max])
observation_space = spaces.Box(low=0, high=1, shape=(6, 6), dtype=np.float16)
print(observation_space)

action_space = spaces.Discrete(9)
print(action_space)

obs_low = np.array(10*[-1000.0])
obs_high = np.array(10*[1000.0])
print(obs_low)
ce = spaces.Box(low=obs_low, high=obs_high)
print(ce)