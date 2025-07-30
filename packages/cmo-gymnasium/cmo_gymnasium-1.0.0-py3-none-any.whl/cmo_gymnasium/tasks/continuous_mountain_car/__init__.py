from cmo_gymnasium.utils.registration import register


register(
    id="cmo-mountaincarcontinuous-v0",
    entry_point="cmo_gymnasium.mo_based_envs.continuous_mountain_car.continuous_mountain_car:MOContinuousMountainCar",
    max_episode_steps=999,
)
