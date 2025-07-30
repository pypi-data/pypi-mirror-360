# wiim
A Python-based API interface for controlling and communicating with WiiM audio devices

## ✨ Introduction

**wiim** is a powerful and user-friendly Python library designed to significantly simplify the integration and control of [WiiM](https://wiimhome.com/) smart audio devices. WiiM devices (built on LinkPlay modules) deliver an immersive musical experience throughout your home with their excellent wireless streaming and multiroom audio capabilities. With **wiim**, you can seamlessly manage your WiiM devices directly from your Python applications.

Whether you need precise control over music playback, synchronization of multiroom groups, or real-time retrieval of playback metadata, **wiim** provides a clean and unified interface. It's the ideal choice for building smart home automations, custom music players, or any Python application requiring interaction with WiiM devices.

## 🚀 Key Features

✅ **Automatic Device Discovery**  
Smartly scans and identifies all WiiM devices on your network, making connection effortless.

✅ **Comprehensive Playback Control**  
Offers all core functionalities including play, pause, stop, skip tracks, volume adjustment, mute/unmute, shuffle, repeat modes, and input source switching.

✅ **Rich Metadata Retrieval**  
Get real-time detailed information about the currently playing track, such as title, artist, album, album art URL, and more, helping you create personalized display interfaces.

✅ **Flexible Group Management**  
Easily create, update, or disband multiroom synchronized playback groups for seamless music across your entire home.

✅ **High Availability & Stability**  
Built-in error handling and device status monitoring mechanisms ensure your control commands are reliably delivered.

## 💡 Quick Start

### Installation

Install the **wiim** library easily via pip:

```bash
pip install wiim
```

### Usage Example

Here's a quick example demonstrating how to connect to and control a WiiM device to play music:

```python
import asyncio
import logging
from typing import Dict

from aiohttp import ClientSession, TCPConnector
from zeroconf import ServiceInfo
from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf, Zeroconf

from .consts import SDK_LOGGER
from .controller import WiimController
from .discovery import verify_wiim_device
from .endpoint import WiimApiEndpoint
from .wiim_device import WiimDevice


class ZeroconfListener:
    """
    A listener class for discovering and collecting Zeroconf services on the network.
    """

    def __init__(self):
        self.discovered_devices: Dict[str, ServiceInfo] = {}

    def remove_service(self, zeroconf: "Zeroconf", type: str, name: str) -> None:
        """Called when a service is removed."""
        SDK_LOGGER.info(f"Zeroconf service removed: {name}, type: {type}")
        self.discovered_devices.pop(name, None)

    def add_service(self, zeroconf: "Zeroconf", type: str, name: str) -> None:
        """Called when a service is added or updated."""
        SDK_LOGGER.info(f"Zeroconf service added/updated: {name}, type: {type}")
        asyncio.create_task(self._async_add_service(zeroconf, type, name))

    async def _async_add_service(
        self, zeroconf: "Zeroconf", type: str, name: str
    ) -> None:
        """Asynchronously retrieves and stores service information."""
        info = await zeroconf.async_get_service_info(type, name)
        if info:
            self.discovered_devices[name] = info


async def _create_cli_session() -> ClientSession:
    """Creates an aiohttp client session for the CLI."""
    return ClientSession(connector=TCPConnector(ssl=False))


async def main_cli():
    """
    Command-line interface for discovering and interacting with WiiM devices using Zeroconf.
    """
    # Set up logging
    SDK_LOGGER.setLevel(logging.INFO)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    SDK_LOGGER.info("Starting WiiM SDK CLI discovery using Zeroconf...")

    # 1. Discover using Zeroconf
    aiozc = AsyncZeroconf()
    listener = ZeroconfListener()
    # Browse for service types common to WiiM devices
    browser = AsyncServiceBrowser(aiozc.zeroconf, "_linkplay._tcp.local.", listener)

    # Wait a few seconds for devices to be discovered
    discover_duration = 5
    SDK_LOGGER.info(
        f"Waiting {discover_duration} seconds for devices to be discovered..."
    )
    await asyncio.sleep(discover_duration)

    # Stop Browse
    await browser.async_cancel()
    await aiozc.async_close()

    if not listener.discovered_devices:
        SDK_LOGGER.info("No WiiM devices found via Zeroconf on the network.")
        return

    # 2. Verify and initialize discovered devices
    async with await _create_cli_session() as session:
        controller = WiimController(session)

        for name, info in listener.discovered_devices.items():
            if not info or not info.parsed_addresses():
                continue

            wiim_device_ip = info.parsed_addresses()[0]
            SDK_LOGGER.info(
                f"Found potential device '{name}' at {wiim_device_ip}. Verifying..."
            )

            potential_locations = [
                f"http://{wiim_device_ip}:{info.port}/description.xml",  # Try the service's own port
                f"http://{wiim_device_ip}/description.xml",  # Try the standard HTTP port
                f"http://{wiim_device_ip}:49152/description.xml",  # Try a common UPnP port
            ]

            upnp_device = None
            for location in potential_locations:
                # Use the verify_wiim_device function from discovery.py to check if this is a WiiM device
                upnp_device = await verify_wiim_device(location, session)
                if upnp_device:
                    SDK_LOGGER.info(f"Successfully verified WiiM device at {location}")
                    break

            if not upnp_device:
                SDK_LOGGER.warning(
                    f"Could not verify device '{name}' at {wiim_device_ip}. It might not be a WiiM device or is not responding."
                )
                continue

            # Create an HTTP API endpoint, using the WiiM device's IP
            http_api = WiimApiEndpoint(
                protocol="https", port=443, endpoint=wiim_device_ip, session=session
            )  #

            # Create and initialize the WiimDevice instance.
            # Set ha_host_ip to the local IP address we just obtained.
            wiim_dev = WiimDevice(
                upnp_device,
                session,
                http_api_endpoint=http_api,
                ha_host_ip=wiim_device_ip,
                polling_interval=60,
            )
            await controller.add_device(wiim_dev)

        if not controller.devices:
            SDK_LOGGER.info("No verifiable WiiM devices could be initialized.")
            return

        # 3. Print device information (same logic as original __main__.py)
        SDK_LOGGER.info(f"Found and verified {len(controller.devices)} WiiM device(s):")
        for device_idx, device in enumerate(controller.devices):
            print(f"\n--- Device {device_idx + 1} ---")
            if not device.available:
                print(
                    f"Name: {device.name} (UDN: {device.udn}) - Currently Unavailable"
                )
                continue

            print(f"  Name: {device.name}")  #
            print(f"  UDN: {device.udn}")  #
            print(f"  Model: {device.model_name}")  #
            print(f"  IP Address: {device.ip_address}")  #
            print(f"  Firmware: {device.firmware_version or 'N/A'}")  #
            print(
                f"  UPnP Device URL: {device.upnp_device.device_url if device.upnp_device else 'N/A'}"
            )

            print(
                f"  Status: {device.playing_status.value if device.playing_status else 'N/A'}"
            )
            print(
                f"  Volume: {device.volume}% {'(Muted)' if device.is_muted else ''}"
            )

            if device.current_track_info:
                track_info = device.current_track_info
                print("  Current Track:")  #
                print(f"    Title: {track_info.get('title', 'N/A')}")  #
                print(f"    Artist: {track_info.get('artist', 'N/A')}")  #
                print(f"    Album: {track_info.get('album', 'N/A')}")  #

        # Clean up resources
        print("\nDisconnecting from devices...")
        for device in controller.devices:
            await device.disconnect()

if __name__ == "__main__":
    asyncio.run(main_cli())
```

**Important Notes for the Example:**
- Starts Zeroconf discovery using AsyncZeroconf with ZeroconfListener to automatically find _linkplay._tcp.local. services broadcasted by WiiM devices on your network.
- Waits a configurable duration (e.g., 5 seconds) using asyncio.sleep() to give Zeroconf time to discover devices on the network.
- Verifies each discovered device by probing common UPnP description URLs like http://<device_ip>/description.xml with verify_wiim_device() to confirm it's a WiiM device.
- Creates a WiimDevice instance for each verified WiiM device and sets up an HTTP API endpoint using WiimApiEndpoint for controlling the device.
- Prints detailed information about each verified device including name, UDN, model, IP address, firmware version, playback status, volume, and current track metadata.
- Cleans up all resources by disconnecting from devices, canceling Zeroconf browsing, and closing aiohttp client sessions after the process completes.


## 📄 License

This project is licensed under the MIT License.

## 📞 Support & Feedback

If you encounter any issues during use, or have any suggestions and ideas, please feel free to submit them via GitHub Issues.
