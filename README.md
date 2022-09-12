# Open Sound Control Omniverse Kit Extension [omni.osc]

![demo.gif](/docs/images/demo.gif)

Omniverse Kit extension for sending and receiving OSC (Open Sound Control) messages.

# Getting Started

Open the Community tab under Extensions window (`Window > Extensions`), search for `OSC`, and install and enable the `omni.osc` extension.

![extension-install](/docs/images/extension-install.png)

You can find an example USD stages that demonstrate how to use the On Osc Message OmniGraph node at [exts/omni.osc/data/examples](/exts/omni.osc/data/examples).

## Running the server

After installing and enabling the extension, you should see the following window.

![server-ui-window](/docs/images/server-ui-window.png)

Enter the private IP address of the computer running your Kit application and the desired port, then click `Start`. If you are prompted to configure your Windows Firewall, ensure that the Kit application is allowed to communicate with other devices on the private network.

![windows-firewall](/docs/images/osc-start-windows-security-alert.png)

You can find the private IP address of your computer by running `ipconfig` in the Windows terminal.

![ipconfig](/docs/images/ipconfig.png)

If you run the server on `localhost`, that means the server can only receive messages from OSC clients running on the same machine. If you want to receive messages from OSC clients running on other devices on the same network, you must run the server on an IP address that is visible to those devices.

Once the server is running, confirm that it can successfully receive messages by inspecting the verbose console logs. It might be helpful to filter only the logs that originate from `omni.osc`.

![console-logs](/docs/images/console-logs.png)

## Receiving messages with Python

Below is a python snippet that demonstrates how to handle OSC messages received by the server. It assumes that the OSC server configured above is running. You can paste and run the below snippet directly into the Omniverse Script Editor for testing.

```python
import carb
import carb.events
import omni.osc

def on_event(event: carb.events.IEvent) -> None:
    addr, args = omni.osc.osc_message_from_carb_event(event)
    carb.log_info(f"Received OSC message: [{addr}, {args}]")

sub = omni.osc.subscribe_to_osc_event_stream(on_event)
```

## Receiving messages with ActionGraph

Search for `OSC` in the Action Graph nodes list and add the `On OSC Message` node to your graph. The node takes a single input,
the OSC address path that this node will handle. This input can be a valid regular expression. Note that this input field does *not* support
OSC pattern matching expressions. The node outputs an OmniGraph bundle with two attributes named `address` and `arguments` which you
can access by using the `Extract Attribute` node.

![og-receive](/docs/images/og-receive.png)

You can find example USD stages that demonstrate how to configure an ActionGraph using this extension at [exts/omni.osc/data/examples](/exts/omni.osc/data/examples).

## Sending messages from Python

Since `omni.osc` depends on [python-osc](https://pypi.org/project/python-osc/), you can import this module directly in
your own Python code to send OSC messages. Please see the [documentation](https://python-osc.readthedocs.io/en/latest/) for additional
information and support.

```python
import random
import time

from pythonosc import udp_client

client = udp_client.SimpleUDPClient("127.0.0.1",  3334)

client.send_message("/scale", [random.random(), random.random(), random.random()])
```

You can paste and run the above snippet directly into the Omniverse Script Editor for testing.

## Sending messages from ActionGraph

This is not currently implemented.

## Limitations & Known Issues

- OSC Bundles are currently not supported.
- The OmniGraph `On OSC Message` node can only handle OSC messages containing lists of floating-point arguments.

# Help

The below sections should help you diagnose any potential issues you may encounter while working with `omni.osc` extension.

## Unable to receive messages

1. First, enable verbose logs in the console (filter by the `omni.osc` extension). The server will log any messages received.
2. Confirm that the computer running the Kit application and the device sending the OSC messages are on the same network.
3. Confirm that kit.exe is allowed to communicate with the private network through the Windows Defender Firewall. Note that
you may have multiple instances of kit.exe on this list. When in doubt, ensure that all of them have the appropriate permission.
![windows-firewall](/docs/images/windows-firewall.png)
4. Confirm that the Windows Defender Firewall allows incoming UDP traffic to the port in use.
5. Confirm that the device sending the OSC messages is sending the messages via UDP to the correct IP address and port.
6. Use a tool such as [wireshark](https://www.wireshark.org/) to confirm that the computer running the Kit application is receiving UDP traffic from the device.

## Unable to send messages

1. Confirm that the computer running the Kit application and the device receiving the OSC messages are on the same network.
2. Confirm that kit.exe is allowed to communicate with the private network through the Windows Defender Firewall.
3. Confirm that the device receiving the OSC messages is able to receive incoming UDP traffic at the port in use.

# Contributing

The source code for this repository is provided as-is and we are not accepting outside contributions.

# License

- The code in this repository is licensed under the Apache License 2.0. See [LICENSE](/LICENSE).
- python-osc is licensed under the Unlicense. See [exts/omni.osc/vendor/LICENSE-python-osc](/exts/omni.osc/vendor/LICENSE-python-osc).

# Resources

- [https://opensoundcontrol.stanford.edu/spec-1_0.html](https://opensoundcontrol.stanford.edu/spec-1_0.html)
- [https://en.wikipedia.org/wiki/Open_Sound_Control](https://en.wikipedia.org/wiki/Open_Sound_Control)
- [https://python-osc.readthedocs.io/en/latest/](https://python-osc.readthedocs.io/en/latest/)
