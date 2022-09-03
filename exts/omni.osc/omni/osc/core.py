## Copyright © 2022 NVIDIA CORPORATION & AFFILIATES. ALL RIGHTS RESERVED.
##
## This software product is a proprietary product of Nvidia Corporation and its affiliates
## (the "Company") and all right, title, and interest in and to the software
## product, including all associated intellectual property rights, are and
## shall remain exclusively with the Company.
##
## This software product is governed by the End User License Agreement
## provided with the software product.

from typing import Callable, Tuple

import carb
import carb.events
import omni.ext
import omni.kit.app

OSC_EVENT_TYPE_NAME: str = "omni.osc"
OSC_EVENT_TYPE: int = carb.events.type_from_string(OSC_EVENT_TYPE_NAME)
OSC_MESSAGE_ADDRESS_STR = "address"
OSC_MESSAGE_ARGUMENTS_STR = "arguments"


def get_osc_event_stream() -> carb.events._events.IEventStream:
    """
    Returns the OSC event stream
    """
    return omni.kit.app.get_app().get_message_bus_event_stream()

def push_to_osc_event_stream(payload: dict) -> None:
    """
    Push a payload to the OSC event stream
    """
    get_osc_event_stream().push(OSC_EVENT_TYPE, sender=0, payload=payload)

def subscribe_to_osc_event_stream(
    cb: Callable[[carb.events._events.IEvent], None]
) -> carb.events._events.ISubscription:
    """
    Returns a Carbonite event subscription to the OSC event stream
    """
    return get_osc_event_stream().create_subscription_to_pop_by_type(OSC_EVENT_TYPE, cb)

def carb_event_payload_from_osc_message(address: str, args: list) -> dict:
    """
    Return a carbonite event payload suitable for pushing to the OSC event stream
    """
    return {OSC_MESSAGE_ADDRESS_STR: address, OSC_MESSAGE_ARGUMENTS_STR: args}

def osc_message_from_carb_event(e: carb.events.IEvent) -> Tuple[str, list]:
    """
    Return the OSC message address and arguments extracted from a carbonite event payload
    """
    return (e.payload[OSC_MESSAGE_ADDRESS_STR], e.payload[OSC_MESSAGE_ARGUMENTS_STR])
