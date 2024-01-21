FROM python:3.11

ARG USERNAME=app
ARG ROOTDIR=/opt/app

WORKDIR ${ROOTDIR}

RUN groupadd -r ${USERNAME} && \
    useradd -d ${ROOTDIR} -r -g ${USERNAME} ${USERNAME} && \
    mkdir ${ROOTDIR}/.local && \
    mkdir ${ROOTDIR}/logs && \
    chown ${USERNAME}:${USERNAME} -R ${ROOTDIR}


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

ENV PATH ${ROOTDIR}/.local/bin:$PATH

COPY requirements.txt requirements.txt

USER ${USERNAME}

RUN pip install --upgrade pip --no-cache-dir --no-python-version-warning && \
    pip install -r requirements.txt --no-cache-dir

USER 0

COPY alembic ${ROOTDIR}/alembic
COPY api ${ROOTDIR}/api
COPY cli ${ROOTDIR}/cli
COPY core ${ROOTDIR}/core
COPY db ${ROOTDIR}/db
COPY models ${ROOTDIR}/models
COPY schemas ${ROOTDIR}/schemas
COPY services ${ROOTDIR}/services
COPY utils ${ROOTDIR}/utils
COPY main.py ${ROOTDIR}/
COPY alembic.ini ${ROOTDIR}/
COPY gunicorn.conf.py ${ROOTDIR}/
COPY start_auth.sh ${ROOTDIR}/

USER ${USERNAME}

EXPOSE 8000

ENTRYPOINT ["sh", "start_auth.sh"]