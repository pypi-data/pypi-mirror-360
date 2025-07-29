
# Aguirre

> Let Python webservers self-host JS/CSS/etc assets like unpkg does

**Warning: The utility functions have been proven out,
but the integrations have had limited usage.
Treat them with caution.**

When your Python application needs a Python dependency from PyPI
you can lean on tools like `pip` and `venv` to manage that.
But what if its a web application that needs a Javascript or
CSS dependency from NPM?
Large applications run by large teams can justify elaborate
build and deployment pipelines.
But a smaller app?
Something internal?
A demo?
Or a learning exercise?
You want a lighter solution...

In recent years it's become popular to lean on unpkg for this.
(Or jsdelivr, or cdnjs, or another service.)
How easy it is to drop one line into your template and let a CDN
look after serving the file to your users:

    <script src="https://www.unpkg.com/jquery@3.7.1/dist/jquery.min.js"></script>

But there are disadvantages to relying on a third party like this.
It needs to be up whenever your app is up, and be reliable.
You are vulnerable to takedowns (remember left-pad?).
Your users give up more privacy.
And worst of all: you can't develop your application offline.

Aguirre lets you download NPM tarballs and add them to your app.
(And probably commit them in too.)
Then you can drop a line into your app and let Aguirre serve the
desired file straight out of the tarball:

    <script src="/pkgs/jquery@3.7.1/dist/jquery.min.js"></script>

Sure, it's not the most scalable solution.
But it's a great way to quickly get things moving.

## Installation

This code is not currently on PyPI.
Consequently you should add the following line to your
`requirements.txt` file:

    git+https://github.com/pscl4rke/aguirre.git

## Integrations

There are some integrations into frameworks inside
`aguirre.integrations`.
Their usage is documented in the module docstrings...

* [Flask](https://github.com/pscl4rke/aguirre/blob/master/aguirre/integrations/flask.py)
* [Quart](https://github.com/pscl4rke/aguirre/blob/master/aguirre/integrations/quart.py)
* [Django](https://github.com/pscl4rke/aguirre/blob/master/aguirre/integrations/django.py) (Partial!)

## Development and Testing

This codebase uses
[ephemerun](https://github.com/pscl4rke/ephemerun)
to test against multiple Python versions.
(It's a bit like Tox,
except is uses containers for isolation rather than virtualenvs.)

## Roadmap

* Better Django support
* Handle `pathlib.Path` arguments

## Licence

This code is copyright P. S. Clarke and is licensed under
the BSD-3-Clause licence.

The test suite contains real-world example files.
These are covered by their own embedded licences.
