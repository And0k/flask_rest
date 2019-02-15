Flask restful service in docker
===============================

# Description

Python Flask restful API running with `Meinheld <https://github.com/mopemope/meinheld>`_ controlled by `Gunicorn <http://gunicorn.org>`_.
When receives list of urls of images it converts them to black and white and serve in local folder

Test docker image on Linux
--------------------------
su
systemctl start docker
docker-compose -f /home/korzh/Python/PycharmProjects/flask_rest/docker-compose.yml up -d

Try out JSON and HTML requests
------------------------------
API supports content negotiation so you can browse results starting from main page _http://127.0.0.1:5000/_
Send requests directly to this address or REST API using documentation provided by `Swagger UI <https://swagger.io/tools/swagger-ui/>`_ at
_http://127.0.0.1:5000/doc_

---

This is a test. Original task [russian] see in system-tech_task[ru].rst