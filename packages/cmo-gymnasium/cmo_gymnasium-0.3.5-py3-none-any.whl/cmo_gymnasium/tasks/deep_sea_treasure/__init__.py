# from cmo_gymnasium.utils.registration import register

# from cmo_gymnasium.tasks.deep_sea_treasure.deep_sea_treasure import (
#     CONCAVE_MAP,
#     MIRRORED_MAP,
#     CONSTRAINED_MAP,
#     CONSTRAINED_CONCAVE_MAP,
#     CONSTRAINED_MIRRORED_MAP,
# )

# register(
#     id="cmo-deep-sea-treasure-v0",
#     entry_point="cmo_gymnasium.mo_based_envs.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
#     max_episode_steps=100,
#     kwargs={"dst_map": CONSTRAINED_MAP},
# )

# register(
#     id="cmo-deep-sea-treasure-concave-v0",
#     entry_point="cmo_gymnasium.mo_based_envs.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
#     max_episode_steps=100,
#     kwargs={"dst_map": CONSTRAINED_CONCAVE_MAP},
# )

# register(
#     id="cmo-deep-sea-treasure-mirrored-v0",
#     entry_point="cmo_gymnasium.mo_based_envs.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
#     max_episode_steps=100,
#     kwargs={"dst_map": CONSTRAINED_MIRRORED_MAP},
# )

# register(
#     id="deep-sea-treasure-v0",
#     entry_point="cmo_gymnasium.mo_based_envs.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
#     max_episode_steps=100,
# )

# register(
#     id="deep-sea-treasure-concave-v0",
#     entry_point="cmo_gymnasium.mo_based_envs.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
#     max_episode_steps=100,
#     kwargs={"dst_map": CONCAVE_MAP},
# )

# register(
#     id="deep-sea-treasure-mirrored-v0",
#     entry_point="cmo_gymnasium.mo_based_envs.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
#     max_episode_steps=100,
#     kwargs={"dst_map": MIRRORED_MAP},
# )