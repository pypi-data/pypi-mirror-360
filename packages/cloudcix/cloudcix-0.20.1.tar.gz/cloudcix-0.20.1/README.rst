Overview
========

``cloudcix`` is a Python client for the CloudCIX REST API for rapidly building secure, scalable CloudCIX applications.

For more information about CloudCIX, see `here <https://www.cloudcix.com/>`__.

Installation
------------

Prerequisites
~~~~~~~~~~~~~
1. Create an account on the CloudCIX Platform

   - `Register <https://saas.cloudcix.com/auth/register>`__

2. Retrieve your API Key

   - Under the ``My Membership`` tab in the sidebar, click on ``Member Details``
   - The ``API Key`` should be available at the top of the form

3. Ensure that you have both Python and pip installed

   - As of right now, the ``cloudcix`` module is available at different versions for Python2 and Python3
   - We recommend you use Python3 and the latest version of the ``cloudcix`` module
   - `Python <http://docs.python-guide.org/en/latest/starting/installation/>`__
   - `pip <https://pip.pypa.io/en/stable/installing/>`__

Installing the ``cloudcix`` library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The cloudcix library is installed using the ``pip`` module.

Depending on your version of Python, you need to install different versions of ``cloudcix``

- Python3
   - ``pip3 install -U cloudcix``
- Python2
   - ``pip install -U 'cloudcix<0.3'``

The 0.2 releases are the last to support Python2.
If you still use Python2 we recommend you upgrade to Python3 as support will be dropped for these versions in time.

Required settings
~~~~~~~~~~~~~~~~~
In order to run a project, the module requires some settings to exist.

The variables required are as follows:

- ``CLOUDCIX_API_URL`` = ``https://legacyapi.api.cloudcix.com/``
  - The base url of the Python2 API
- ``CLOUDCIX_API_V2_URL`` = ``https://api.cloudcix.com/`` 
  - The API name is prepended to this url after the https:// for the Python3 API. 
- ``CLOUDCIX_API_VERSION`` = 2
  - The version of the api
- ``CLOUDCIX_API_USERNAME``
  - The email of the account that you signed up with
- ``CLOUDCIX_API_PASSWORD``
  - The password associated with your CloudCIX account
- ``CLOUDCIX_API_KEY``
  - The API key associated with your CloudCIX Member (see **Prerequisites**)

These variables can be declared in a settings file, as follows

.. code:: python

    # In main python script
    import os
    os.environ.setdefault('CLOUDCIX_SETTINGS_MODULE', 'my_project.my_settings')

.. code:: python

    # In my_project/my_settings.py
    CLOUDCIX_API_URL = 'https://legacyapi.api.cloudcix.com/'
    CLOUDCIX_API_V2_URL = 'https://api.cloudcix.com/'
    CLOUDCIX_API_USERNAME = 'EMAIL'               # CloudCIX login
    CLOUDCIX_API_PASSWORD = 'PASSWORD'            # CloudCIX password
    CLOUDCIX_API_KEY = 'NUMBER/CHARACTER STRING'  # CloudCIX api key
    CLOUDCIX_API_VERSION = 2                      # CloudCIX version

Examples
--------
See `here <https://cloudcix.github.io/python-cloudcix/examples.html>`_ for examples on how to use this library.
