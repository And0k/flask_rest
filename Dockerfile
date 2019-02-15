ARG DIR_NAME=service_images
ARG PACKAGES="zlib-dev jpeg-dev py3-pillow"
#
# This is where pip will install to:
ARG PYTHONUSERBASE=/pyroot
ARG PYTHON_VER=3.6
# ENV PYTHON_VERSION is used already in base images and it is 3-digit


ARG PYTHONPATH_ARG=$PYTHONUSERBASE/lib/python${PYTHON_VER}

#--- Development image ----------------------------------------------------------------
FROM python:${PYTHON_VER}-alpine3.8 as builder
LABEL maintainer="Andrey Korzh <ao.korzh@gmail.com>"
# Getting values of all global arguments
ARG DIR_NAME
ARG PACKAGES
ARG PYTHONUSERBASE
ARG PYTHON_VER
ARG PYTHONPATH_ARG

ENV LANG C.UTF-8
RUN apk --no-cache add ${PACKAGES}
RUN pip3 install pipenv
RUN mkdir -p ${PYTHONUSERBASE}

ENV PYTHONUSERBASE=$PYTHONUSERBASE \
    PYTHONPATH=$PYTHONPATH_ARG:$PYTHONPATH \
    PATH=$PYTHONUSERBASE/bin:$PATH

## THE MAIN COURSE: Install Application into container
# Install dependencies # Pipfile Pipefile.lock ./
WORKDIR /build
COPY ./dist/no_pillow/Pipfile .
RUN PIP_USER=1 PIP_IGNORE_INSTALLED=1 pipenv install --system --deploy --skip-lock

## Install our application
# COPY dist/*.whl ./
# RUN pip3 install --user --ignore-installed *.whl


#--- Production image -----------------------------------------------------------------
FROM tiangolo/meinheld-gunicorn:python${PYTHON_VER}-alpine3.8 as prod
LABEL maintainer="Andrey Korzh <ao.korzh@gmail.com>"
# Getting values of all global arguments
ARG DIR_NAME
ARG PACKAGES
ARG PYTHONUSERBASE
ARG PYTHON_VER
ARG PYTHONPATH_ARG


ENV LANG C.UTF-8
RUN apk --no-cache add ${PACKAGES}
# --virtual .build-deps \ && apk del .build-deps

# This is crucial for pkg_resources to work
ENV PYTHONUSERBASE=$PYTHONUSERBASE \
    PYTHONPATH=$PYTHONPATH_ARG:$PYTHONPATH:/usr/lib/python$PYTHON_VER:/usr/lib/python$PYTHON_VER/site-packages \
    PATH=$PYTHONUSERBASE/bin:$PATH
# added some as /usr/lib/python3.6/site-packages to PYTHONPATH because it is set to /app only in base image (https://github.com/tiangolo/meinheld-gunicorn-docker/blob/master/python3.6-alpine3.8/Dockerfile)

# Finally, copy artifacts  (currently builder's service_images and test are in /pyroot/lib/python3.6/site-packages/)
COPY --from=builder $PYTHONUSERBASE/ $PYTHONUSERBASE/
#COPY --from=builder $PYTHONUSERBASE/bin/$DIR_NAME $PYTHONUSERBASE/bin/

# Install our application
WORKDIR /app
COPY $DIR_NAME ./$DIR_NAME

#RUN chown -R rest:rest $PYTHONUSERBASE/lib/
#USER rest

# Gunicorn configuration (http://docs.gunicorn.org/en/latest/run.html) used by base image
# (see also https://github.com/tiangolo/meinheld-gunicorn-docker or https://github.com/tiangolo/meinheld-gunicorn-flask-docker)
#   file that contains Flask application to be imported by Gunicorn
ENV MODULE_NAME="$DIR_NAME.manage"
#   We use defaults for VARIABLE_NAME=app, WORKERS_PER_CORE, HOST, LOG_LEVEL,
#   use included in base image file GUNICORN_CONF and /app/prestart.sh
ENV PORT=5000

# to build image from this directory run:
# docker build -t flask_rest_srv_image ./
# then:
# docker run -d -p 80:80 -e flask_rest_srv_image