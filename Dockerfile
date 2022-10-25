FROM python:3.9-bullseye
LABEL maintainer="Joshua Thorpe"
ARG VERSION
LABEL version="$VERSION"
RUN apt-get update \
  && apt-get install -yq \
    git \
    curl \
    sudo \
    rpi.gpio \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /root/smart-gate
COPY . .
# Remove unneeded files for production \
RUN  rm -rf .git .*ignore reference shell_ui Jenkinsfile* deploy.sh rpi_src/test* tox.ini build_docker.sh run-smart-gate

# Install dependencies
RUN pip install --upgrade pip && export READTHEDOCS=True && pip install .
RUN bash arduino_src/install_and_configure_arduino-cli.sh

LABEL git-commit="$(git rev-parse HEAD )"

# Allow arduino upload script to be used as alternative entrypoint
RUN chmod o+x arduino_src/upload.sh
CMD ["python3", "rpi_src/main.py"]
