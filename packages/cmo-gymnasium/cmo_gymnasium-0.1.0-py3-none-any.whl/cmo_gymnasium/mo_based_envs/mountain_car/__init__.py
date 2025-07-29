from cmo_gymnasium.utils.registration import register


register(
    id="cmo-mountaincar-v0",
    entry_point="cmo_gymnasium.mo_based_envs.mountain_car.mountain_car:MOMountainCar",
    max_episode_steps=200,
)

register(
    id="cmo-mountaincar-3d-v0",
    entry_point="cmo_gymnasium.mo_based_envs.mountain_car.mountain_car:MOMountainCar",
    max_episode_steps=200,
    kwargs={"add_speed_objective": True, "merge_move_penalty": True},
)

register(
    id="cmo-mountaincar-timemove-v0",
    entry_point="cmo_gymnasium.mo_based_envs.mountain_car.mountain_car:MOMountainCar",
    max_episode_steps=200,
    kwargs={"merge_move_penalty": True},
)

register(
    id="cmo-mountaincar-timespeed-v0",
    entry_point="cmo_gymnasium.mo_based_envs.mountain_car.mountain_car:MOMountainCar",
    max_episode_steps=200,
    kwargs={"remove_move_penalty": True, "add_speed_objective": True},
)
