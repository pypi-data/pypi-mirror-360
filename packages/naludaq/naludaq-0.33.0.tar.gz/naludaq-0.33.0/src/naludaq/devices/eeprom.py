from typing import Sequence

import numpy as np

from naludaq.helpers.exceptions import InvalidParameterFile

from .i2c_device import I2CDevice


class EEPROM(I2CDevice):
    def __init__(self, board):
        """Class for controlling the M24M01 EEPROM.

        The M24M01 is a 1-megabit (128 kilobyte) I2C bus EEPROM. The full address space
        is accessible to the user.

        A portion of memory is addressed using a 17 bit address. The lower 16 bits
        are included in read/write commands, while the highest bit is actually the
        lowest bit of the device address.

        Args:
            board (Board): the board object.

        Raises:
            InvalidParameterFile: if the YAML does not contain a definition for the EEPROM
        """
        self._validate_eeprom_params_or_raise(board.params)
        self._eeprom_params = board.params["peripherals"]["eeprom"]
        self._default_addr = self._eeprom_params["addr"]
        super().__init__(board, self._default_addr)

        self._capacity = self._eeprom_params["capacity"]
        self._segments = self._eeprom_params["segments"]
        self._page_size = self._eeprom_params["page_size"]

        self._max_io_bytes = (
            4  # max bytes that can be sent/received with one I2C command
        )
        self._byte_order = ">"

    def store_array(self, addr: int, arr: "Sequence | np.ndarray", dtype: np.dtype):
        """Store an array into the EEPROM

        Args:
            addr (int): the starting address of the array
            arr (Sequence | np.ndarray): the array to store. For safety, the dtype
                of this array is ignored and the array is converted to the dtyep given
                instead.
            dtype (np.dtype): the dtype to store the array as. An object dtype cannot
                be used.

        Raises:
            TypeError: if the given combination of array and dtype results in an
                array that cannot be stored.
            I2CError: if there was a problem communicating with the device
        """
        dtype = self._convert_type_to_dtype_or_raise(dtype)
        arr = self._convert_array_dtype_or_raise(arr, dtype).flatten()
        self._validate_address_block_or_raise(addr, arr.size * dtype.itemsize)

        self.store_raw_data(addr, arr.tobytes())

    def load_array(self, addr: int, num_elements: int, dtype: np.dtype) -> np.ndarray:
        """Load an array from the EEPROM.

        The size of the block read depends on the number of elements in the
        array and the element data type.

        Args:
            addr (int): the starting address of the array
            num_elements (int): the number of elements in the array
            dtype (np.dtype): the data type for elements in the array

        Returns:
            np.ndarray: a 1-D array with the given data type.

        Raises:
            I2CError: if there was a problem communicating with the device
        """
        if not isinstance(num_elements, int):
            raise TypeError("Number of elements must be an int")
        dtype = self._convert_type_to_dtype_or_raise(dtype)
        self._validate_address_block_or_raise(addr, num_elements * dtype.itemsize)

        data = self.load_raw_data(addr, num_elements * dtype.itemsize)
        return np.frombuffer(data, dtype)

    def store_raw_data(self, addr: int, data: bytes):
        """Write raw data to the EEPROM memory.

        Args:
            addr (int): pointer to the start of the block to write.
            data (bytes-like): data to store in the EEPROM. Can be any size, as long
                as the data fits into the location provided (see YAML).

        Raises:
            I2CError: if there was a problem communicating with the device
        """
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data address must be bytes-like")
        self._validate_address_block_or_raise(addr, len(data))

        for start_addr, data_chunk in self._iter_data_chunks(addr, data):
            addr_bytes = self._get_data_addr_bytes(start_addr)
            self._set_addr_from_byte_loc(start_addr)
            self.send_write_command(addr_bytes + data_chunk)

    def load_raw_data(self, addr: int, amount: int) -> bytes:
        """Reads data from the EEPROM.

        Args:
            addr (int): pointer to the start of the block to read.
            amount (int): length of data to read. Can be any length, as long as the
                block does not exceed the boundaries of the storage array (see YAML).

        Returns:
            bytes: the data read from the EEPROM.

        Raises:
            I2CError: if there was a problem communicating with the device
        """
        self._validate_address_block_or_raise(addr, amount)

        result = bytearray()
        chunk_size = self._max_io_bytes
        for start_addr in range(addr, addr + amount, chunk_size):
            self._set_addr_from_byte_loc(start_addr)

            # NOTE: ack-checking after writing causes too much delay which ends up trashing the response
            self.send_write_command(
                self._get_data_addr_bytes(start_addr), check_ack=False
            )
            self.send_read_command(bytes([0xFF] * chunk_size), check_ack=False)
            response = self._read_response_registers()

            response = self._discard_ack_bits(response)[1 : chunk_size + 1]
            result += response

        return bytes(result[:amount])

    def _get_data_addr_bytes(self, data_addr: int):
        """Get the address for data as a `bytes` object.

        Args:
            data_addr (int): address of the data being written

        Returns:
            bytes: the 2-byte address
        """
        return data_addr.to_bytes(2, "big")

    def _set_addr_from_byte_loc(self, byte_loc: int):
        """Sets the device address based on the byte location. The lowest bit of
        the device address is the highest bit of the data address.
        """
        self._addr = self._default_addr + ((byte_loc >> 16) & 1)

    def _validate_address_block_or_raise(self, start: int, length: int):
        """Makes sure a block of addresses is fully contained within the range
        of valid addresses.

        Args:
            start (int): start address
            length (int): block length

        Raises:
            TypeError: if the start address or length is not an int.
            ValueError: if any portion of the block is out of bounds.
        """
        if not isinstance(start, int):
            raise TypeError("Data address must be int")
        if not isinstance(length, int):
            raise TypeError("Data length must be int")
        if length <= 0:
            raise ValueError("Data length cannot be negative")
        if not length <= start + length <= self._capacity:
            raise ValueError("Address block is out of bounds")

    @staticmethod
    def _validate_eeprom_params_or_raise(params: dict) -> int:
        """Validate EEPROM params in YAML.

        Args:
            params (dict): board params

        Raises:
            InvalidParameterFile: if the params are invalid.
        """
        eeprom_params = params.get("peripherals", {}).get("eeprom", None)
        if eeprom_params is None:
            raise InvalidParameterFile("Board does not have EEPROM support")

        required_entries = {
            "addr": int,
            "capacity": int,
            "segments": dict,
        }
        for name, type_ in required_entries.items():
            value = eeprom_params.get(name, None)
            if value is None:
                raise InvalidParameterFile(f'EEPROM params missing key "{name}"')
            if not isinstance(value, type_):
                raise InvalidParameterFile(
                    f'EEPROM params value for "{name}" has wrong type {type(value).__name__}, expected {type.__name__}'
                )

    def _convert_type_to_dtype_or_raise(self, dtype) -> np.dtype:
        try:
            dtype = np.dtype(dtype).newbyteorder(self._byte_order)
        except TypeError:
            raise
        if dtype is object:
            raise TypeError('Data type "object" cannot be safely stored')
        return dtype

    @staticmethod
    def _convert_array_dtype_or_raise(arr, dtype: np.dtype):
        arr = np.array(arr)
        try:
            arr = np.array(arr).astype(dtype)
        except ValueError as e:
            raise ValueError("Invalid array and/or datatype") from e
        if arr.dtype == object:
            raise TypeError('Data type "object" cannot be safely stored')
        return arr

    def _iter_data_chunks(self, start_addr: int, data: bytes):
        """Iterate over data in chunks. Yields (starting address, chunk data) for
        each chunk.

        The device doesn't allowing write operations that cross page boundaries,
        so this function splits a chunk that does cross boundaries into two smaller
        chunks that live on either side of the page boundary.

        If the data is not evenly divisible by the chunk size, then the last chunk
        is made smaller.
        """
        page_size = self._page_size
        chunk_size = self._max_io_bytes

        for i in range(0, len(data), chunk_size):
            # page numbers determined by edges of data addresses
            upper_page = (start_addr + i + chunk_size - 1) // page_size
            lower_page = (start_addr + i) // page_size

            if upper_page != lower_page:
                addr_boundary = upper_page * page_size
                data_boundary = addr_boundary - start_addr - i
                yield start_addr + i, data[i:data_boundary]
                yield addr_boundary, data[data_boundary : i + chunk_size]
            else:
                yield start_addr + i, data[i : i + chunk_size]
