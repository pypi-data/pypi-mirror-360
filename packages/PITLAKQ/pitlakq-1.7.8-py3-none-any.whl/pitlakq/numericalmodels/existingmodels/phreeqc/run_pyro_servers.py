"""Start Pyro servers for PHRREQC distributed calculations.
"""

import subprocess


def start_servers(n=4):
    """Start n Pyro servers.
    """
    for server_count in range(1, n + 1):
        cmd = 'start "Server %d" /wait python phreeqc_pyro_server.py _node%d'
        cmd = cmd % (server_count, server_count)
        subprocess.Popen(cmd, shell=True)


if __name__ == '__main__':
    start_servers()
