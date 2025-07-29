from cmo_gymnasium.utils.registration import register

register(
    id="cmo-lunar-lander-v0",
    entry_point="cmo_gymnasium.mo_based_envs.lunar_lander.lunar_lander:MOLunarLander",
    max_episode_steps=1000,
)

register(
    id="cmo-lunar-lander-continuous-v0",
    entry_point="cmo_gymnasium.mo_based_envs.lunar_lander.lunar_lander:MOLunarLander",
    max_episode_steps=1000,
    kwargs={"continuous": True},
)