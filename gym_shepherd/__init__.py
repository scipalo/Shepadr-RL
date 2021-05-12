from gym.envs.registration import register

register(
    id='shepherd-v0',
    entry_point='gym_shepherd.envs:FooEnv',
)
register(
    id='shepherd-extrahard-v0',
    entry_point='gym_shepherd.envs:FooExtraHardEnv',
)