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
RUN git clone --depth=1 --branch=docker https://github.com/ThorpeJosh/smart-gate.git
WORKDIR /root/smart-gate
RUN rm -rf .git .*ignore reference shell_ui Jenkinsfile* deploy.sh rpi_src/test* tox.ini
# Install python dependencies
RUN pip3 install .
# Install arduino dependencies
RUN bash arduino_src/install_and_configure_arduino-cli.sh 

LABEL git-commit="$(git rev-parse HEAD )"

ENTRYPOINT ["python3", "/root/smart-gate/rpi_src/main.py"]
