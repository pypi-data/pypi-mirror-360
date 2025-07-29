# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chatty_shell']

package_data = \
{'': ['*']}

install_requires = \
['langchain-community>=0.3.27,<0.4.0',
 'langchain-openai>=0.3.27,<0.4.0',
 'langchain>=0.3.26,<0.4.0',
 'langgraph>=0.5.1,<0.6.0']

entry_points = \
{'console_scripts': ['chat = chatty_shell.main:main']}

setup_kwargs = {
    'name': 'chatty-shell',
    'version': '0.1.5',
    'description': '',
    'long_description': None,
    'author': 'Artur Dernst',
    'author_email': 'artur@dernst.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
