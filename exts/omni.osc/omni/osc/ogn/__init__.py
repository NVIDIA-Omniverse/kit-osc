# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

"""
Dynamically import every file in a directory tree that looks like a Python Ogn Node.
This includes linked directories, which is the mechanism by which nodes can be hot-reloaded from the source tree.
"""

# Required to register nodes in Kit 104
try:
    import omni.graph.core as og
    og.register_ogn_nodes(__file__, "omni.osc")
except Exception:
    # Swallow any exceptions
    pass
