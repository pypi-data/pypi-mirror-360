# insta360

This Python package implements 
[RTMP (Real-Time Messaging Protocol)](https://en.wikipedia.org/wiki/Real-Time_Messaging_Protocol)
protocols for interacting with Insta360 cameras.

RTMP is a proprietary protocol used by Insta360 cameras for many of its core functionalities.
This package aims to provide a unified interface for interacting with Insta360
cameras by reverse engineering the proprietary RTMP protocol.

The RTMP protocol is implemented by reverse engineering the communication between
Insta360 cameras and the official Android app.

Documentation is available at [https://insta360.whitebox.aero](https://insta360.whitebox.aero).

# Compatibility

While the package is developed and tested with Insta360 X3 and X4, it should work
with other Insta360 cameras as well. If you find any compatibility issues, please
open an issue. PRs are also welcome to improve the compatibility with other
Insta360 cameras.

Here is a list all the functions that are implemented and tested and their
compatibility with different Insta360 cameras:

**Stream Resolutions:**

- X3: 1440 × 720 at 30fps (Any higher or lower resolution yields glitchy stream)
- X4: 2880 × 1440 at 30fps (Hardcoded at hardware level)

**Legend:**

- ✅: Implemented and tested
- ❌: Not implemented
- 🟡: Implemented but broken
- 🚫: Not supported by device

**RTMP Module:**

| Functionality              | Implemented | X3 | X4 |
|:---------------------------|:-----------:|:--:|:--:|
| sync_local_time_to_camera  |      ✅      | ✅  | ✅  |
| get_camera_info            |      ✅      | ✅  | ✅  |
| take_picture               |      ✅      | ✅  | ✅  |
| get_camera_files_list      |      ✅      | ✅  | ✅  |
| set_normal_video_options   |      ✅      | ✅  | ✅  |
| get_normal_video_options   |      ✅      | ✅  | ✅  |
| start_capture              |      ✅      | ✅  | ✅  |
| stop_capture               |      ✅      | ✅  | ✅  |
| get_capture_current_status |      ✅      | ✅  | ✅  |
| start_preview_stream       |      ✅      | ✅  | ✅  |
| stop_preview_stream        |      ✅      | ✅  | ✅  |
| start_live_stream          |      ❌      | ❌  | ❌  |
| stop_live_stream           |      ❌      | ❌  | ❌  |
| get_camera_type            |      ❌      | ❌  | ❌  |
| get_serial_number          |      ❌      | ❌  | ❌  |
| get_exposure_settings      |      ❌      | ❌  | ❌  |
| set_exposure_settings      |      ❌      | ❌  | ❌  |
| set_capture_settings       |      ❌      | ❌  | ❌  |
| get_capture_settings       |      ❌      | ❌  | ❌  |
| get_camera_uuid            |      ❌      | ❌  | ❌  |
| set_time_lapse_options     |      ❌      | ❌  | ❌  |
| start_time_lapse           |      ❌      | ❌  | ❌  |
| stop_time_lapse            |      ❌      | ❌  | ❌  |
| is_camera_connected        |      ❌      | ❌  | ❌  |
| get_battery_status         |      ❌      | ❌  | ❌  |
| get_storage_state          |      ❌      | ❌  | ❌  |

# Installation

To install the package, run the following command:

```bash
pip install insta360
```

## Developer environment setup

If you'd like to contribute to the project or do additional development, take a
look at the [Developer Guide](https://insta360.whitebox.aero/developer-guide/getting-started/).

# Usage

First make sure you are [connected](#connecting-to-the-wifi) to the camera's Wi-Fi network.

The package provides `rtmp` module, for interacting with Insta360
cameras using RTMP protocol. RTMP is a proprietary protocol used by Insta360
cameras for many of its core functionalities. Depending on your use case, you can choose to use the `rtmp` module.

Below are some examples of how to use the `rtmp` module. For more
detailed information, refer to the API reference pages in the documentation on
[`rtmp` module](https://insta360.whitebox.aero/api-reference/rtmp-module/).

## Examples

## `rtmp` module

Here is an example of how to use the `rtmp` module:

```python
import time
from insta360.rtmp import Client

# Create an RTMP client
client = Client()

# Start capturing video
client.start_capture()
time.sleep(10)

# Stop capturing video
client.stop_capture()
time.sleep(5)

# Close the client
client.close()
```

### Camera events

The `rtmp` module also supports registering event handlers. For example, you can
register a handler to get data every time a camera streams video data:

```python
from insta360.rtmp import Client

# Create an RTMP client
client = Client()

@client.on_connect()
async def event_handler(**kwargs):
    print("Connected to the camera")

# Connect to camera, and the event will print the message when connected
client.open()
```

Depending on what you'd like to accomplish, you might want to ensure that the
event handlers are executed in strict order of events happening (e.g. you likely
want to ensure that the video data is always processed in proper order, even if
there is a burst due to connectivity troubles). You can do this by setting
`wait=True` when registering the event handler:

```python
from insta360.rtmp import Client

# Create an RTMP client
client = Client()

@client.on_video_stream(wait=True)
async def event_handler(content, **kwargs):
    print("Received {} bytes of video content".format(len(content)))

client.open()
# Start preview stream, which will stream the data to the event handler
client.start_preview_stream()
```

For more info on the available events and usage guidance, refer
to the [events' documentation](https://insta360.whitebox.aero/api-reference/event-system/).

For guidance on how to use the `wait` option, refer to the
[event processing order](https://insta360.whitebox.aero/api-reference/event-system/#event-processing-order)
section.

# Connecting to the Wi-Fi

<a id="connecting-to-the-wifi"></a>
Start your camera and soon after you will see a Wi-Fi network with the name
`YOUR_CAMERA_MODEL_NAME.OSC`. Connect to this network using the password `88888888`.
If you are using Insta360 X4, the password is randomly generated during the
device setup. In this case, you can find the password on your camera by navigating
to `Settings > Wi-Fi Settings > Password`.

Although the security issue of having a fixed password is no longer present in
recent models like the Insta360 X4 and you can change the Wi-Fi password on cameras
like this Insta360 X3, this is a **huge security hole** for older models.

Any host in the nearby can connect to these older models as soon they are turned
on; once established the connection they can also do a **telnet** into the
Insta360's GNU/Linux operating system as **root** (the IP address of the camera
is **192.168.42.1**) and do whatever they want, even to damage permanently
(brick) the camera.

## The Protobuf problem

The messages exchanged from the Android app and the camera
use the **Protocol Buffers**, which is an open standard by Google.

Unfortunately the protobuf messages are not self-describing;
that is, there is no way to tell the names, meaning, or full
datatypes of exchanged messages without an external
specification. To write an understandable source code you need
to extract the specific language description files from a
compiled binary file, e.g. a library from the Android app. To
run the insta360.py module you need such files compiled for
Python. Follow the link at the bottom of this page to get more
instructions.

## The `insta` program

The **insta** is a somewhat working example using the insta360.py module.
It has the basic functionality required for a remote control: start and stop
recording, get preview stream. You can run it from an Android smartphone if you
install the [Termux](https://termux.dev/en/) app and the required Python
libraries.

We are working to make installing this program easier, but for now you can clone
the repository and run the following command to create a virtual environment and
install the required packages:

```bash
pip install poetry
poetry config virtualenvs.in-project true
poetry env use 3.10
poetry install
```

Then, run the following command to create a shell with the virtual environment:

```bash
poetry shell
```

Then, run the following command to run the program:

```bash
# Preview and capture simultaneously
./insta -o ./output/dump.mp4 -c preview -c capture

# Start recording
./insta -c capture

# Know all the options
./insta -h
```

Alternatively, if you'd like to avoid creating a shell, you can use:

```bash
poetry run ./insta -h
```

![insta command screenshot screenshot](https://gitlab.com/whitebox-aero/insta360/-/raw/main/assets/insta_cmd.jpg "insta command screenshot")

## Docs

Documentation is auto-generated with [MkDocs](https://www.mkdocs.org/).
While contributing, make sure to follow
[Google docstring conventions](https://mkdocstrings.github.io/griffe/docstrings/#google-style)
when documenting the code.

To generate the docs, set up the [development environment](https://insta360.whitebox.aero/developer-guide/getting-started/)
with `poetry` and use it to download the required packages:

```bash
pip install poetry
poetry config virtualenvs.in-project true
poetry env use 3.10
poetry install
```

Then, run the following command to run the server:

```bash
mkdocs serve
```
