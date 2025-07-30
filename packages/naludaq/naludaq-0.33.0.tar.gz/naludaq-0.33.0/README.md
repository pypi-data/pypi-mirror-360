# Introduction

Naludaq (Nalu Data Acquisition) is a backend software package to communicate with Nalu Scientifics hardware. It contains several modules to communicate with the boards, both sending commands, receiving responses and receiving bulk data. It also contains modules to parse and store data.
This module is designed to interact with a user interface or used to create automated experiments.

The package is designed around the board object, a software representation of the hardware board. It contains a map of the registers found on the hardware system with a mirror of all values sent and received from the board, a connection object handling the connections, and all parameters describing the board. See the `board` section.

In the package are different modules, they are designed in layers. Connections and daq are the lowest level, the communications module is one step abstracted with english names for the hardware registers and command builders to send register updates and commands to the board.
Above that are controllers, controlling different aspects of the board. The software the user develops should build on top of the controllers primarily and rare cases should a user have to use the communication module.

A Quick rundown:
The controllers are the modules the users should use to build their interfaces.
The controllers manipulate the registers on the FPGA using the communication layer. This is a set of tools to update the different registers on the FPGA.
The communication layers communication with the hardware using the connection.
There is a mirroring between the hardware board and the software board. The software board carries a mirror of all the params and the connection.
A factory supplies the connection to the SW board since the connection can be ethernet, uart or usb.


# Getting Started

This backend is intended to be integrated with either NaluCommand (command line tools), NaluScope (Graphical user interface) or jupyter notebooks.
To run the Naludaq standalone you will have to install the package.

```
pip install naludaq
```

To install the latest version of the master branch.
It is then possible to import the package in your notebook or python script.

```py
import naludaq
```


## Prerequisites

To start using the Naludaq as a standalone it's highly recommended to have a virtual envirnoment setup.
As a user or developer you will need to run python version 3.9 or later.
See the instructions below in the Development installation section.
A hardware board is also recommended, it's possible to use the software without hardware using the demo board. It's a software replica with limited functionality.


# Development installation

This is the prefered method to get a developement environment up and running.
1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
2. Create and activate a virtual envirnoment, minimum Python version is 3.9.

```
conda create -n nalu-dev python=3.9
conda activate nalu-dev
```

Then pull the repository into a suitable folder:

```
git clone http://github.com/NaluScientific/naludaq.git
cd naludaq
```

To get the development environment up and running you have to install the package as an editable package:

```
pip install -e .[dev]
```

