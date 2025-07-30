import psutil


def list_available_addresses():
    """
    List all available network addresses on the system.
    :return: A list of tuples containing interface names and their corresponding addresses.
    """
    addresses = list()
    addresses.append(('All IPV4 interfaces', '0.0.0.0'))
    addresses.append(('All IPV6 interfaces', '::'))
    for interface in psutil.net_if_addrs().items():
        for addr in interface[1]:
            if addr.family.name == 'AF_INET':
                addresses.append((interface[0], addr.address))
            elif addr.family.name == 'AF_INET6':
                addresses.append((interface[0], f'[{addr.address}]'))
    return addresses

if __name__ == '__main__':
    for interface_name, address in list_available_addresses():
        print(f"{interface_name}: {address}")