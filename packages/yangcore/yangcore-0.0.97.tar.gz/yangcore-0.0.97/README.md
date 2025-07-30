# YANGcore

YANGcore is a Python based application server having a [RESTCONF](https://tools.ietf.org/html/rfc8040)-based interface binding to a [SQL Alchemy](https://www.sqlalchemy.org)-based database backend.


## Installation

  `pip install yangcore`

## Overview

  - HTTPS or HTTP
  - RESTCONF HEAD, GET, POST, PUT, and DELETE work over entire tree.
  - Ordered-by user query parameters ('insert' and 'point') work.
  - [List Pagination](https://datatracker.ietf.org/doc/html/draft-ietf-netconf-list-pagination-rc) query parameters ('limit', 'offset', and 'direction') work.
  - The ./well-known/host-meta, RESTCONF root (i.e., {+restconf}), and YANG-library resources.
  - Tested using in-memory, file-base, MySQL and, a long time ago, AWS Aurora and Postgres.
  - TLS connection to backend RDBMS, with or w/o client certificate.
  - Logging and dynamic callouts for Audit log and Notifications log
  - Database-level transactions and concurrent access.
  - In-memory database support for ephemeral use-cases.
  - Lightweight and fast: single-threaded [Asynchronous I/O](https://docs.python.org/3/library/asyncio.html).
  - Python 3.11 and 3.12

## Motivation

RESTCONF is great REST API right out of the box.  The API is auto-generated off of a collection of
YANG modules, which defines the API contract.  YANG is the popular data modelling langauge defined
by the IETF ([RFC 7950](https://www.rfc-editor.org/rfc/rfc7950.html))and recommended by the Internet
Architecture Board.

As far as APIs go, RESTCONF ([RFC 8040](https://www.rfc-editor.org/rfc/rfc8040.html)) scores high on
both the [Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)
and the [Amundsen Maturity Model](http://amundsen.com/talks/2016-11-apistrat-wadm/index.html) models.
See [API Maturity](https://medium.com/good-api/api-maturity-fb25560151a3) for a description for what
makes for a good API.

Python is a popular programming language.  A Python implementation of a RESTCONF server
seems like it could be popular.  Searching for Python-based RESTCONF tooling found
[Jetconf](https://github.com/CZ-NIC/jetconf), but its been abandoned.

Thus there seemed to be an opportunity to work and YANGcore became something.

<!--
An API contract is key to success.  But popular API-modelling languages ([Swagger/OpenAI](https://swagger.io/specification/), [RAML](https://raml.org), [API Blueprint](https://apiblueprint.org), etc.) seem weak relative to [YANG](https://datatracker.ietf.org/doc/html/rfc8341) when coupled with [RESTCONF](https://tools.ietf.org/html/rfc8040).
-->

<!--
[RESTful JSON](https://restfuljson.org) and [Marshmallow](https://marshmallow.readthedocs.io/en/stable)
YANG is a better API modelling language than [JSON Schema](https://json-schema.org).
-->


## More Information

Please see the [documentation](https://watsen.net/docs) for more information.

