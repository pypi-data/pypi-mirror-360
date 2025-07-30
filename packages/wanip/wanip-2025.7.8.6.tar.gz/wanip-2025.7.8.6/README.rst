wanip
=====

Determine your WAN IP, using publicly available providers

Example usage
-------------

.. code-block:: bash

    $ wanip -h
    usage: wanip [-h] [-p PROVIDER] [-4 | -6] [-v]

    Ask a provider for your ip with which you connect to it, then print it out

    options:
      -h, --help            show this help message and exit
      -p, --provider PROVIDER
                            the provider to contact, instead of pseudo-randomly auto-selecting one from a pre-built
                            internal list (default: None)
      -4, --ipv4            force the usage of IPv4 (default: False)
      -6, --ipv6            force the usage of IPv6 (default: False)
      -v, --verbose         used once: show which provider will be contacted; used twice (or more often):
                            display contactable providers as well (i.e., the pre-built internal list) (default: 0)

    Respect the netiquette when contacting the provider.
    $ wanip -4
    80.167.65.60
    $ wanip -6vv
    https://api.ipify.org
    https://checkip.amazonaws.com
    https://eth0.me/
    https://icanhazip.com
    https://ident.me
    https://ifconfig.co
    https://ifconfig.me/ip
    https://ip.me
    https://ipapi.co/ip
    https://ipecho.net/plain
    https://ipinfo.io/ip
    https://iprs.fly.dev
    https://l2.io/ip
    https://my.ip.fi
    https://wgetip.com
    https://whatismyip.akamai.com
    https://www.trackip.net/ip
    Trying https://ifconfig.me/ip
    2a01:599:b44:be52:9f91:3767:2b2f:cd93

Installation
------------

The `project <https://pypi.org/project/wanip/>`_ is on PyPI, so simply run

.. code-block:: bash

    $ python -m pip install wanip
