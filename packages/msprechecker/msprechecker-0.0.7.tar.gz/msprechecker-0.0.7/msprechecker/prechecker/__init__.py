# Copyright (c) 2025-2025 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = [
    "CHECKERS",
]

from msprechecker.prechecker.config_checker import (
    mindie_config_checker,
    ranktable_checker,
    model_config_checker,
    user_config_checker,
    mindie_env_checker
)
from msprechecker.prechecker.env_checker import env_checker
from msprechecker.prechecker.system_checker import system_checker_instance
from msprechecker.prechecker.hccl_checker import hccl_checker_instance
from msprechecker.prechecker.model_checker import model_size_checker, model_sha256_collecter
from msprechecker.prechecker.utils import CHECKER_TYPES
from msprechecker.prechecker.hardware_capacity.cpu_checker import cpu_checker
from msprechecker.prechecker.hardware_capacity.npu_checker import npu_checker
from msprechecker.prechecker.hardware_capacity.network_checker import network_checker_instance

CHECKERS = {
    CHECKER_TYPES.basic: [
        system_checker_instance,
        env_checker,
        mindie_config_checker,
        ranktable_checker,
        user_config_checker,
        mindie_env_checker
    ],
    CHECKER_TYPES.hccl: [hccl_checker_instance],
    CHECKER_TYPES.model: [model_config_checker, model_size_checker, model_sha256_collecter],
    CHECKER_TYPES.hardware: [cpu_checker, npu_checker, network_checker_instance]
}

CHECKERS[CHECKER_TYPES.all] = []
for key, checker in CHECKERS.items():
    if key != CHECKER_TYPES.all:
        CHECKERS[CHECKER_TYPES.all].extend(checker)

CHECKER_INFOS = {
    CHECKER_TYPES.basic: "checking env / system info",
    CHECKER_TYPES.hccl: "checking hccl connection status",
    CHECKER_TYPES.model: "checking or comparing model size and sha256sum value",
    CHECKER_TYPES.hardware: "checking CPU/NPU hardware computing capacity",
    CHECKER_TYPES.all: "checking all",
}

CHECKER_INFOS_STR = "; ".join([f"{kk} for {vv}" for kk, vv in CHECKER_INFOS.items()])
