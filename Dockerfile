FROM python:3.9-bullseye AS prod
LABEL maintainer="Joshua Thorpe"
ARG VERSION
LABEL version="$VERSION"
RUN apt-get update \
  && apt-get install -yq \
    git \
    curl \
    sudo \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN apt-get update \
  && apt-get install -yq rpi.gpio || pip install --no-cache-dir RPi.GPIO \
  ; apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /root/smart-gate
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && export READTHEDOCS=True \
    && pip install --no-cache-dir -e  . \
    && rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info
RUN bash arduino_src/install_and_configure_arduino-cli.sh

LABEL git-commit="$(git rev-parse HEAD )"

# Allow arduino upload script to be used as alternative entrypoint
RUN chmod o+x arduino_src/upload.sh
CMD ["python3", "rpi_src/main.py"]

FROM prod AS dev
RUN pip install --no-cache-dir -e .[dev] \
    && rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info
