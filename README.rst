Flask restful service in docker
===============================

**GitHub repo**: <https://github.com/And0k/flask_rest>

**Docker Hub image**: <https://hub.docker.com/r/and0k/flask_rest>


Description
-----------

Python Flask restful API running with `Meinheld <https://github.com/mopemope/meinheld>`_ controlled by `Gunicorn <http://gunicorn.org>`_.
When receives list of urls of images it converts them to black and white and serve in local folder.

Test restful service without docker
-----------------------------------

* run ``pipenv install -dev``
* run tests using pipenv from ``/test/``
* to run Flask development server run ``manage.py`` from ``/service_images/`` directory.

Docker image was build on Alpine Linux and has size 155MB. Download image: ``docker pull and0k/flask_rest``

Build docker image on Linux
---------------------------

Clone repository and run from its directory:

``pipenv install``

``su``

``systemctl start docker``

``docker-compose -f docker-compose.yml up -d``

Try out JSON and HTML requests
------------------------------
API supports content negotiation so you can browse results starting from main page ``http://127.0.0.1:5000/``.
Send requests directly to this address or REST API using documentation provided by `Swagger UI <https://swagger.io/tools/swagger-ui/>`_ at
``http://127.0.0.1:5000/doc``.

---

This is a test. Original task (russian) see in ``/system-tech_task[ru].rst``
