# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from typing import Callable

import omni.ui as ui

OnStartCallback = Callable[[str, int], bool]
OnStopCallback = Callable[[], bool]


class OscWindow(ui.Window):
    def __init__(
        self, default_addr: str, default_port: int, on_start: OnStartCallback, on_stop: OnStopCallback
    ) -> None:
        super().__init__("OSC UDP Server", width=300, height=300)

        def start() -> None:
            """
            Callback when the user presses the start button
            """
            is_running = on_start(addr.as_string, port.as_int)
            running.set_value(is_running)

        def stop() -> None:
            """
            Callback when the user presses the stop button
            """
            is_running = on_stop()
            running.set_value(is_running)

        def update_running_label(label: ui.Label, running: bool) -> None:
            """
            Keep the UI label up to date with the state of the server
            """
            if running:
                label.text = f"Running UDP server @ {addr.as_string}:{port.as_int}"
                label.set_style({"color": "green"})
            else:
                label.text = "Stopped"
                label.set_style({"color": "red"})

        def toggle_enabled(field: ui.AbstractField, running: bool) -> None:
            """
            Enable or disable the input field based on the state of the server
            """
            field.enabled = not running
            color = "gray" if running else "white"
            field.set_style({"color": color})

        # Settings

        addr = ui.SimpleStringModel(default_addr)
        port = ui.SimpleIntModel(default_port)
        running = ui.SimpleBoolModel(False)

        with self.frame:
            with ui.VStack():
                label = ui.Label("", height=20)
                update_running_label(label, running.get_value_as_bool())
                running.add_value_changed_fn(lambda m: update_running_label(label, m.get_value_as_bool()))
                with ui.VStack(height=20):
                    with ui.HStack():
                        ui.Label("Address:")
                        addr_field = ui.StringField(addr)
                        toggle_enabled(addr_field, running.get_value_as_bool())
                        running.add_value_changed_fn(lambda m: toggle_enabled(addr_field, m.get_value_as_bool()))
                    ui.Spacer(height=2)
                    with ui.HStack():
                        ui.Label("Port:")
                        port_field = ui.IntField(port)
                        toggle_enabled(port_field, running.get_value_as_bool())
                        running.add_value_changed_fn(lambda m: toggle_enabled(port_field, m.get_value_as_bool()))
                with ui.VStack():
                    ui.Button("Start", clicked_fn=start)
                    ui.Button("Stop", clicked_fn=stop)
