# Copyright 2022-2023 OmniSafe Team. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""CMO-Gymnasium Environments."""

import copy

from gymnasium import make as gymnasium_make
from gymnasium import register as gymnasium_register

from cmo_gymnasium import vector
from cmo_gymnasium.tasks.safe_multi_agent.safe_mujoco_multi import make_ma
from cmo_gymnasium.utils.registration import make, register

from pathlib import Path

from cmo_gymnasium.tasks.deep_sea_treasure.deep_sea_treasure import (
    CONCAVE_MAP,
    MIRRORED_MAP,
    CONSTRAINED_MAP,
    CONSTRAINED_CONCAVE_MAP,
    CONSTRAINED_MIRRORED_MAP,
)


__all__ = [
    'register',
    'make',
    'gymnasium_make',
    'gymnasium_register',
    'mo_envs',
]

VERSION = 'v0'
ROBOT_NAMES = ('Point', 'Car', 'Doggo', 'Racecar', 'Ant')
MAKE_VISION_ENVIRONMENTS = True
MAKE_DEBUG_ENVIRONMENTS = True

# ========================================
# Helper Methods for Easy Registration
# ========================================

PREFIX = 'CMO'

robots = ROBOT_NAMES


def __register_helper(env_id, entry_point, spec_kwargs=None, **kwargs):
    """Register a environment to both CMO-Gymnasium and Gymnasium registry."""
    env_name, dash, version = env_id.partition('-')
    if spec_kwargs is None:
        spec_kwargs = {}

    register(
        id=env_id,
        entry_point=entry_point,
        kwargs=spec_kwargs,
        **kwargs,
    )
    gymnasium_register(
        id=f'{env_name}Gymnasium{dash}{version}',
        entry_point='cmo_gymnasium.wrappers.gymnasium_conversion:make_gymnasium_environment',
        kwargs={'env_id': f'{env_name}Gymnasium{dash}{version}', **copy.deepcopy(spec_kwargs)},
        **kwargs,
    )


def __combine(tasks, agents, max_episode_steps):
    """Combine tasks and agents together to register environment tasks."""
    for task_name, task_config in tasks.items():
        # Vector inputs
        for robot_name in agents:
            env_id = f'{PREFIX}{robot_name}{task_name}-{VERSION}'
            combined_config = copy.deepcopy(task_config)
            combined_config.update({'agent_name': robot_name})

            __register_helper(
                env_id=env_id,
                entry_point='cmo_gymnasium.builder:Builder',
                spec_kwargs={'config': combined_config, 'task_id': env_id},
                max_episode_steps=max_episode_steps,
            )

            if MAKE_VISION_ENVIRONMENTS:
                # Vision inputs
                vision_env_name = f'{PREFIX}{robot_name}{task_name}Vision-{VERSION}'
                vision_config = {
                    'observe_vision': True,
                    'observation_flatten': False,
                }
                vision_config.update(combined_config)
                __register_helper(
                    env_id=vision_env_name,
                    entry_point='cmo_gymnasium.builder:Builder',
                    spec_kwargs={'config': vision_config, 'task_id': env_id},
                    max_episode_steps=max_episode_steps,
                )

            if MAKE_DEBUG_ENVIRONMENTS and robot_name in ['Point', 'Car', 'Racecar']:
                # Keyboard inputs for debugging
                debug_env_name = f'{PREFIX}{robot_name}{task_name}Debug-{VERSION}'
                debug_config = {'debug': True}
                debug_config.update(combined_config)
                __register_helper(
                    env_id=debug_env_name,
                    entry_point='cmo_gymnasium.builder:Builder',
                    spec_kwargs={'config': debug_config, 'task_id': env_id},
                    max_episode_steps=max_episode_steps,
                )


# ----------------------------------------
# Safety Navigation
# ----------------------------------------

# Button Environments
# ----------------------------------------
button_tasks = {'Button0': {}, 'Button1': {}, 'Button2': {}}
__combine(button_tasks, robots, max_episode_steps=1000)


# Push Environments
# ----------------------------------------
push_tasks = {'Push0': {}, 'Push1': {}, 'Push2': {}}
__combine(push_tasks, robots, max_episode_steps=1000)


# Goal Environments
# ----------------------------------------
goal_tasks = {'Goal0': {}, 'Goal1': {}, 'Goal2': {}}
__combine(goal_tasks, robots, max_episode_steps=1000)


# Circle Environments
# ----------------------------------------
circle_tasks = {'Circle0': {}, 'Circle1': {}, 'Circle2': {}}
__combine(circle_tasks, robots, max_episode_steps=500)


# Run Environments
# ----------------------------------------
run_tasks = {'Run0': {}}
__combine(run_tasks, robots, max_episode_steps=500)


