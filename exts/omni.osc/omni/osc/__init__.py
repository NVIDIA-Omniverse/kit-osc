# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import omni.kit.pipapi

# python-osc:
# - SWIPAT request: http://nvbugs/3684871
# - A copy of the source is forked to https://github.com/NVIDIA-Omniverse/python-osc
# - The dependency vendored and installed from exts/omni.osc/vendor/python_osc-1.8.0-py3-none-any.whl
omni.kit.pipapi.install(
    package="python-osc", module="pythonosc", use_online_index=False, ignore_cache=True, ignore_import_check=False
)

from pythonosc import *  # noqa: F401

from .core import *  # noqa: F401,F403
from .extension import *  # noqa: F401,F403
from .server import *  # noqa: F401,F403

# NOTE(jshrake): omni.graph is an optional dependency so handle the case
# that the below import fails
try:
    from .ogn import *
except Exception as e:
    print(f"omni.osc failed to import OGN due to {e}")
    pass
