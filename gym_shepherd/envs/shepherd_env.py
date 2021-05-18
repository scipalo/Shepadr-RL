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
        sheep_x.append(0)
        sheep_y.append(0)
        herd = list(set(zip(sheep_x, sheep_y)) )
        self.sheep_num = len(herd)
        dog = (0,0)

        print(herd)

        return herd, dog

    def __init__(self):

        self.info_mode = 1
        self.dog_influence = 2
        self.dog_influence_rm = 5

        self.finish = False
        self.curr_episode = 0
        self.current_step = 0
        self.episode_length = 0
        self.episode_reward = 0

        self.sheep_num = 20
        self.field_size = 10
        self.herd, self.dog = self.init_sheep_table()

        self.max_num_of_steps = 1000 
        self.target_distance = 10
        self.calculated_distance = sqrt(2)*self.field_size # za 20 kvadratov je to 18

        self.action_space = spaces.Discrete(4)
        obs_low = np.array(3*[0])
        obs_high = np.ones(3)
        self.observation_space = spaces.Discrete(64) #spaces.Box(low=obs_low, high=obs_high)

 
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
        self._take_action(action)
        
        # get reward and state 
        # TODO (Ada) nastavi not self.calculated_distance - to je max razdalja ovce od centra
        ob = self._get_state()
        reward = self._get_reward()

        # bad terminal conditions
        if self.current_step > self.max_num_of_steps:
            self.finish = True

        # good terminal conditions
        
        _, max_distance = self.dist_herd_center()
        self.calculated_distance = max_distance

        if self.calculated_distance <= self.target_distance:
            print("calc dist: "+str(self.calculated_distance))
            print("tar dist: "+str(self.target_distance))
            success = True
            self.finish = True

        # update rl parameters
        self.episode_length += 1
        self.episode_reward += reward

        # generate info return parameter
        if self.info_mode == 1 and self.finish:
            info = {'rewrd':self.episode_reward, 'lenght':self.episode_length, 'success': success}
        else:
            info = {'number of sheep':self.sheep_num, 'success': success}

        # ob je cifra
        return ob, reward, self.finish, info

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
        return 20
        
    def _get_reward(self):
            """Return reward based on action of the dog"""
            # območja, ovca pes, ovca ovca
            reward = self.areas() + \
                     self.closenes_sheep_dog()  + \
                     self.closenes_sheep_sheep()
            print("Reward: "+ str(reward))
            return reward

    def _take_action(self, action):
        """Update position of dog based on action and env"""
        # dog movement & influenced sheep movement accordingly
        self._take_action_dog(action)
         # sheep movement (all sheep)
        self._update_environment()

    def _update_environment(self):

        """Update environment based on new position of dog"""
   
        state = self.herd
        pes = self.dog
        n = self.field_size

        newState = []
        (x, y) = pes
        for ovca in state:
            (i, j) = ovca

            # ali je blizu psa
            r_x = x-i
            r_y = y-j
            if r_x**2+r_y**2<=self.dog_influence_rm*self.dog_influence_rm:
                ii = jj = 0
                if abs(r_x)<abs(r_y):
                    if r_x>0:
                        ii = 1
                    else:
                        ii = -1
                else:
                    if r_y>0:
                        jj = 1
                    else:
                        jj = -1
                
                
                if (i +ii, j +jj) not in newState and 0<=i+ii<=n and 0<=j+jj<=n:
                    newState.append((i +ii, j +jj))
                else:
                    if ii == 0:
                        if (i +ii + 1, j +jj) not in newState and 0<=i+ii +1<=n and 0<=j+jj<=n:
                            newState.append((i +ii +1, j +jj))
                        elif (i +ii -1, j +jj) not in newState and 0<=i+ii-1<=n and 0<=j+jj<=n:
                            newState.append((i +ii -1, j +jj))
                        else:
                            newState.append(ovca)
                    else:
                        if (i +ii, j +jj +1) not in newState and 0<=i+ii<=n and 0<=j+jj+1<=n:
                            newState.append((i +ii, j +jj +1))
                        elif (i +ii, j +jj -1) not in newState and 0<=i+ii<=n and 0<=j+jj-1<=n:
                            newState.append((i +ii, j +jj -1))
                        else:
                            newState.append(ovca)
            else:
                a=random.randint(-1,1)
                if a>0: #gor dol
                    b = random.randint(-1,1)
                    if (i, j +b) not in newState and 0<=j+b<=n:
                            newState.append((i, j +b))
                    elif (i - 1, j + b) not in newState and 0<=j+b<=n and 0<=i-1<=n:
                            newState.append((i-1, j +b))
                    elif (i + 1, j + b) not in newState and 0<=j+b<=n and 0<=i+1<=n:
                            newState.append((i+1, j +b))
                    else:
                            newState.append(ovca)
                
                else:
                    b = random.randint(-1,1)
                    if (i +b , j) not in newState and 0<=i+b<=n:
                            newState.append((i + b, j))
                    elif (i+b, j + 1) not in newState and 0<=i+b<=n and 0<=j+1<=n:
                            newState.append((i+b, j +1))
                    elif (i + b, j - 1) not in newState and 0<=i+b<=n and 0<=j-1<=n:
                            newState.append((i+b, j -1))
                    else:
                            newState.append(ovca)

        self.herd = newState

    def _take_action_dog(self, action):

        """Return state based on action of the dog"""
        
        state = self.herd
        (x, y) = self.dog
        n = self.field_size

        #prestavi se pes, če se lahko
        if action==0:
            if 0<=y+1<n: #gor
                self.dog = (x, y+1)
        elif action == 1:#desno
            if 0<=x+1<n:
                self.dog = (x+1, y)
        elif action == 2: #dol
            if 0<=y-1<n:
                self.dog = (x, y-1)
        elif action == 3: #levo
            if 0<=x-1<n:
                self.dog = (x-1,y)

        Gor =[]
        Dol = []
        Levo = []
        Desno = []

        newSheep = []

        (x,y) = self.dog #nism zihr, da je ta stranica potrebna  
        for sheep in state:
            (i, j) = sheep
            if sheep in Gor:
                if (i, j+1) not in newSheep:
                    newSheep.append((i, j+1))
                elif (i-1,j+1) not in newSheep:
                    newSheep.append((i-1, j+1))
                elif (i+1,j+1) not in newSheep:
                    newSheep.append((i+1, j+1))
                else:
                    print("ta ovca nima več kam")
            elif sheep in Dol:
                if (i, j-1) not in newSheep:
                    newSheep.append((i, j-1))
                elif (i-1,j-1) not in newSheep:
                    newSheep.append((i-1, j-1))
                elif (i+1,j-1) not in newSheep:
                    newSheep.append((i+1, j-1))
                else:
                    print("ta ovca nima več kam")
            elif sheep in Levo:
                if (i-1, j) not in newSheep:
                    newSheep.append((i-1, j))
                elif (i-1,j+1) not in newSheep:
                    newSheep.append((i-1, j+1))
                elif (i-1,j-1) not in newSheep:
                    newSheep.append((i-1, j-1))
                else:
                    print("ta ovca nima več kam")

            elif sheep in Desno:
                if (i+1, j) not in newSheep:
                    newSheep.append((i+1, j))
                elif (i+1,j+1) not in newSheep:
                    newSheep.append((i+1, j+1))
                elif (i+1,j-1) not in newSheep:
                    newSheep.append((i+1, j-1))
                else:
                    print("ta ovca nima več kam")
            else:
                if x-i==self.dog_influence: #pes je 2 desno od ovce
                    if (i-1, j) in state:
                        if (i-1, j-1) not in state:
                            newSheep.append((i-1,j-1))
                        elif (i-1, j+1) not in state:
                            newSheep.append((i-1,j+1))
                        else:
                            Levo.append((i-1,j))
                        newSheep.append((i-1,j))
                    else: 
                        newSheep.append((i-1,j))

                
                elif x-i==-self.dog_influence: #pes je 2 levo od ovce
                    if (i+1, j) in state:
                        if (i+1, j-1) not in state:
                            newSheep.append((i+1,j-1))
                        elif (i+1, j+1) not in state:
                            newSheep.append((i+1,j+1))
                        else:
                            Desno.append((i+1,j))
                            newSheep.append((i+1,j))
                    else:
                        newSheep.append((i+1,j))

                if y-j==self.dog_influence: #pes je 2 gor od ovce
                    if (i, j-1) in state:
                        if (i-1, j-1) not in state:
                            newSheep.append((i-1,j-1))
                        elif (i+1, j-1) not in state:
                            newSheep.append((i+1,j-1))
                        else:
                            Dol.append((i,j-1))
                            newSheep.append((i,j-1))
                    else:
                        newSheep.append((i,j-1))

                if y-j==-self.dog_influence: #pes je 2 dol od ovce
                    if (i, j+1) in state:
                        if (i-1, j+1) not in state:
                            newSheep.append((i-1,j+1))
                        elif (i+1, j+1) not in state:
                            newSheep.append((i+1,j+1))
                        else:
                            Gor.append((i,j+1))
                            newSheep.append((i,j+1))
                    else:
                        newSheep.append((i,j+1))

        self.herd = newSheep

    # REWARD

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

    # funkcija dist_herd_dog izračuna razdaljo vsake ovce do psa in vrne najkrajšo razdaljo
    def dist_herd_dog(self):

        herd = self.herd
        dog = self.dog

        distances = []
        for i in range(len(herd)):        
            distances.append(distance.euclidean(herd[i], dog))
        return min(distances)


    # funcija closenes_sheep_sheep sprejme seznam ovc, velikost polja in radij za ovce pri katerem je dosežen cilj
    # vrne nagrado glede na stanje razpršenosti ovc (glede na to koliko je najdaljša razdalja ovce do njihovega središča)
    # razpon vrednosti je (goal_radius, diagonala polja)
    def closenes_sheep_sheep(self):

        herd = self.herd
        dog = self.dog
        field_size = self.field_size
        goal_radius = self.target_distance

        h = (field_size*sqrt(2)-goal_radius)/4
        center, max_distance = self.dist_herd_center()
        max_distance = max_distance - goal_radius
        if (max_distance >= 0 ) and (max_distance <= h):
            reward = 1
        elif (max_distance > h ) and (max_distance <= 2*h):
            reward = 0.75
        elif (max_distance > 2*h ) and (max_distance <= 3*h):
            reward = 0.25
        elif (max_distance > 3*h ) and (max_distance <= 4*h):
            reward = 0
        else:
            reward = 100
            print("Distance < 0, done.")

        return reward

    # funkcija closenes_sheep_dog sprejme seznam ovc, pozicijo psa, velikost polja in razdaljo pri kateri pes vpliva na ovce
    # izračuna razdaljo psa do najbližje ovce in vrne temu primerno nagrado
    # razpon je (dog_impact, diagonala polja)
    def closenes_sheep_dog(self):

        herd = self.herd
        dog = self.dog
        field_size = self.field_size
        dog_impact = self.dog_influence

        h = (field_size*sqrt(2)-dog_impact)/4
        min_distance = self.dist_herd_dog()
        min_distance = min_distance - dog_impact
        if (min_distance > 0 ) and (min_distance <= h):
            reward = 1
        elif (min_distance > h ) and (min_distance <= 2*h):
            reward = 0.75
        elif (min_distance > 2*h ) and (min_distance <= 3*h):
            reward = 0.25
        elif (min_distance > 3*h ) and (min_distance <= 4*h):
            reward = 0
        else:
            reward = 1
            print("Dog can impact herd.")

        return reward

    # funkcija areas sprejme pozicije ovc in pozicijo psa ter prešteje v koliko območjih okoli psa se nahajajo ovce. 
    # vrne nagrado glede na število območij.
    def areas(self):

        herd = self.herd
        dog = self.dog
        field_size = self.field_size

        rewards = {1:1, 2:0.75, 3:0.25,4:0}
        herd = list(map(lambda i: (i[0], field_size-i[1]), herd))
        dog = (dog[0], field_size - dog[1])
        point1 = (dog[0] + 1,dog[1]+1)
        point2 = (dog[0] - 1,dog[1]+1)
        seznam_up = []
        seznam_down = []
        seznam_left = []
        seznam_right = []
        nic = 0
        #d=(x-x1)(y2-y1) - (y-y1)(x2-x1)
        for i in herd: 
            d1 = (i[0]-dog[0])*(point1[1]-dog[1]) - (i[1]-dog[1])*(point1[0]-dog[0])
            d2 = (i[0]-dog[0])*(point2[1]-dog[1]) - (i[1]-dog[1])*(point2[0]-dog[0])
            if (d1 < 0) and (d2 >= 0):
                seznam_up.append(i)
            elif (d1 >= 0) and (d2 > 0):
                seznam_right.append(i)
            elif (d1 > 0) and (d2 <= 0):
                seznam_down.append(i)
            elif (d1 <= 0) and (d2 < 0):
                seznam_left.append(i)
            else: nic += 1
        seznam = [seznam_up, seznam_right, seznam_down, seznam_left]
        no_of_areas = 0
        for j in seznam:
            if len(j) != 0:
                no_of_areas += 1

        print(no_of_areas)
        reward = rewards[no_of_areas]

        return reward

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
        plt.scatter( dog[0],  dog[1], 
                    c='r', s=50, label='Dog')
        plt.scatter(x,  y, 
                    c='b', s=50, label='Sheep')

        plt.title('Shepherding')
        plt.xlim([0, self.field_size*size])
        plt.ylim([0, self.field_size*size])
        plt.legend()
        plt.draw()
        plt.pause(0.5)
