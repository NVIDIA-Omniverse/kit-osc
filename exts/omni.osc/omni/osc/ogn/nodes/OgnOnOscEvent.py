# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

"""
This is the implementation of the OGN node defined in OgnOnOscEvent.ogn
This implementation is inspired by the OgnOnCustomEvent node
See https://gitlab-master.nvidia.com/omniverse/kit/-/blob/master/kit/source/extensions/omni.graph.action/nodes/OgnOnCustomEvent.py # noqa E501
"""
import re
from typing import Any, List, Union

import carb
import carb.events
import carb.profiler
import omni.graph.core as og
import omni.osc

from .. import OgnOnOscEventDatabase


class OgnOnOscEventInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information."""
        # This subscription object controls the lifetime of our callback, it will be
        # cleaned up automatically when our node is destroyed
        self.sub = None
        # Set when the callback has triggered
        self.is_set = False
        # The last event received
        self.event: Union[None, carb.events.IEvent] = None
        # The node instance handle
        self.node = None
        # The regex used to match the OSC address path
        self.osc_path_regex = ""
        # The compiled regex pattern
        self.osc_path_regex_pattern = None

    @carb.profiler.profile
    def on_event(self, event: carb.events.IEvent):
        """The event callback"""
        if event is None:
            return

        # Only handle messages with a path that matches the OSC address path regex
        osc_addr, _ = omni.osc.osc_message_from_carb_event(event)
        if self.osc_path_regex_pattern is None or not self.osc_path_regex_pattern.match(osc_addr):
            return

        self.is_set = True
        self.event = event
        # Tell the evaluator we need to be computed
        if self.node.is_valid():
            self.node.request_compute()

    @carb.profiler.profile
    def first_time_subscribe(self, node: og.Node, osc_path_regex: str) -> bool:
        """Checked call to set up carb subscription
        Args:
            node: The node instance
            event_name: The name of the carb event
        Returns:
            True if we subscribed, False if we are already subscribed
        """

        if self.osc_path_regex != osc_path_regex:
            # osc path regex changed since we last subscribed, re-compile
            try:
                self.osc_path_regex_pattern = re.compile(osc_path_regex)
                self.osc_path_regex = osc_path_regex
            except Exception as e:
                carb.log_error(f"Error compiling OSC Address Path Regex '{osc_path_regex}': {e}")

        if self.sub is None:
            self.sub = omni.osc.subscribe_to_osc_event_stream(self.on_event)
            self.node = node
            return True

        return False

    def try_pop_event(self) -> Union[None, carb.events.IEvent]:
        """Pop the last event received, or None if there is no event to pop"""
        if self.is_set:
            self.is_set = False
            event = self.event
            self.event = None
            return event
        return None


# ======================================================================


class OgnOnOscEvent:
    """
    This node triggers when an OSC event is received that matches the OSC address path regex.
    """

    @staticmethod
    def internal_state():
        """Returns an object that will contain per-node state information"""
        return OgnOnOscEventInternalState()

    @staticmethod
    def release(node):
        state = OgnOnOscEventDatabase.OgnOnOscEventDatabase.per_node_internal_state(node)
        if state.sub:
            state.sub.unsubscribe()
        state.sub = None

    @staticmethod
    def validate_osc_message_args(args: List[Any]) -> bool:
        """
        Returns true if the OSC message arguments has the shape of List[float]
        """
        all_args_are_float = all(isinstance(arg, float) for arg in args)
        return all_args_are_float

    @staticmethod
    def resolve_osc_message_args_type(node: og.Node, args: List[Any]) -> bool:
        """
        Attempt to resolve the node outputs:args attribute and return True if successful
        """
        args_attr: og.Attribute = node.get_attribute("outputs:args")
        expected_type = args_attr.get_resolved_type()
        actual_type = og.Type(og.BaseDataType.DOUBLE, tuple_count=len(args), array_depth=0)
        if expected_type.base_type == og.BaseDataType.UNKNOWN:
            # The attribute type is unresolved so resolve it now
            args_attr.set_resolved_type(actual_type)
            return True
        elif expected_type != actual_type:
            # The attribute type was already resolved, but the type of args does not match
            carb.log_warn(f"Expected OSC arguments of type {expected_type} but got {actual_type}")
            return False
        else:
            # Nothing to do, return true
            return True

    @staticmethod
    @carb.profiler.profile
    def compute(db: og.Database) -> bool:
        state: OgnOnOscEventInternalState = db.internal_state
        osc_path_regex = db.inputs.path

        if state.first_time_subscribe(db.node, osc_path_regex):
            return True

        event = state.try_pop_event()

        if event is None:
            return False

        try:
            addr, args = omni.osc.osc_message_from_carb_event(event)

            node: og.Node = db.node

            if not OgnOnOscEvent.validate_osc_message_args(args):
                carb.log_error(f"OSC message arguments must be of type float, got: {args}")
                return False

            if not OgnOnOscEvent.resolve_osc_message_args_type(node, args):
                return False

            db.outputs.path = addr
            db.outputs.args = args if len(args) > 1 else args[0]
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        except Exception as e:
            carb.log_error(f"Error in OgnOnOscEvent::compute: {e}")
            return False
        return True
