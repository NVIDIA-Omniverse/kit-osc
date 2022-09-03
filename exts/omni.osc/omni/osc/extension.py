# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.


from typing import Any, List

import carb
import carb.events
import carb.profiler
import omni.ext
import omni.kit.app
from pythonosc.dispatcher import Dispatcher

from .core import carb_event_payload_from_osc_message, push_to_osc_event_stream
from .menu import OscMenu
from .server import DaemonOSCUDPServer
from .window import OscWindow


class OmniOscExt(omni.ext.IExt):
    def on_startup(self, ext_id):
        def on_start(host: str, port: int) -> bool:
            return self.server.start(host, port)

        def on_stop() -> bool:
            return self.server.stop()

        def toggle_window_visible(_arg0, _arg1) -> None:
            """
            Toggle the window visibility from the editor menu item
            """
            self.window.visible = not self.window.visible

        self.server = OmniOscExt.create_server()
        # The main UI window
        default_addr = carb.settings.get_settings().get("exts/omni.osc/address")
        default_port = carb.settings.get_settings().get("exts/omni.osc/port")
        self.window = OscWindow(
            on_start=on_start, on_stop=on_stop, default_addr=default_addr, default_port=default_port
        )
        # The editor menu entry that toggles the window visibility
        self.menu = OscMenu(on_click=toggle_window_visible)
        # Toggle the editor menu entry when the user closes the window
        self.window.set_visibility_changed_fn(lambda visible: self.menu.set_item_value(visible))

    def on_shutdown(self):
        self.window = None
        self.menu = None
        if self.server is not None:
            self.server.stop()
            self.server = None

    def create_server() -> DaemonOSCUDPServer:
        """
        Create a server that routes all OSC messages to a carbonite event stream
        """

        @carb.profiler.profile
        def on_osc_msg(addr: str, *args: List[Any]) -> None:
            """
            OSC message handler
            """
            carb.log_verbose(f"OSC message: [{addr}, {args}]")
            payload = carb_event_payload_from_osc_message(addr, args)
            push_to_osc_event_stream(payload)

        # Server
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(on_osc_msg)
        return DaemonOSCUDPServer(dispatcher)
