# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import threading

import carb
import carb.events
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher


class DaemonOSCUDPServer:
    """
    Run a python-osc BlockingOSCUDPServer in a separate thread.

    Usage::

        import omni.osc.core as osc

        dispatcher = osc.Dispatcher()
        dispatcher.set_default_handler(lambda(path, args): print(f"{path}: {args}"))
        server = osc.DaemonOSCUDPServer(dispatcher)
        server.start("192.168.0.1", 3434)
        # ...
        server.stop()
    """

    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher: Dispatcher = dispatcher
        self.server: osc_server.BlockingOSCUDPServer = None
        self.thread: threading.Thread = None

    def running(self) -> bool:
        """
        Returns true if the server is running
        """
        return self.thread is not None and self.thread.is_alive()

    def start(self, addr: str, port: int) -> bool:
        """
        Start the OSC server on the specified address and port.
        Does nothing if the server is already running.
        """
        if not self.running():
            carb.log_info(f"Starting OSC server on {addr}:{port}")
            try:
                self.server = osc_server.BlockingOSCUDPServer((addr, port), dispatcher=self.dispatcher)
                self.thread = threading.Thread(target=lambda: self.server.serve_forever())
                # NOTE(jshrake): Running the thread in daemon mode ensures that the thread and server
                # are properly disposed of in the event that the main thread exits unexpectedly.
                self.thread.daemon = True
                self.thread.start()
            except Exception as e:
                carb.log_error(f"Error starting OSC server: {e}")
        else:
            carb.log_info("OSC server already running")
        return self.running()

    def stop(self) -> bool:
        """
        Stops the OSC server.
        """
        if self.running():
            carb.log_info("Stopping OSC server")
            try:
                self.server.shutdown()
                self.thread.join()
            except Exception as e:
                carb.log_error(f"Error stopping OSC server: {e}")
            finally:
                self.server = None
                self.thread = None
        else:
            carb.log_info("OSC server not running")
        return self.running()
