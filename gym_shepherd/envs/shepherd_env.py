import gym
import random
from gym import spaces

import numpy as np
from math import sqrt
from scipy.spatial import distance
import matplotlib.pyplot as plt

class ShepherdEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    # action_space ... actions of an agent
    # action_space ... the environment’s data to be observed by the agent

    def init_sheep_table (self):

        sheep_x = [random.choice(range(1, self.field_size)) for i in range(self.sheep_num)]
        sheep_y = [random.choice(range(1, self.field_size)) for i in range(self.sheep_num)]
        #.discard((0,0))
        herd = list(set(zip(sheep_x, sheep_y)))
        self.sheep_num = len(herd)
        dog = (0,0)

        #print(herd)

        return herd, dog

    def state_translation_fun(self):

        zf = [1, 2, 3, 4]
        zzf = [1,2,3,4,5,6,7,8]
        states = [ i*100 + j*10 + k for i in zzf for j in zf for k in zf]
        #print(states[1:15])
        
        d = { states[i] : i  for i in range(128)}
        #print(d)

        return d

    def __init__(self):

        self.state_translation_dict = self.state_translation_fun()

        self.info_mode = 1
        self.finish = False

        self.curr_episode = 0
        self.current_step = 0
        self.episode_length = 0
        self.episode_reward = 0
        
        self.sheep_num = 70
        self.field_size = 60
        self.herd, self.dog = self.init_sheep_table()

        self.dog_move_size = 4
        self.dog_influence = int(self.field_size/4)
        self.dog_influence_rm = int(self.field_size/4)

        self.max_num_of_steps = 6000
        self.target_distance = int((int(sqrt(self.sheep_num)) + 1)/2)+1
        self.calculated_distance = sqrt(2)*self.field_size # za 20 kvadratov je to 18

        self.action_space = spaces.Discrete(8)
        self.observation_space = spaces.Discrete(128) #spaces.Box(low=obs_low, high=obs_high)

 
    def step(self, action):

        """
        The dog takes a step in the environment
        Parameters
        ----------
        action : float array
        Returns
        -------
        ob, reward, episode_over, info : tuple
            observation (float array) : 
                observation after dog position is updated.
            reward (float) : 
                amount of reward achieved by dog in the previous step.
            episode_over (bool) : 
                flag that indicates if the environment is reset or not.
            info (dict) :
                useful information about the environment for debugging.
        """
        
        success = False

        self.current_step += 1
        # print(str(self.curr_episode)+" "+str(self.current_step),end="")
        
        action = self._take_action(action)
        
        # get reward and state 
        ob = self._get_state()
        reward = self._get_reward()

        # bad terminal conditions
        if self.current_step > self.max_num_of_steps:
            self.finish = True

        # good terminal conditions
        
        _, max_distance = self.dist_herd_center()
        self.calculated_distance = max_distance

        if self.calculated_distance <= self.target_distance:
            print("FINISHED")
            print("calc dist: "+str(self.calculated_distance))
            print("tar dist: "+str(self.target_distance))
            success = True
            self.finish = True

        # update rl parameters
        self.episode_length += 1
        self.episode_reward += reward

        # generate info return parameter
        if self.info_mode == 1 and self.finish:
            info = {'reward':self.episode_reward, 'lenght':self.episode_length, 'success': success}
        else:
            info = {'sheep_num' : len(self.herd), 'success': success}

        # ob je cifra
        return action, ob, reward, self.finish, info

    def reset(self):

        self.finish = False
        self.curr_episode += 1
        self.current_step = 0
        self.episode_length = 0
        self.episode_reward = 0

        self.current_step = 0
        self.herd, self.dog = self.init_sheep_table()

        state = self._get_state()
        return state

    def _get_state(self):
        """Return state based on action of the dog
           Stack all variables and return state array
          
        state = np.hstack((self.sheep_com, self.farthest_sheep, 
                    self.target, self.dog_pose, self.radius_sheep, 
                    self.target_distance))
        return state
        """
        dog_direction = self.dog_direction() # vrača 1-8
        dog_sheep = self.closenes_sheep_dog('discrete') * 4
        sheep_sheep = self.closenes_sheep_sheep('discrete') * 4

        if dog_sheep < 2:
            dog_sheep += 1
        if sheep_sheep <2:
            sheep_sheep += 1

        state = dog_direction * 100 + dog_sheep * 10 + sheep_sheep
        state_trans = self.state_translation_dict[state] 
        # print("new state: ", end=" ")
        # print(state_trans)

        return state_trans
    
    def dog_direction(self):

        dog = self.dog
        herd = self.herd
               
        obmocje = 0
        center, _ = self.dist_herd_center()
        point1 = (center[0] + 2,center[1]+1)
        point2 = (center[0] + 1,center[1]+2)
        point3 = (center[0] - 1,center[1]+2)
        point4 = (center[0] - 2,center[1]+1)
        #d=(x-x1)(y2-y1) - (y-y1)(x2-x1)
        for i in herd: 
            d1 = (dog[0]-center[0])*(point1[1]-center[1]) - (dog[1]-center[1])*(point1[0]-center[0])
            d2 = (dog[0]-center[0])*(point2[1]-center[1]) - (dog[1]-center[1])*(point2[0]-center[0])
            d3 = (dog[0]-center[0])*(point3[1]-center[1]) - (dog[1]-center[1])*(point3[0]-center[0])
            d4 = (dog[0]-center[0])*(point4[1]-center[1]) - (dog[1]-center[1])*(point4[0]-center[0])
            if (d1 > 0) and (d2 > 0) and (d3 > 0) and (d4 >= 0):
                obmocje = 1
            elif (d1 <= 0) and (d2 > 0) and (d3 > 0) and (d4 > 0):
                obmocje = 2
            elif (d1 < 0) and (d2 <= 0) and (d3 > 0) and (d4 > 0):
                obmocje = 3
            elif (d1 < 0) and (d2 < 0) and (d3 <= 0) and (d4 > 0):
                obmocje = 4
            elif (d1 < 0) and (d2 < 0) and (d3 < 0) and (d4 <= 0):
                obmocje = 5
            elif (d1 >= 0) and (d2 < 0) and (d3 < 0) and (d4 < 0):
                obmocje = 6
            elif (d1 > 0) and (d2 >= 0) and (d3 < 0) and (d4 < 0):
                obmocje = 7
            elif (d1 > 0) and (d2 > 0) and (d3 >= 0) and (d4 < 0):
                obmocje = 8
        
        return obmocje 

    # RISANJE

    def render(self, size=30, mode='human'):

        # if not fig:
        #     # create a figure
        #     fig = plt.figure()
        #     plt.ion()
        #     plt.show()

        herd = self.herd
        dog = self.dog

        plt.clf()
        x = list(map(lambda x: x[0]*size, herd))
        y = list(map(lambda x: x[1]*size, herd))
        plt.scatter( dog[0]*size,  dog[1]*size, 
                    c='r', s=50, label='Dog')
        plt.scatter( self.field_size*0.25*size,self.field_size*0.25*size, 
                    c='y', s=50, label='Dog')
        plt.scatter(x,  y, 
                    c='b', s=50, label='Sheep')
        plt.title('Shepherding')
        plt.xlim([0, self.field_size*size])
        plt.ylim([0, self.field_size*size])
        #plt.legend()
        plt.draw()
        plt.pause(0.001)

    # REWARD

    def _get_reward(self):
        """Return reward based on action of the dog"""
        # območja, ovca pes, ovca ovca
        in_house = self.in_house()
        dog_direction = self.dog_direction()
        dog_sheep = self.closenes_sheep_dog() 
        sheep_sheep = self.closenes_sheep_sheep()
        reward = 0.03 * in_house + sheep_sheep #  0.1 * in_house + 0.1 * dog_sheep +
        if self.current_step % 499 == 0:
            print("Reward: "+ str(0.1 *in_house) +" "+ str(0.1 *dog_sheep) +" "+ str(sheep_sheep)+"-> "+ str(reward))
        return reward


    def in_house(self):
    
        center, _ = self.std_dev_herd_center()
        dist = distance.euclidean(center, (self.field_size*0.25,self.field_size*0.25))
        max_distance = self.field_size*sqrt(2)

        #print("CCC", dist/max_distance)
        return dist/max_distance
        

    # funkcija dist_herd_center sprejme položaj ovc in izračuna njihovo središče
    # vrne (x,y) kooridnato središča in najdaljšo izmed razdalj ovc do središča
    def dist_herd_center(self):

        herd = self.herd

        seznam_x = list(map(lambda i: i[0], herd))
        seznam_y = list(map(lambda i: i[1], herd))
        x = sum(seznam_x)/len(seznam_x)
        y = sum(seznam_y)/len(seznam_y)
        center = (x,y)
        distances = []

        for i in range(len(herd)):        
            distances.append(distance.euclidean(herd[i], center))

        return center, max(distances)

    def std_dev_herd_center(self):

        herd = self.herd
        goal_radius = self.target_distance

        seznam_x = list(map(lambda i: i[0], herd))
        seznam_y = list(map(lambda i: i[1], herd))
        x = sum(seznam_x)/len(seznam_x)
        y = sum(seznam_y)/len(seznam_y)
        center = (x,y)
        distances = []

        for i in range(len(herd)):        
            distances.append(distance.euclidean(herd[i], center))

        std_dev = sum(distances)/len(distances)
        return center, std_dev

    def closenes_sheep_sheep(self, type='continuous'):

        # continum std dev

        goal_radius = self.target_distance
        _, std_dev_sheep_center = self.std_dev_herd_center()
        std_dev_normalised = min( max(0, std_dev_sheep_center - goal_radius) / (self.field_size*sqrt(2)/5), 1) 

        reward = 1 - std_dev_normalised
        rew_pow = reward*reward
        rew_disc = round(rew_pow * 4)/4

        #print("HHHHH", rew_disc, rew_pow)
        if type == 'continuous':
            return rew_pow
       
        return rew_disc

    # distance dog to center of sheep
    def closenes_sheep_dog(self, type='continuous'):

        dog_impact = self.dog_influence
        center, _ = self.dist_herd_center()
        dog_center_dist = distance.euclidean(center, self.dog)

        rew = 1 - min(max(dog_center_dist - dog_impact, 0)/(self.field_size*sqrt(2)/3), 1)
        rew_pow = rew*rew
        rew_disc = round(rew_pow * 4)/4

        #print("REW", rew_disc, rew_pow)
        if type == 'continuous':
            return rew_pow

        return rew_disc 

    # TAKE ACTION functions

    def _take_action(self, action):
        """Update position of dog based on action and env"""
        # dog movement & influenced sheep movement accordingly
        action = self._take_action_dog(action)
        # sheep movement (all sheep)
        self.fake_random()
        return action

    def _take_action_dog(self, action):

        """Return state based on action of the dog"""        
        
        (x, y) = self.dog
        n = self.field_size

        #prestavi se pes, če se lahko
        move_size = self.dog_move_size
        is_move = False
        
        if action==0:
            if 0<=y+move_size<n: #gor
                self.dog = (x, y+move_size)
            else:
                self.dog = (x, y-move_size)
                action = (action + 2 ) % 4
                
        elif action == 1:#desno
            if 0<=x+move_size<n:
                self.dog = (x+move_size, y)
            else:
                self.dog = (x-move_size,y)
                action = (action + 2 ) % 4
        elif action == 2: #dol
            if 0<=y-move_size<n:
                self.dog = (x, y-move_size)
            else:
                self.dog = (x, y+move_size)
                action = (action + 2 ) % 4
        elif action == 3: #levo
            if 0<=x-move_size<n:
                self.dog = (x-move_size,y)
            else:
                self.dog = (x+move_size,y)
                action = (action + 2 ) % 4

        # diagonale
        elif action == 1: #levo gor
            if 0<=x-move_size<n and 0<=y+move_size <n:
                self.dog = (x-move_size,y+move_size)
            else:
                self.dog = (x+move_size,y-move_size)
                action = 6
        elif action == 5: #levo dol
            if 0<=x-move_size<n and 0<=y-move_size<n:
                self.dog = (x-move_size,y-move_size)
            else:
                self.dog = (x+move_size,y+move_size)
                action = 7
        elif action == 6: #desno gor
            if 0<=x+move_size<n and 0<=y+move_size<n:
                self.dog = (x+move_size,y+move_size)
            else:
                self.dog = (x-move_size,y-move_size)
                action = 4
        elif action == 7: #desno dol
            if 0<=x+move_size<n and 0<=y-move_size<n:
                self.dog = (x+move_size,y-move_size)
            else:
                self.dog = (x-move_size,y+move_size)
                action = 5
        
        self.sheep_escape()
        return action

    def sheep_escape(self):
        state = self.herd
        dog = self.dog
        n = self.field_size
        newState = []
        for sheep in state:
            #print("sheep", sheep, state)
            xx = sheep[0]
            yy = sheep[1]
            if distance.euclidean(sheep, dog) < self.dog_influence:
                sheep_options = [(xx-1, yy-1), (xx-1,yy), (xx-1,yy+1),(xx,yy-1),(xx,yy+1),(xx+1,yy-1), (xx+1,yy),(xx+1,yy+1)]
                sheep_options = self.clean_options(sheep_options)
                if len(sheep_options)>0:
                    dist_dog = list(map(lambda i: distance.euclidean(i, dog), sheep_options))
                    m = max(dist_dog)
                    #max_dist_dog = [j for j in dist_dog if j == m]
                    max_dist_dog_i = [i for i, j in enumerate(dist_dog) if j == m]
                    center,_ = self.dist_herd_center()
                    d = { i: distance.euclidean(sheep_options[i], center)  for i in max_dist_dog_i}
                    move =min(d, key=d.get) #indeks poteze v sheep_options
                    newState.append(sheep_options[move])
                else:
                    newState.append(sheep)
            else:
                newState.append(sheep)

        self.herd = newState

    def is_on_lawn(self, sheep):
        x, y = sheep
        return(0<=y<self.field_size and 0<=x<self.field_size)

    def clean_options(self, sheep_options):
        cleared_sheep_options = []
        for option in sheep_options:
            if option == self.dog:
                pass
            elif option in self.herd:
                pass
            elif not self.is_on_lawn(option):
               pass
                #print("PADE DOL", option)
            else:
                cleared_sheep_options.append(option)

        return cleared_sheep_options

    def sheep_move_to_center(self, sheep):
        xx = sheep[0]
        yy = sheep[1]
        sheep_options = [(xx-1, yy-1), (xx-1,yy), (xx-1,yy+1),(xx,yy-1),(xx,yy+1),(xx+1,yy-1), (xx+1,yy),(xx+1,yy+1)]
        sheep_options = self.clean_options(sheep_options)
        if len(sheep_options)>0:
            center,_ = self.dist_herd_center()
            dist_to_center = list(map(lambda x: distance.euclidean(center,x),sheep_options))
            new_position = np.argmin(dist_to_center)

            return sheep_options[new_position]

        else:
            return sheep

    def sheep_move_random(self, sheep):
        xx = sheep[0]
        yy = sheep[1]
        sheep_options = [(xx-1, yy-1), (xx-1,yy), (xx-1,yy+1),(xx,yy-1),(xx,yy+1),(xx+1,yy-1), (xx+1,yy),(xx+1,yy+1)]
        sheep_options = self.clean_options(sheep_options)

        if len(sheep_options)>0:
            new_position_idx = random.randint(0,len(sheep_options)-1)
            return sheep_options[new_position_idx]
        else:
            return sheep

    def fake_random(self):
        herd = self.herd
        new_herd = []
        e = 0.04
        for i in range(len(herd)):
            if random.uniform(0, 1) < e:
                new_herd.append(self.sheep_move_to_center(herd[i]))
            else:
                new_herd.append(self.sheep_move_random(herd[i]))
        
        self.herd = new_herd

