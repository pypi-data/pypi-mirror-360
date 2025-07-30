# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['honeyshare', 'honeyshare.api']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.32.4,<3.0.0']

setup_kwargs = {
    'name': 'honeyshare',
    'version': '1.0.3',
    'description': 'Python API client for HoneyShare.live',
    'long_description': '# HoneyShareLib\n\nThe [HoneyShare](https://honeyshare.live/) API Client.\n\n## Installing\n\nAvailable in [PYPI](https://pypi.org/project/honeyshare/).\n\n    pip install honeyshare\n\n## Usage\n\nInitialize HoneyShare with a [Key](https://honeyshare.live/licenses):\n\n    from honeyshare import HoneyShare\n\n    hs = HoneyShare(key="Your HoneyShare Key"")\n\nThe library is organized around the five HoneyShare objects:\n\n    hs.Blacklist.ipv4s()     // Blacklists of IPs\n    hs.Blacklist.hostnames() // Blacklists of Hostnames\n\n    hs.IPv4.list()               // IP list\n    hs.IPv4(ip).ipv4()           // IP\'s meta data\n    hs.IPv4(ip).ports()          // Ports accessed by IP\n    hs.IPv4(ip).hostnames()      // Hostnames of IP\n    hs.IPv4(ip).timeseries()     // Timeseries of IP\n    hs.IPv4(ip).timeseries(port) // Timeseries of IP on Port\n    hs.IPv4(ip).bytes(port)      // Bytes sent by IP on Port\n\n    hs.Hostname.list()               // Hostname list\n    hs.Hostname(hostname).hostname() // Hostname\'s meta data\n    hs.Hostname(hostname).ipv4()     // IPs of Hostname\n\n    hs.Port.list()          // List of Ports\n    hs.Port(port).port()    // Port\'s meta data\n    hs.Port(port).ipv4()    // IP\'s that acceed port\n    hs.Port(port).ipv4(ip)  // IP\'s meta data on Port\n    hs.Port(port).bytes(ip) // Bytes sent by IP on Port\n\n    hs.Timeseries.list() // List all connections\n\n## Building and Installing Locally\n\n    poetry build\n    pip install --force-reinstall dist/honeyshare-*.whl\n',
    'author': 'Pedro Melgueira',
    'author_email': 'pedro@honeyshare.live',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
