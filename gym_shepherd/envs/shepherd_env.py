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
        dog = (20,20)

        #print(herd)

        return herd, dog

    def state_translation_fun(self):

        zf = [1, 2, 3, 4]
        states = [ i*100 + j*10 + k for i in zf for j in zf for k in zf]
        #print(states[1:15])
        
        d = { states[i] : i  for i in range(64)}
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
        
        self.sheep_num = 100
        self.field_size = 50
        self.herd, self.dog = self.init_sheep_table()

        self.dog_move_size = 2 
        self.dog_influence = int(self.field_size/8)
        self.dog_influence_rm = int(self.field_size/4)

        self.max_num_of_steps = 100
        self.target_distance = int(sqrt(self.sheep_num)) + 2
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
        print(str(self.curr_episode)+" "+str(self.current_step))
        
        action = self._take_action(action)
        
        # get reward and state 
        # TODO state return 
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
        areas  = self.areas() * 4
        dog_sheep = self.closenes_sheep_dog() * 4
        sheep_sheep = self.closenes_sheep_sheep('discrete') * 4

        if areas < 2:
            areas += 1
        if dog_sheep < 2:
            dog_sheep += 1
        if sheep_sheep <2:
            sheep_sheep += 1

        #print([areas,dog_sheep,sheep_sheep])
        
        state = areas * 100 + dog_sheep * 10 + sheep_sheep
        state_trans = self.state_translation_dict[state] 
        print("new state: ", end=" ")
        print(state_trans)

        return state_trans
        
    def _get_reward(self):
            """Return reward based on action of the dog"""
            # območja, ovca pes, ovca ovca
            dog_sheep = self.closenes_sheep_dog() 
            sheep_sheep = self.closenes_sheep_sheep()
            reward = 0.25 * dog_sheep + sheep_sheep
            print("Reward: "+ str(0.25 * dog_sheep) +" "+ str(sheep_sheep))
            return reward

    def _take_action(self, action):
        """Update position of dog based on action and env"""
        # dog movement & influenced sheep movement accordingly
        self._take_action_dog(action)
        self._take_action_dog(action)
         # sheep movement (all sheep)
        self._update_environment()

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
        plt.scatter(x,  y, 
                    c='b', s=50, label='Sheep')

        plt.title('Shepherding')
        plt.xlim([0, self.field_size*size])
        plt.ylim([0, self.field_size*size])
        #plt.legend()
        plt.draw()
        plt.pause(0.05)

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
    def closenes_sheep_sheep(self, type='continuous'):

        field_size = self.field_size
        goal_radius = self.target_distance

         # continum

        max_radius = field_size*sqrt(2)/2
        center, max_sheep_radius = self.dist_herd_center()
        max_sheep_radius = max_sheep_radius - goal_radius

        reward = 1 - (max_sheep_radius/max_radius)
        # reward = 1/(max_sheep_radius/max_radius)

        if type == 'continuous':
            return reward
       
        # dicrete
        
        h = (field_size*sqrt(2)-goal_radius)/6
        max_distance = max_sheep_radius - goal_radius
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

        reward = rewards[no_of_areas]

        return reward


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

    def clean_options(self, sheep_options):
        for option in sheep_options:
            if option == self.dog:
                sheep_options.remove(option)
            elif option in self.herd:
                sheep_options.remove(option)
            elif not self.is_on_lawn(option):
                sheep_options.remove(option)
        return sheep_options

    def is_on_lawn(self, sheep):
        x, y = sheep
        return(0<=y<self.field_size and 0<=x<self.field_size)

