Summary
-------

This cube allows a client to forge signed HTTP resquests that are then
recognized as valid by the CubicWeb web server, ie. the request is
handled as an authenticated user. For example, it can be used to start
an operation using an authenticated user.

It's usually used alongside with cubicweb-rqlcontroller_ and
cwclientlib_.

This cube aims at make it easy to write REST-like APIs for CW.

Long story short: cubicweb-signedrequest_ allows you to make
authenticated HTTP requests simply by addind a properly forged HTTP
header in your request.

.. Warning:: cubicweb-signedrequest_ is **very** ticklish about time:
             your request will be refused is the ``Date`` header if
             not very accurate. Also, for security reasons, you won't
             have any detail on why your request has been denied.


How to use signed HTTP requests in your CubicWeb app?
-----------------------------------------------------

This cube aims at making it possible to use tokens to authenticate to
a CubicWeb application. It provides a Token entity that have a unique
``token_id`` attribute and a generated (secret) token. This `Token`
entity is related to a ``CWUser`` (using the `token_for_user`
relation).

It's the possible to make authenticated HTTP requests (authenticated
as this CWUser) by adding a `Authorization` header to the HTTP
request. This header is computed as a HMAC hash with:

  - the secret token as key,

  - the concatenation os `method` + `url` + all the signed headers.


By default, the `method` is the `Cubicweb` string, and the signed
headers are 'Content-SHA512', 'Content-Type' and 'Date'.

The `doc/sreq_example.py` script is an simple python script showing how to
forge such a HTTP GET request using `urllib2`.

Please read the documentation of cwclientlib_ for examples of how it
can be used.

.. _cubicweb-rqlcontroller: https://www.cubicweb.org/project/cubicweb-rqlcontroller
.. _cubicweb-signedrequest: https://www.cubicweb.org/project/cubicweb-signedrequest
.. _cwclientlib: https://www.cubicweb.org/project/cwclientlib
