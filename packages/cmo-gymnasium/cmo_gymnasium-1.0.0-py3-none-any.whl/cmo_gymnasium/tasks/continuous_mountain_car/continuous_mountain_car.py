import math
from typing import Optional

import numpy as np
from gymnasium import spaces
from gymnasium.envs.classic_control.continuous_mountain_car import (
    Continuous_MountainCarEnv,
)
from gymnasium.utils import EzPickle

import cmo_gymnasium.utils.registration as cmo_gym

class MOContinuousMountainCar(Continuous_MountainCarEnv, EzPickle):
    """
    A continuous version of the MountainCar environment, where the goal is to reach the top of the mountain.

    See [source](https://gymnasium.farama.org/environments/classic_control/mountain_car_continuous/) for more information.

    ## Reward space:
    The reward space is a 2D vector containing the time penalty and the fuel reward.
    - time penalty: -1.0 for each time step
    - fuel reward: -||action||^2 , i.e. the negative of the norm of the action vector

    ## Cost space:
    The cost space is a 2D vector containing:
    - Cost[0]: 1.0 if the car is in the initial x-axis[-0.6, -0.4] position, else 0.0
    - Cost[1]: 1.0 if the mountain car collides with left wall x = -1.2, else 0.0
    """

    def __init__(self, render_mode: Optional[str] = None, goal_velocity=0):
        super().__init__(render_mode, goal_velocity)
        EzPickle.__init__(self, render_mode, goal_velocity)

        self.reward_space = spaces.Box(low=np.array([-1.0, -1.0]), high=np.array([0.0, 0.0]), dtype=np.float32)
        self.reward_dim = 2
        # Initialize cost vector
        self.costs_dim = 2
        self.costs_space = spaces.Box(low=0.0, high=1.0, shape=(self.costs_dim,), dtype=np.float32)

        self.num_collisions = 0   # Counter for collisions with the wall

    def reset(self, seed=None, options=None):
        """Reset environment and episode-specific counters"""
        # Call parent reset
        observation, info = super().reset(seed=seed, options=options)
        
        # Reset episode-specific counters
        self.num_collisions = 0
        
        return observation, info

    def step(self, action: np.ndarray):
        # Essentially a copy paste from original env, except the rewards

        position = self.state[0]
        velocity = self.state[1]
        force = min(max(action[0], self.min_action), self.max_action)

        velocity += force * self.power - 0.0025 * math.cos(3 * position)
        if velocity > self.max_speed:
            velocity = self.max_speed
        if velocity < -self.max_speed:
            velocity = -self.max_speed
        position += velocity
        if position > self.max_position:
            position = self.max_position
        if position < self.min_position:
            position = self.min_position
        if position == self.min_position and velocity < 0:
            velocity = 0

        # Convert a possible numpy bool to a Python bool.
        terminated = bool(position >= self.goal_position and velocity >= self.goal_velocity)

        reward = np.zeros(2, dtype=np.float32)
        # Time reward is negative at all timesteps except when reaching the goal
        if terminated:
            reward[0] = 0.0
        else:
            reward[0] = -1.0

        # Actions cost fuel, which we want to optimize too
        reward[1] = -math.pow(action[0], 2)

        self.state = np.array([position, velocity], dtype=np.float32)

        # Costs

        costs = np.zeros(self.costs_dim, dtype=np.float32)

        # Cost of being in the initial x-axis position 
        # Initial position of the car is ~unif(-0,6, -0.4)
        costs[0] = 1.0 if (position >= -0.6 and position <= -0.4) else 0.0 

        # Cost of colliding with the wall (inelastic collision)
        if position == self.min_position:
            self.num_collisions += 1.0

        if self.num_collisions > 0:
            costs[1] = 1.0

        if self.render_mode == "human":
            self.render()
        return self.state, reward, costs, terminated, False, {}


if __name__ == "__main__":
    env = cmo_gym.make("cmo-mountaincarcontinuous-v0", render_mode="human")
    terminated = False
    env.reset()
    while True:
        obs, r, costs, terminated, truncated, _ = env.step(env.action_space.sample())
        print(f"Observation: {obs}, Reward: {r}, Costs: {costs}, Terminated: {terminated}, Truncated: {truncated}")
