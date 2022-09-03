# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import asyncio

import omni.kit.test
import omni.osc


class Test(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    async def test_can_start_and_stop_server(self):
        server = omni.osc.DaemonOSCUDPServer(None)
        is_running = server.start("localhost", 12345)
        self.assertTrue(is_running)
        await asyncio.sleep(0.1)
        is_running = server.running()
        self.assertTrue(is_running)
        is_running = server.stop()
        self.assertFalse(is_running)

    async def test_server_can_receive_messages(self):
        server = omni.osc.OmniOscExt.create_server()
        is_running = server.start("localhost", 3337)
        self.assertTrue(is_running)

        self.count = 0
        def on_event(e) -> None:
            addr, _ = omni.osc.osc_message_from_carb_event(e)
            self.assertEqual(e.type, omni.osc.core.OSC_EVENT_TYPE)
            self.assertEqual(addr, "/filter")
            self.count += 1
        sub = omni.osc.subscribe_to_osc_event_stream(on_event)

        total_msg_count = 10
        def send_messages():
            import random

            from pythonosc import udp_client
            client = udp_client.SimpleUDPClient(address="127.0.0.1", port=3337)
            self.assertTrue(client is not None)
            for _ in range(total_msg_count):
                client.send_message("/filter", random.random())
        send_messages()
        # Wait a few seconds for the server to receive the messages
        await asyncio.sleep(3)
        # Manually pump the stream so our subscription callback executes
        omni.osc.get_osc_event_stream().pump()
        self.assertEqual(self.count, total_msg_count)
