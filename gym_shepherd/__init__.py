from gym.envs.registration import register

register(
    id='Shepherd-v0',
    entry_point='gym_shepherd.envs.shepherd_env:ShepherdEnv',
)
register(
    id='Shepherd-extrahard-v0',
    entry_point='gym_shepherd.envs.shepherd_extrahard_env:ShepherdExtraHardEnv',
)