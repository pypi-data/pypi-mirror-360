"""Python client for the Rust backend (naludaq_rs).

This package contains all the basic functionality required to communicate with the Rust backend.
Higher-level functionality (such as the DataCollector) is provided by the rest of the NaluDAQ package.

The Rust backend is an application which runs either locally (in-process or out-of-process) or remotely (over the network).
Its purpose is to provide a flexible and performant interface for controlling hardware and acquiring data.
It provides a REST API through HTTP for communicating with the hardware, which the `backend` subpackage interally uses
for everything. The user should never need to care about the specifics of the REST API.

There really very few things this client cares about:
- Hardware connections and I/O (abstracted as "Devices")
- Data (acquisition) storage and retrieval
- Server configuration

The connection to the server is held by a "Context," which provides a simple HTTP interface. The context
does not usually need to be created manually, as it is created by the `Board` object. However, if it is
desired to communicate with the server without a Board object then one can be created manually.

Control of the server is split into "managers", which are each responsible for managing a specific aspect
of the server. The only managers are:

- AcquisitionManager - data acquisition and retrieval
- BoardIoManager - reading and writing registers
- ConfigManager - server configuration (you probably won't need to use this often)
- ConnectionManager - opening and configuring connections to hardware

Note that the BoardIoManager, ConfigManager, and ConnectionManager will rarely need to be used
externally, as the Board object and various controllers provide a higher-level interface; the
AcquisitionManager is the only one the user should really care about.

Besides controlling the server, there are a few useful types which model the hardware and data:

- RemoteAcquisition - accessing an acquisition remotely
- LocalAcquisition - accessing an acquisition in memory
- DiskAcquisition - accessing an acquisition on disk
- TemporaryAcquisition - a remote acquisition, but only exists for as long as you need it
- Device - a representation of a hardware device, mainly useful for viewing available devices.
"""


from .context import Context
from .managers import (
    AcquisitionManager,
    BoardIoManager,
    ConfigManager,
    ConnectionManager,
)
from .models import (
    AvailableD2xxDevice,
    AvailableSerialDevice,
    D2xxDevice,
    Device,
    DeviceType,
    DiskAcquisition,
    DiskChunk,
    LocalAcquisition,
    RemoteAcquisition,
    SerialDevice,
    TemporaryAcquisition,
    UdpDevice,
)