# ----------------------------------------
# Safety Vision
# ----------------------------------------

# Race Environments
# ----------------------------------------
race_tasks = {
    'Race0': {'floor_conf.type': 'village'},
    'Race1': {'floor_conf.type': 'village'},
    'Race2': {'floor_conf.type': 'village'},
}
__combine(race_tasks, robots, max_episode_steps=500)


# Fading Environments
# ----------------------------------------
fading_tasks = {'FadingEasy0': {}, 'FadingEasy1': {}, 'FadingEasy2': {}}
__combine(fading_tasks, robots, max_episode_steps=1000)

fading_tasks = {'FadingHard0': {}, 'FadingHard1': {}, 'FadingHard2': {}}
__combine(fading_tasks, robots, max_episode_steps=1000)


# ----------------------------------------
# Safety Velocity
# ----------------------------------------

# __register_helper(
#     env_id='SafetyHalfCheetahVelocity-v0',
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_half_cheetah_velocity_v0:SafetyHalfCheetahVelocityEnv',
#     max_episode_steps=1000,
#     reward_threshold=4800.0,
# )

# __register_helper(
#     env_id='SafetyHopperVelocity-v0',
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_hopper_velocity_v0:SafetyHopperVelocityEnv',
#     max_episode_steps=1000,
#     reward_threshold=3800.0,
# )

# __register_helper(
#     env_id='SafetySwimmerVelocity-v0',
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_swimmer_velocity_v0:SafetySwimmerVelocityEnv',
#     max_episode_steps=1000,
#     reward_threshold=360.0,
# )

# __register_helper(
#     env_id='SafetyWalker2dVelocity-v0',
#     max_episode_steps=1000,
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_walker2d_velocity_v0:SafetyWalker2dVelocityEnv',
# )

# __register_helper(
#     env_id='SafetyAntVelocity-v0',
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_ant_velocity_v0:SafetyAntVelocityEnv',
#     max_episode_steps=1000,
#     reward_threshold=6000.0,
# )

# __register_helper(
#     env_id='SafetyHumanoidVelocity-v0',
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_humanoid_velocity_v0:SafetyHumanoidVelocityEnv',
#     max_episode_steps=1000,
# )

# __register_helper(
#     env_id='SafetyHalfCheetahVelocity-v1',
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_half_cheetah_velocity_v1:SafetyHalfCheetahVelocityEnv',
#     max_episode_steps=1000,
#     reward_threshold=4800.0,
# )

# __register_helper(
#     env_id='SafetyHopperVelocity-v1',
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_hopper_velocity_v1:SafetyHopperVelocityEnv',
#     max_episode_steps=1000,
#     reward_threshold=3800.0,
# )

# __register_helper(
#     env_id='SafetySwimmerVelocity-v1',
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_swimmer_velocity_v1:SafetySwimmerVelocityEnv',
#     max_episode_steps=1000,
#     reward_threshold=360.0,
# )

# __register_helper(
#     env_id='SafetyWalker2dVelocity-v1',
#     max_episode_steps=1000,
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_walker2d_velocity_v1:SafetyWalker2dVelocityEnv',
# )

# __register_helper(
#     env_id='SafetyAntVelocity-v1',
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_ant_velocity_v1:SafetyAntVelocityEnv',
#     max_episode_steps=1000,
#     reward_threshold=6000.0,
# )

# __register_helper(
#     env_id='SafetyHumanoidVelocity-v1',
#     entry_point='cmo_gymnasium.tasks.safe_velocity.safety_humanoid_velocity_v1:SafetyHumanoidVelocityEnv',
#     max_episode_steps=1000,
# )

# ---------------------------------------- 
# MO-Based Environments

__register_helper(
    env_id='cmo-mountaincarcontinuous-v0',
    entry_point='cmo_gymnasium.tasks.continuous_mountain_car.continuous_mountain_car:MOContinuousMountainCar',
    max_episode_steps=1000,
)

__register_helper(
    env_id='cmo-mountaincar-v0',
    entry_point='cmo_gymnasium.tasks.mountain_car.mountain_car:CMOMountainCar',
    max_episode_steps=1000,
)

__register_helper(
    env_id="cmo-mountaincar-3d-v0",
    entry_point="cmo_gymnasium.tasks.mountain_car.mountain_car:CMOMountainCar",
    max_episode_steps=200,
    spec_kwargs={"add_speed_objective": True, "merge_move_penalty": True},
)

__register_helper(
    env_id="cmo-mountaincar-timemove-v0",
    entry_point="cmo_gymnasium.tasks.mountain_car.mountain_car:CMOMountainCar",
    max_episode_steps=200,
    spec_kwargs={"merge_move_penalty": True},
)

