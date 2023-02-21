
ARG workdir=Weather-reminder
ARG user=wr

# build stage
FROM python:3.10-slim as builder

ARG workdir
ARG user

WORKDIR /$workdir

ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && \
    apt-get -y --no-install-recommends install curl gcc libc-dev libpq-dev

# get and build packages
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /$workdir/wheels -r requirements.txt


# final stage
FROM python:3.10-slim

ARG workdir
ARG user

RUN adduser --disabled-password --gecos '' --no-create-home --shell /bin/false $user

WORKDIR /$workdir

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl

COPY --from=builder /$workdir/wheels /wheels
COPY --from=builder /$workdir/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY --chown=$user:$user . .

RUN chmod +x start.sh

EXPOSE 80

USER $user

CMD ./start.sh
