# Use Ubuntu 22.04 LTS as based image
FROM ubuntu:22.04

# Metadata
LABEL author="M. A. Irsyad M. Aminuddin <contact@irsyadler.com>"

# Install sudo for setup usage
RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install sudo

# Add non-root user "docker" with password "docker"
RUN useradd --create-home --user-group --shell /bin/bash docker && echo "docker:docker" | chpasswd && usermod -a -G sudo docker

# Set non-root user
USER docker

# Set working directory
WORKDIR /WFP-Collector

# Copy project file
COPY --chown=docker:docker . .
