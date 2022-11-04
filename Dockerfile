FROM python:3.9-bullseye AS prod
LABEL maintainer="Joshua Thorpe"
ARG VERSION
LABEL version="$VERSION"
ENV SMART_GATE_VERSION="$VERSION"
ENV SMART_GATE_CONTAINER="TRUE"

# Try install rpi.io via apt (arm) or pip (x86)
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

# Allow arduino upload script to be used as alternative entrypoint
RUN chmod o+x arduino_src/upload.sh
CMD ["python3", "rpi_src/main.py"]

FROM prod AS dev
RUN pip install --no-cache-dir -e .[dev] \
    && rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info