__register_helper(
    env_id="cmo-mountaincar-timespeed-v0",
    entry_point="cmo_gymnasium.tasks.mountain_car.mountain_car:CMOMountainCar",
    max_episode_steps=200,
    spec_kwargs={"remove_move_penalty": True, "add_speed_objective": True},
)

__register_helper(
    env_id="cmo-deep-sea-treasure-v0",
    entry_point="cmo_gymnasium.tasks.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
    max_episode_steps=100,
    spec_kwargs={"dst_map": CONSTRAINED_MAP},
)

__register_helper(
    env_id="cmo-deep-sea-treasure-concave-v0",
    entry_point="cmo_gymnasium.tasks.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
    max_episode_steps=100,
    spec_kwargs={"dst_map": CONSTRAINED_CONCAVE_MAP},
)

__register_helper(
    env_id="cmo-deep-sea-treasure-mirrored-v0",
    entry_point="cmo_gymnasium.tasks.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
    max_episode_steps=100,
    spec_kwargs={"dst_map": CONSTRAINED_MIRRORED_MAP},
)

__register_helper(
    env_id="deep-sea-treasure-v0",
    entry_point="cmo_gymnasium.tasks.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
    max_episode_steps=100,
)

__register_helper(
    env_id="deep-sea-treasure-concave-v0",
    entry_point="cmo_gymnasium.tasks.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
    max_episode_steps=100,
    spec_kwargs={"dst_map": CONCAVE_MAP},
)

__register_helper(
    env_id="deep-sea-treasure-mirrored-v0",
    entry_point="cmo_gymnasium.tasks.deep_sea_treasure.deep_sea_treasure:DeepSeaTreasure",
    max_episode_steps=100,
    spec_kwargs={"dst_map": MIRRORED_MAP},
)

__register_helper(
    env_id="cmo-four-room-v0",
    entry_point="cmo_gymnasium.tasks.four_room.cmo_four_room:CMOFourRoom",
    max_episode_steps=200,
)

__register_helper(
    env_id="cmo-FrozenLake-v0",
    entry_point="cmo_gymnasium.tasks.frozen_lake.frozen_lake:CMOFrozenLakeEnv",
    max_episode_steps=200,
)

__register_helper(
    env_id="cmo-lunar-lander-v0",
    entry_point="cmo_gymnasium.tasks.lunar_lander.lunar_lander:CMOLunarLander",
    max_episode_steps=1000,
)

__register_helper(
    env_id="cmo-lunar-lander-continuous-v0",
    entry_point="cmo_gymnasium.tasks.lunar_lander.lunar_lander:CMOLunarLander",
    max_episode_steps=1000,
    spec_kwargs={"continuous": True},
)

__register_helper(
    env_id="cmo-minecart-v0",
    entry_point="cmo_gymnasium.tasks.minecart.minecart:CMOMinecart",
    max_episode_steps=1000,
)

__register_helper(
    env_id="cmo-minecart-rgb-v0",
    entry_point="cmo_gymnasium.tasks.minecart.minecart:CMOMinecart",
    max_episode_steps=1000,
    spec_kwargs={"image_observation": True},
    nondeterministic=True,
)

__register_helper(
    env_id="cmo-minecart-deterministic-v0",
    entry_point="cmo_gymnasium.tasks.minecart.minecart:CMOMinecart",
    max_episode_steps=1000,
    spec_kwargs={
        "config": str(Path(__file__).parent / "tasks" / "minecart" / "mine_config.json")
    },
)

__register_helper(
    env_id="cmo-taxi-v0",
    entry_point="cmo_gymnasium.tasks.taxi.taxi:CMOTaxiEnv",
    reward_threshold=8, 
    max_episode_steps=200,
)

# List of MO-based environment IDs as registered below
mo_envs = [
    'cmo-mountaincarcontinuous-v0',
    'cmo-deep-sea-treasure-v0',
    'cmo-deep-sea-treasure-concave-v0',
    'cmo-deep-sea-treasure-mirrored-v0',
    'deep-sea-treasure-v0',
    'deep-sea-treasure-concave-v0',
    'deep-sea-treasure-mirrored-v0',
    'cmo-four-room-v0',
    'cmo-FrozenLake-v0',
    'cmo-lunar-lander-v0',
    'cmo-lunar-lander-continuous-v0',
    'cmo-minecart-v0',
    'cmo-minecart-rgb-v0',
    'cmo-minecart-deterministic-v0',
    'cmo-mountaincar-v0',
    'cmo-mountaincar-3d-v0',
    'cmo-mountaincar-timemove-v0',
    'cmo-mountaincar-timespeed-v0',
    'cmo-taxi-v0',
]
