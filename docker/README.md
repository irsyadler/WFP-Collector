# WFP-Collector: Docker
To enable WFP-Collector in containerized deployment, we provide Dockerfile to build Docker image and run Docker container. The Dockerfile will: 
* Run the command to install the necessary applications.
* Create a new non-root user (with sudo capability) using `docker` as both name and password.
* Copy the WFP-Collector files and folders into the container.
* Change the copied items' ownership to the `docker` user.


**NOTE:** Executing Docker-related command must be done in the repository's root directory (`WFP-Collector/`). It is because the Dockerfile is located in this repository's sub-directory. If the command is executed in the same folder as Dockerfile, the necessary WFP-Collector files and directory will not be copied into the built image. Hence, all commands in this documentation should be executed in the repository's root directory (`WFP-Collector/`).

## Directory Structure
* [Dockerfile](Dockerfile) – Instruction to build a docker image for WFP-Collector deployment.
* [Dockerfile.dockerignore](Dockerfile.dockerignore) – List of paths that should be ignored during Docker image building.
* [README.md](README.md) – This Docker documentation.



## Create Docker Image for WFP-Collector 
To build a Docker image, execute the following command:
```
bash run docker build
```
The above command is a shortcut to the corresponding command:
```
docker build --tag wfp-collector:0.5.2 --file docker/Dockerfile .
```
A Docker image named `wfp-collector` with tag `0.5.2` will be created.


## Run Docker Container for WFP-Collector 
To run a Docker container, execute the following command:
```
bash run docker container
```
The above command is a shortcut to the corresponding command:
```
docker run --detach --tty --interactive --cap-add=NET_ADMIN --security-opt="seccomp=unconfined" --name wfp-collector-0.5.2 wfp-collector:0.5.2
```
A Docker container named `wfp-collector-0.5.2` will be started. The `--cap-add=NET_ADMIN` and `--security-opt="seccomp=unconfined"` arguments is to allow the WFP-Collector to capture network packets from a network interface.