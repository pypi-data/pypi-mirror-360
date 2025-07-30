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
"""Tasks in CMO-Gymnasium."""

from cmo_gymnasium.tasks.safe_navigation.button.button_level0 import ButtonLevel0
from cmo_gymnasium.tasks.safe_navigation.button.button_level1 import ButtonLevel1
from cmo_gymnasium.tasks.safe_navigation.button.button_level2 import ButtonLevel2
from cmo_gymnasium.tasks.safe_navigation.circle.circle_level0 import CircleLevel0
from cmo_gymnasium.tasks.safe_navigation.circle.circle_level1 import CircleLevel1
from cmo_gymnasium.tasks.safe_navigation.circle.circle_level2 import CircleLevel2
from cmo_gymnasium.tasks.safe_navigation.goal.goal_level0 import GoalLevel0
from cmo_gymnasium.tasks.safe_navigation.goal.goal_level1 import GoalLevel1
from cmo_gymnasium.tasks.safe_navigation.goal.goal_level2 import GoalLevel2
from cmo_gymnasium.tasks.safe_navigation.push.push_level0 import PushLevel0
from cmo_gymnasium.tasks.safe_navigation.push.push_level1 import PushLevel1
from cmo_gymnasium.tasks.safe_navigation.push.push_level2 import PushLevel2
from cmo_gymnasium.tasks.safe_navigation.run.run import RunLevel0
from cmo_gymnasium.tasks.safe_vision.fading.fading_level0 import (
    FadingEasyLevel0,
    FadingHardLevel0,
)
from cmo_gymnasium.tasks.safe_vision.fading.fading_level1 import (
    FadingEasyLevel1,
    FadingHardLevel1,
)
from cmo_gymnasium.tasks.safe_vision.fading.fading_level2 import (
    FadingEasyLevel2,
    FadingHardLevel2,
)
from cmo_gymnasium.tasks.safe_vision.race.race_level0 import RaceLevel0
from cmo_gymnasium.tasks.safe_vision.race.race_level1 import RaceLevel1
from cmo_gymnasium.tasks.safe_vision.race.race_level2 import RaceLevel2

from cmo_gymnasium.tasks.deep_sea_treasure.deep_sea_treasure import DeepSeaTreasure
from cmo_gymnasium.tasks.four_room.cmo_four_room import CMOFourRoom
from cmo_gymnasium.tasks.continuous_mountain_car.continuous_mountain_car import Continuous_MountainCarEnv