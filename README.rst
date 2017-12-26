apptoolkit
===========

.. image:: https://img.shields.io/pypi/v/apptoolkit.svg
    :target: https://pypi.python.org/pypi/apptoolkit/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/wheel/apptoolkit.svg
    :target: https://pypi.python.org/pypi/apptoolkit/

.. image:: https://img.shields.io/pypi/pyversions/apptoolkit.svg
    :target: https://pypi.python.org/pypi/apptoolkit/

.. image:: https://img.shields.io/pypi/l/apptoolkit.svg
    :target: https://pypi.python.org/pypi/apptoolkit/

Introduction
-----------

This is a lightweight set of tools for obtaining information about Android devices in Python

Installing
----------

Install and update using `pip`:

.. code-block:: text

    pip install -U apptoolkit

A Simple Example
----------------

.. code-block:: python

    from apptoolkit import Device

    android_devices = Device.get_android_devices()

    下面是输出信息：
    [
    {
        "uid": "BY2WKN1519078327",
        "rom_version": "Che2-UL00 V100R001CHNC00B287",
        "brand": "Honor",
        "os_version": "4.4.2",
        "sdk_version": "19",
        "os_type": "Android",
        "model": "Che2-UL00"
    },
    {
        "uid": "GWY0217414001213",
        "rom_version": "MHA-AL00C00B213",
        "brand": "HUAWEI",
        "os_version": "7.0",
        "sdk_version": "24",
        "os_type": "Android",
        "model": "MHA-AL00"
    }
    ]

    ios_devices = Device().get_ios_devices()

    下面是输出信息：
    [
    {
        "uid": "xxxxxxxxxxxxxx1f8a4dcfaac1fd01",
        "rom_version": "11.0.3",
        "brand": "iPhone",
        "device_name": "马飞的 iPhone",
        "os_version": "11.0.3",
        "model": "iPhone6s",
        "os_type": "iOS"
    }
    ]
  
Learn more
-----------

You can read this http://mafei.me/ to learn more about the `apptoolkit`.
