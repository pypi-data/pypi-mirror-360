# from pathlib import Path
# from cmo_gymnasium.utils.registration import register

# register(
#     id="cmo-minecart-v0",
#     entry_point="cmo_gymnasium.minecart.minecart:CMOMinecart",
#     max_episode_steps=1000,
# )

# register(
#     id="cmo-minecart-rgb-v0",
#     entry_point="cmo_gymnasium.minecart.minecart:CMOMinecart",
#     kwargs={"image_observation": True},
#     nondeterministic=True,  # This is a nondeterministic environment due to the random placement of the mines
#     max_episode_steps=1000,
# )

# register(
#     id="cmo-minecart-deterministic-v0",
#     entry_point="cmo_gymnasium.minecart.minecart:CMOMinecart",
#     kwargs={"config": str(Path(__file__).parent.absolute()) + "/mine_config_det.json"},
#     max_episode_steps=1000,
# )
