

def calc_checksum(data: bytes):
    """
    Calculate checksum for a command without checksum byte.
    """
    data = data[2:]
    checksum = 0
    for byte in data:
        checksum += byte
        checksum = checksum % 256
    return checksum


def check_checksum(data: bytes):
    checksum = calc_checksum(data[:-1])
    return checksum == data[-1]
