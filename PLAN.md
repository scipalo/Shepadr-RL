# Shepadr-Plan

SHEPARD

DOG: 

actions: right, left, up, down, hitro, počasi (smer x hitrost)
movement: Q _tabela (expotation) + random (exploration)
hitrost psa: Vp
stanja (pozicija psa x oblika črede): 
    • pozicija glede na ovce (obdanost)
    • pozicija glede na težišče črede (?)
    • razpršenost/oblika črede 

negativne nagrade:
    • pes je obdan z ovcami
    • ovce so razpršene (kako se to matematično optimalno izračuna)

SHEEP:

actions: right, left, up, down
movement: 
    • vpliv psa: proč od psa
    • ni vpliva psa: random (opt?)
    • zaporedno ali vzporedno (na enem polju je lahko le ena ovca)
      
pozicija: tabela ničel in enic

hitrost ovce: Vo = 1

Def: 
    • vpliv psa = razdalja(pes, ovca) = x



IMPLEMENTACIJA: Na podlagi taksija
POTEK: Manjšanje epsilona (manj raziskovanja)

LINKI:

Video zbiranja ovc: https://www.youtube.com/watch?v=tDQw21ntR64
Taksi (poganjanje primera): https://l.facebook.com/l.php?u=https%3A%2F%2Fwww.learndatasci.com%2Ftutorials%2Freinforcement-q-learning-scratch-python-openai-gym%2F%3Ffbclid%3DIwAR0flZORv0L11cg0s3JROhxwtdG3gfOT3hzikXiJuHOrR6b0RNj0tOlnJNUh=AT2dp1RNTSOxve-YqS98mE78Ti5sdprD77VkY4EbmqG5bwwDujaeCSfRCnkzDlrP2Plwql1B0YNhw1pxAwo9QG6eD74aXiD_kh_2LcLQJl_Ws5hR_zpmd8p3w4I9Ng 

Shepherd gym example: https://github.com/buntyke/shepherd_gym/blob/master/README.md
Socer gym example: https://github.com/openai/gym-soccer
Our own environment: 
    https://github.com/openai/gym/blob/master/docs/creating-environments.md
    https://stackoverflow.com/questions/45068568/how-to-create-a-new-gym-environment-in-openai
Tutorial own environment: 
    https://towardsdatascience.com/creating-a-custom-openai-gym-environment-for-stock-trading-be532be3910e


REZULTATI

"""
1. std dev (sheep sheep)
dolžina najdaljše vce do centra ovc ne pomaga nič

        # continum max radius (not working)

        # center, max_sheep_radius = self.dist_herd_center()
        # max_sheep_radius = max_sheep_radius - goal_radius
        # max_radius = field_size*sqrt(2)/2
        # reward = 1 - (max_sheep_radius/max_radius)
        # reward = 1/(max_sheep_radius/max_radius)

spremenili smo v VARIANCO ovc oddaljenosti od centra

2. (dog sheep) oddaljenost od centra ovc

razdalja med najbližjo ovco in psom moivira, da nanje vpliva, ampak ne prinese rezultatov
spremenili smo v oddaljenost od centra ovc

3. smeri 
območj skrbijo, da se pes postavi v kot, da ima ovce le na dveh straneh, drugače n eprinese nič 
spremenili smo v osem smernih vektorjev (dog, center) da dobimo relacijo s med pozicijo centra in psa in s tem spreminjanje smeri