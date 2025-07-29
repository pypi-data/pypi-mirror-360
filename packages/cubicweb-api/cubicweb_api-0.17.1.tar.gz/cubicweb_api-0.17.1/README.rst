Summary
================

.. Useful links
.. _RQLController cube: https://forge.extranet.logilab.fr/cubicweb/cubes/rqlcontroller
.. _CubicWebJS: https://forge.extranet.logilab.fr/cubicweb/cubicwebjs
.. _React Admin CubicWeb: https://forge.extranet.logilab.fr/cubicweb/react-admin
.. _OpenAPI: https://www.openapis.org
.. _JWT: https://jwt.io
.. _CubicWeb Repository: https://forge.extranet.logilab.fr/cubicweb/cubicweb
.. _Matrix channel: https://matrix.to/#/#cubicweb:matrix.logilab.org

This cube exposes the new api, replacing the `RQLController cube`_ with a simpler architecture.
We plan on integrating this new API directly into CubicWeb, without having to rely on this cube.

You can use the `CubicWebJS`_ client to communicate with this API in JavaScript.
See the project `React Admin CubicWeb`_ for an example on how to use `CubicWebJS`_.


**⚠️ Please note this cube will later be integrated into CubicWeb.
The installation instructions only applies for the API cube while it lives in its own repository.**

Vision
------

The goal is to offer a minimal API surface,
similar to data-servers compatible with SPARQL.
To this end, this API mainly offers a route to send RQL requests to.

There are only a few helper endpoints to login, fetch the data schema
and retrieve debug information about the server setup.
Those are either impossible to express in RQL,
or essential to have to simplify debugging.

**We will not create endpoints to make common RQL requests easier.**
Instead it is the responsibility of each client
to make creating those requests easier by offering helpers.

If you have trouble expressing your need through RQL,
please ask your question in our `Matrix channel`_ or
open an issue on the `CubicWeb Repository`_.
Depending on the need we may update RQL to add new features!

Setup
-----

Install this cube with pip by running:

``pip install cubicweb_api``

Then open the ``__pkginfo__.py`` of your CubicWeb instance
and add ``cubicweb-api`` in the ``__depends__`` dictionary.

Existing instances
~~~~~~~~~~~~~~~~~~

If you are adding the api to an existing instance,
you need to manually add the cube and run a migration.
To do so, run the following commands
(replacing ``<YOUR_INSTANCE>`` with your instance name):

Open a shell using `cubicweb-ctl shell <YOUR_INSTANCE>`.
In that shell type `add_cube(api)`, then `exit()` to leave the shell.

And finally upgrade your instance:

``cubicweb-ctl upgrade <YOUR_INSTANCE>``

The command will ask you to edit the ``all-in-one.conf`` file.
Accept the changes to write the default configuration options available for this cube.

Configuration options
~~~~~~~~~~~~~~~~~~~~~

Several configuration options are available in `pyramid.ini`:

``cubicweb_api.api_path_prefix``
''''''''''''''''''''''''''''''''

Path after the hostname on which to serve the api. Defaults to ``api``.
The api version number will be added after this prefix (only v1 for now).

**Example:**

For a cubicweb instance deployed on ``http://localhost:8080``.

The api will be deployed by default  at ``http://localhost:8080/api/v1``.

If you set the option to ``cubicweb_api.api_path_prefix = my/custom/path``,
it will be then be deployed on ``http://localhost:8080/my/custom/path/v1``

``cubicweb.includes = cubicweb_api.auth.routes``
''''''''''''''''''''''''''''''''''''''''''''''''

Include ``cubicweb_api.auth.routes`` to enable the login and logout routes.
These routes will use whatever authentication policy is enabled in cubicweb.

``cubicweb.includes = cubicweb_api.auth.jwt``
'''''''''''''''''''''''''''''''''''''''''''''

Include ``cubicweb_api.auth.jwt`` to enable the JWT cookie authentication policy.

**⚠️ This feature is experimental, do not use in production**

Available Routes
----------------

This cube uses the `OpenAPI`_ specification to describe and validate data.
The complete specification is available in `openapi_template.yaml <cubicweb_api/openapi/openapi_template.yaml>`_.

On running instances, the ``<PREFIX>/openapi`` route provides the specification in an interactive HTML page
(http://localhost:8080/api/v1/openapi with default settings).
The ``<PREFIX>/openapi.yaml`` route provides the raw YAML file.

Authentication
--------------

When sending valid credentials to the login route,
a `JWT`_ token will be generated and sent in the ``Set-Cookie`` header.
This token must be sent as a cookie for each request to be successful.

Please note the login route is disabled by default (see section "Configuration options").

Troubleshooting
---------------

**Pyramid**

Depending on your pyramid configuration,
you may need to manually include the api
routes by adding this line in your pyramid.ini

``cubicweb.includes = cubicweb_api``
