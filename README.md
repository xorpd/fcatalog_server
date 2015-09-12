The FCatalog Server
===================

FCatalog is the Functions Catalog. It allows to save large amount of different
binary blobs, and find similarities quickly between them and a given new binary
blob. 
FCatalog server works together with a python client that runs with IDA
pro.

This was written to help binary reversers find similar functions, however it
might be useful for other purposes as well.

You can find the [fcatalog_client repository here](https://github.com/xorpd/fcatalog_client).

Installation
------------

When you have internet connection, run:

    ./get_deps

This will fetch all the needed dependencies from the internet. Now just copy
everything and put it on a disk.

On an offline setting, run:

    sudo ./install

This should install the fcatalog server. You can uninstall using:

    sudo ./uninstall


Using the server
----------------

To start the server run:

    sudo start fcatalog

To stop the server run:

    sudo stop fcatalog


The server will start by default on 127.0.0.1:1337

Tests
-----

Install pytest:

    pip install pytest

and run:

    py.test


Website
-------

If you like this, you might like other stuff at http://www.xorpd.net
