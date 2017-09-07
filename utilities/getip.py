# A generic class written for utils to use throughout
# the codebase. Written for the purpose of duplicated functionality
# as detected by code climate.

import socket


def get_ip():
    # http://stackoverflow.com/a/28950776/671626
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 0))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP