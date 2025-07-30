from naludaq.communication.registers import Registers


class RegisterCache:
    def __init__(self, board) -> None:
        """Cache utility for software registers.

        Args:
            board (Board): the board object, the source of register values.
        """
        self._board = board
        self._cache = {}

    @property
    def board(self):
        return self._board

    def add(self, name: str, reg_type: Registers):
        """Adds a register to be tracked by the cache.

        Args:
            name (str): the register name
            reg_type (Registers): the type of register (e.g. AnalogRegisters).

        Raises:
            TypeError if arguments are an invalid type
            KeyError if the register is already added, or is not a valid register.
        """
        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, not {type(name).__name__}")
        try:
            if not issubclass(reg_type, Registers):
                raise TypeError("Register type must be a subclass of Registers")
        except:
            raise TypeError("Registers must be a class")
        if name in self._cache:
            raise KeyError(f'The register "{name}" is already added.')
        try:
            value = reg_type(self._board).registers[name]["value"]
        except KeyError:
            raise KeyError(f'Register "{name}" is not a valid register')
        self._cache[name] = [reg_type, value]

    def get(self, name: str) -> int:
        """Gets a register value from the cache.

        Args:
            name (str): the register name.

        Returns:
            The value of the register

        Raises:
            TypeError if arguments are an invalid type
            KeyError if the register has not been added to the cache.
        """
        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, not {type(name).__name__}")
        try:
            return self._cache[name][1]
        except KeyError:
            raise KeyError(f'The register "{name}" has not been added.')

    def update(self, name: str, value: int = None):
        """Updates the value in the cache.

        Args:
            name (str): the name of the register.
            value (int): the value to set the register to.
                If `None`, the value from the software
                registers is used instead.

        Raises:
            TypeError if arguments are an invalid type
            KeyError if the register has not been added.
        """
        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, not {type(name).__name__}")
        if not isinstance(value, (int, type(None))):
            raise TypeError("Value must be int or None")
        try:
            if value is None:
                value = self._get_software_register(name)
            self._cache[name][1] = value
        except KeyError:
            raise KeyError(f'The register "{name}" has not been added.')

    def update_all(self, reg_values: dict = None):
        """Updates the cached values for all (or a subset of)
        all tracked registers.

        Args:
            reg_values (dict): a dict of {reg_name: reg_value} to
                update the cache with. If `None`, all registers are
                updated with the software registers.

        Raises:
            TypeError if arguments are an invalid type
            KeyError if one or more registers are not added.
        """
        if not isinstance(reg_values, (dict, type(None))):
            raise TypeError(
                f"Register values must be a dict or None, not {type(reg_values).__name__}"
            )
        if reg_values is None:
            for name in self._cache:
                self.update(name)
        else:
            for name, value in reg_values.items():
                self.update(name, value)

    def restore(self, name: str):
        """Writes the value held in the cache to the board.

        Args:
            name (str): the reigster name.

        Raises:
            TypeError if arguments are an invalid type
            KeyError if the register is not added.
        """
        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, not {type(name).__name__}")
        try:
            value = self.get(name)
            self._get_register_obj(name).write(name, value)
        except KeyError:
            raise KeyError(f'The register "{name}" has not been added.')

    def restore_all(self):
        """Writes all values held in the cache to the board.

        Raises:
            KeyError if the register is not added.
        """
        for name in self._cache:
            self.restore(name)

    def _get_register_obj(self, name: str) -> Registers:
        """Gets an instantiated `Registers` object that
        can be used to communicate with the given register.

        Args:
            name (str): the name of the register.

        Returns:
            The `Registers` object.

        Raises:
            TypeError if arguments are an invalid type
            KeyError if the register has not been added
        """
        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, not {type(name).__name__}")
        try:
            return self._cache[name][0](self._board)
        except KeyError:
            raise KeyError(f'The register "{name}" has not been added.')

    def _get_software_register(self, name: str):
        """Gets the value of a software register.

        Args:
            name (str): the register name

        Returns:
            The software register value

        Raises:
            TypeError if arguments are an invalid type
            KeyError if the register has not been added
        """
        if not isinstance(name, str):
            raise TypeError(f"Name must be a string, not {type(name).__name__}")
        try:
            return self._get_register_obj(name).registers[name]["value"]
        except KeyError:
            raise KeyError(f'The register "{name}" has not been added.')
