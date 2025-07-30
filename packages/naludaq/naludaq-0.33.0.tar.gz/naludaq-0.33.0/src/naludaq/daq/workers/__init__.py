def get_usb_reader(board, serial_buffer, *args, **kwargs):
    """Get a usb reader depending on connection type"""
    conn_type = board.connection_info.get("type", "uart")

    if conn_type in ["ft60x"]:
        from naludaq.daq.workers.worker_usb_reader import UsbReader

        worker = UsbReader(
            board.connection,
            serial_buffer,
            *args,
            frequency=kwargs.get("frequency", 1000),
            **kwargs,
        )
    else:
        from naludaq.daq.workers.worker_serial_reader import SerialReader

        worker = SerialReader(
            board.connection,
            serial_buffer,
            *args,
            **kwargs,
        )
    return worker