The package can now be imported in your project and edited in your favorite editor, [VS Code](https://code.visualstudio.com/)

## Development with gigabit ethernet backend

To use the gigabit ethernet backend you will need to install the `naludaq_rs` package.

1. Clone the package from GitHub
2. install the package as an editable package. See instructions in the `naludaq_rs` package.


## Pre-commit

This project uses pre-commit hooks to make sure the code is following the style guide.
To install the pre-commit hooks, run the following command:

```
pip install pre-commit
pre-commit install
```

The hooks will run automatically when you commit changes to the repository.

The code MUST run the pre-commit hooks before commiting. If the hooks fail, the commit will be rejected.

# Examples

See the [example repository](https://github.com/NaluScientific/naluexamples).

# Development Use

Once the package is installed it's now possible to start using the package.
There is a boilerplate interface named `Naludaq` in `naludaq` it contains basic functionality.
It's a good starting point to get the software started.
If more advanced scripts are required please continue reading below.
A datasheet for the board is also required to understand the registers and the commands.

# Generate Documentation

The documentation is auto-generated using sphinx. These are the steps to generate the documentation based on the current base.
If major changes are made in the code base the documentation need to re-generated, se `Setup generating documentation` below.

To generate the html verison of the documentation navigate to the project folder.

```
cd docs
pip install sphinx
pip install sphinx_rtd_theme
make html
```

Generating pdf requires more prerequisites. On Windows install [MikTex](https://miktex.org/) and [Perl](http://strawberryperl.com/).
From the MikTex console install the ``latexmk`` addon.

```
cd docs
pip install sphinx
pip install sphinx_rtd_theme
make latexpdf
```

The documentation is generated to the build folder under docs.
More settings for the documentation are found in `docs/source/conf.py`.

# Command Line Use

The `naludaq` comes with an easy interface conveniently called `naludaq`.
It contains high level functionality to operate the board without having to dig deeper into the framework.

Startup:

```py
import os
from naludaq.board import Board

board_model = "asocv3"
board = Board(board_model)
working_dir = os.path.curdir
nd = naludaq.NaluDaq(board, working_dir)
```

The naludaq object can then be used to setup the board and readout data.

# Package structure

```
.
├── src/naludaq
|   ├── backend
|   ├── board
|   ├── communication
|   ├── controllers
|   ├── daq
|   ├── helpers
|   ├── io
|   ├── models
|   ├── parsers
|   └── tools
├── tests
|   └── ...
├── CHANGELOG.md
├── LICENSE.txt
├── pyproject.toml
└── README.md
```


## Board

The board module is a state holder for the application and is a software replica of the settings on the hardware board. It holds the connection to the hardware and stores all the settings sent to the hardware. This is a work around since not all registers can be read out.
The board is created by a factory taking a connection information dictionary and the board model.

The board holds 3 main parts.
- parameters describing the hardwares properties, these paramters are used to describe the protocol to parse the captured data and they also determines sampling rate, connections available.
- a connection object (optional),
- a register map (optional) describing the layout, name and addresses of the different hardware registers.

Nalu uses a default register file repository called NaluConfigs which contains the default registers. For everyday use the defaults are the perfect choice and are loaded by leaving out a filepath to the register- and clockfile when loading them.

Example:

```py

from naludaq.board import Board, startup_board
# Create a board object for an ASoCv2 board
board = Board(
    'asocv2',
    registers= "asocv2.yml" # Can be ommitted if default registers are used
    clock= "asocv2_clock.txt" # Can be ommited if default clockprogram is used, accepts pathlib paths.
)

# Create a connection to the board.
board.get_uart_connection(comport="COM5", baud=115200)

# Or if the FTDI driver is present:
board.get_ftdi_connection(serial_number="XYZ123", baud=115200)

# Run the startup sequence to program the board.
startup_board(board)
```

## Communication

The communication module is currently split up in 5 parts depending on what part of the hardware they control. The analog and digital registers control different aspects of the ASICs and the control registers communicate with the FPGA. The i2c talk to the onboard auxillary electronics. While serial is a helper to the analog and digital register, it contains functions to communicate with the ASICs using the serial interface rather than the default parallel. Certain versions of the boards don't have a parallel connection between the FPGA and the ASIC and the serial interface must be used.

The communication module is not intended to be used standalone but is used by the controllers.
The Analog, Digital, and Control registers, have a common API.

Usage:

```py
with board as brd:  # Opens a connection to the board
    # Write all registers
    DigitalRegister(board).write_all()

    # Write a specific register
    DigitalRegister(board).write(name, value)

    # Read all registers
    DigitalRegister(board).read_all()

    # Read a specific registers
    DigitalRegister(board).read(name)
```

For Control and Digital registers it's possible to read data out from hardware.

```py
# Returns a dictionary {reg_name: reg_map}
# where reg_map is {"value": value, "address": addr, "bitposition": bitposition, "bitwidth": bitwidth, "readwrite": read/write, "description": desc}
values_dict = DigitalRegister(board).read_all()

# Returns the register map {"value": value, "address": addr, "bitposition": bitposition, "bitwidth": bitwidth, "readwrite": read/write, "description": desc}
value = DigitalRegister(board).read(name)
```

## Controllers

The controllers control one aspects of the board functionality. This means there is one controller for each hardware function on the board.
Important to remember that higher level scripts use controllers to orchestrate behaviors such as reading out data, capturing pedestals, scanning trigger levels. This higher level functionalities can be found under tools.
The controllers contains functions to control lower level functionality of the boards, the controllers are recepies to send specific commands to the boards in a certain order to set the mode or state of the board.
There are multiple aspects of the board operations and each onboard component or functional aspect has it's own controller. This way it's possible to create custom scripts or extend functionality easily by using this code.

The following controllers are available:
- `board`
- `connection`
- `external_bias`
- `pedestals`
- `peripherals`
- `project`
- `readout`
- `clock`
- `trigger`

Example:

```py
from naludaq.controllers.board import get_board_controller
brd_ctrl = get_board_controller(board)
brd_ctrl.start_readout(**readout_params)
```

### Accessing controller from the board object

Some controllers are tightly coupled to the board and are already an attribute of the board.
An example is the trigger controller, to use the trigger controllers functionality a user can simply do:

```py
values = {0: 2000, 1: 1800, 2: 1900}
board.trigger.values = values
```

Current quick-access controllers are:

- trigger
- readout
- control
- ext_bias
- peripherals
- clock


## DAQ

The Data AcQuisition (DAQ) module captures the data stream from the board and processes it.
Workers are submodules running as either threads or processes processing aspects of the data stream.
The parsers converts the binary data stream to python readable data.

There are different types of DAQ objects depending on use.

```py
from naludaq.daq import get_daq

location = '/home/username/subfolder' # Linux storage path, replace with yours
daq = get_daq(board, parsed =False, debug=False, location, start_workers=True)
```

To parse the return data, you'll need a parser for the board specific protocol.

```py
from naludaq.parsers import get_parser
params = {
    "model": # Must have, the model of the board used, determines protocol
    "samples": # amount of samples per windows,
    "windows": # max amount of windows the board can readout,
    "channels": # max amount of channels
    "data_bitmask": # how many bits of data we have in a 16-bit package.
    "num_lastbits" # how many bits in the bottom to remove
    "num_footer": # how long is the footer at the end of package (xFACE is 2)
    "num_evt_headers": # How many 16-bit packages are event headers in the begining
    "num_channel_headers" # How meany headers for each channel
    "num_window_headers": # Header at the end of a window (1-4 channels), currently only AARDVARCv3.
}
parser = get_parser(params)
```

Or use the board.params as the input for `get_parser`

The DAQ module contains the Preprocessing submodule which is used to process the raw data from the DAQ into human readble data.
The preprococessing module wil parse, pedestals correct, timing correct, and ADC2mV convert the data depending on configuration.

```py

from naludaq.daq.preprocess import Preprocessing

Preprocess(board).run(
    to_process: dict,  # (Event)
    correct_pedestals: bool,
    convert_mv: bool,
    correct_time: bool,
    convert_time: bool,
    process_in_place: bool,
)

```


## Helpers

Contains helper functions.

### Exceptions

There a multiple exceptions unique to the naludaq package. They are found under helpers.exceptions.
When developing use these exceptions if they fit. Feel free to create your own if you need to.


## Models

Contains a datatype suited for experiments with this package. It's called Acquisition.
It's an extended Python [deque](https://docs.python.org/3/library/collections.html#collections.deque).

It's designed to hold the events and it stores the pedestals and all the paramters used to capture the data.

## Parsers

The hardware sends data in bytes. The return data must be parsed before it can be interpreted. The dataformat is depent on the chip and/or firmware. Select a parser be importing `get_parser(model)`.

## Tools

This module contains higher level tools that changes multiple behaviours of the board such as calibrations and pedestals.

# Running the Tests

The tests are using [pytest](https://github.com/pytest-dev/pytest)
To run the tests simply do:

```
pytest tests\
```

The tests tests the internal package logic and use pytest-mocker to mock the hardware. Actual hardware testing is done manually.


# Coding style

All code is linted with ruff and follow pep8. The code is styled using Google's [style guide](http://google.github.io/styleguide/pyguide.html).
Before making any contributions to this package please make sure you lint the code and make sure the documentation follows the style guide. The only exception is the 100 col line width instead of 80.

We use pre-commit hooks to auto clean and lint the code.

Before pushing an update a developer must setup pre-commit and the correct hooks, this is done by:

```
pip install pre-commit
pre-commit install
```

# Versioning

We use [SemVer](http://semver.org) for versioning. For the versions available, see the [tags](https://github.com/NaluScientific/naludaq/tags) on this repository

See the [CHANGELOG.rst](CHANGELOG.rst)

# Authors

* **Ben Rotter**
* **Marcus Luck**
* **Mitchell Matsumori-Kelly**
* **Thomas Yang**
* **Alvin Yang**
* **Kenneth Laurtizen**
* **Emily Lum**


# License

This project is licensed under the LGPL License - see the [LICENSE.txt](LICENSE.txt) file for details

# Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
