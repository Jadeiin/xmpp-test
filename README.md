# xmpp-test

xmpp-test is a library, command-line utility and webservice that allows you to test the DNS and TLS setup of
an XMPP server.

**NOTE:** This library is still in early development stages

## Installation

This script requires at Python3.6 or later. It is strongly recommended that you use
[pyenv](https://github.com/pyenv/pyenv) and 
[pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

For now, only cloning the GIT repository is supported:

```
git clone https://github.com/mathiasertl/xmpp-test.git
```

After that, you can installl required library dependencies using:

```
pip install -r requirements.txt
```

## CLI usage

See

```
python xmpp-test.py -h
```

for usage

## Start webserver

You can start a simple HTTP webserver using:

```
python xmpp-test.py http-server
```

Note that this server is extremely basic and is intended to be used behind a real HTTP server.

## Docker

This library uses Python and can only test what the underlying OpenSSL/LibreSSL implementation and the Python
version used support. Thus there are different Dockerfiles using different combinations of Python and OpenSSL
to be able to test across a broad range of TLS versions and ciphers.
