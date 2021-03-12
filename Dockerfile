FROM debian:buster-slim
LABEL maintainer="Joshua Thorpe"
ARG VERSION
LABEL version="$VERSION"
RUN apt-get update \
  && apt-get install -yq \
    git \
    curl \
    sudo \
    python3 \
    python3-pip \
    python3-serial \
    python3-setuptools \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /root
RUN git clone --depth=1 --branch=docker https://github.com/ThorpeJosh/smart-gate.git \
  && cd smart-gate \
  # Remove unneeded files for production \
  rm -rf .git .*ignore reference shell_ui Jenkinsfile* deploy.sh rpi_src/test* tox.ini build_docker.sh run-smart-gate

# Install dependencies
WORKDIR /root/smart-gate
RUN pip3 install .
RUN bash arduino_src/install_and_configure_arduino-cli.sh

LABEL git-commit="$(git rev-parse HEAD )"

# Allow arduino upload script to be used as alternative entrypoint
RUN chmod o+x arduino_src/upload.sh
ENTRYPOINT ["python3", "rpi_src/main.py"]
