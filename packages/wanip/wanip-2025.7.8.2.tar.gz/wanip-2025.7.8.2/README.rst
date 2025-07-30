wanip
=====

Determine your WAN IP, using publicly available providers

Example usage
-------------

.. code-block:: bash

    $ wanip -h
    usage: wanip [-h] [-p PROVIDER] [-4] [-v]

    Ask a provider for your ip with which you connect to it, then print it out

    options:
      -h, --help            show this help message and exit
      -p, --provider PROVIDER
                            the provider to contact, instead of pseudo-randomly auto-selecting one from a pre-built
                            internal list (default: None)
      -4, --ipv4            force the usage of IPv4 (default: False)
      -v, --verbose         used once: show which provider will be contacted; used twice (or more often):
                            display contactable providers as well (i.e., the pre-built internal list) (default: 0)

    Respect the netiquette when contacting the provider.

Installation
------------

The `project <https://pypi.org/project/wanip/>`_ is on PyPI, so simply run

.. code-block:: bash

    $ python -m pip install wanip
