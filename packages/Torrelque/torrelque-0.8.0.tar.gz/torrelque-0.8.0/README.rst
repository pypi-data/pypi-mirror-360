.. image:: https://img.shields.io/pypi/l/Torrelque.svg
   :target: https://spdx.org/licenses/LGPL-3.0-only.html
   :alt: PyPI - License
.. image:: https://heptapod.host/saajns/torrelque/badges/branch/default/pipeline.svg
   :target: https://heptapod.host/saajns/torrelque/-/commits/branch/default
   :alt: Pipeline status
.. image:: https://heptapod.host/saajns/torrelque/badges/branch/default/coverage.svg
   :target: https://saajns.heptapod.io/torrelque/htmlcov/?badge=coverage
   :alt: Test code coverage
.. image:: https://badge.fury.io/py/Torrelque.svg
   :target: https://pypi.python.org/pypi/Torrelque
   :alt: PyPI
.. image::
   https://img.shields.io/gitlab/pipeline-status/saajns%2Ftorrelque
   ?gitlab_url=https%3A%2F%2Fheptapod.host&branch=branch%2Fdefault&label=documentation
   :target: https://saajns.heptapod.io/torrelque/
   :alt: RTFM

*********
Torrelque
*********
Torrelque is a Python package that provides minimal asynchronous reliable
distributed Redis-backed (or a protocol-compatible alternative) work queues.
It is built:

1. Lock-free. It relies on Redis transactions and its single-threaded
   execution model.
2. Poll-free. Waiting subset of the Python API relies either on blocking Redis
   commands or notifications.
3. Bulk-friendly. Tasks can be produced and consumed in bulk.
4. Introspectable. Task stats, task status transition watching API, and
   the data model comprehensible directly in Redis.

Supported Redis server implementations: Redis, KeyDB, Valkey.

Install
=======
::

   pip install Torrelque

Quickstart
==========
Producer:

.. sourcecode:: python

   import redis.asyncio
   import torrelque

   client = redis.asyncio.Redis()
   queue = torrelque.Torrelque(client, queue='email')
   queue.schedule_sweep()  # to make due requeued tasks available again

   task_data = {'addr': 'joe@doe.com', 'subj': 'hello', 'body': '...'}
   task_id = await queue.enqueue(task_data)
   print('Email task enqueued', task_id)

Consumer:

.. sourcecode:: python

   import redis.asyncio
   import torrelque

   client = redis.asyncio.Redis()
   queue = torrelque.Torrelque(client, queue='email')

   while True:
       task_id, task_data = await queue.dequeue()
       try:
           await some_email_client.send(**task_data)
       except Exception:
           print('Email sending error, retrying in 30s', task_id)
           await queue.requeue(task_id, delay=30)
       else:
           print('Email sent', task_id)
           await queue.release(task_id)

Example list
============
- `Producer-consumer <e1_>`_. Infinite producing and consuming loops.
- `Batch processing <e2_>`_. Finite number of tasks, consumers stop with a
  poison pill, bulk enqueue. This example can be used as a synthetic benchmark.
  Because there's no IO-bound workload, it'll be CPU-bound which isn't normal
  mode of operation for an asynchronous application. But it can be used to
  compare between CPython, PyPy and concurrency parameters.
- `Web application background task <e3_>`_. This tornado application allows
  to start a task and push server-sent events (SSE) to UI about its status. UI
  starts a task and waits for it to complete. When a task fails it's re-queued
  with exponential back-off.


.. _e1: https://heptapod.host/saajns/torrelque/blob/branch/default/example/producer_consumer.py
.. _e2: https://heptapod.host/saajns/torrelque/blob/branch/default/example/batch_processing.py
.. _e3: https://heptapod.host/saajns/torrelque/blob/branch/default/example/wait_until_complete.py
