FROM bitnami/minideb:latest

ARG CUDA_VERSION=12.4.1
ARG CUDA_PACKAGE_VERSION=12.4.1-1

RUN install_packages python3 python3-pip python3-venv 
# RUN install_packages git wget software-properties-common
# RUN wget https://developer.download.nvidia.com/compute/cuda/12.4.1/local_installers/cuda-repo-debian12-12-4-local_12.4.1-550.54.15-1_amd64.deb
# RUN dpkg -i cuda-repo-debian12-12-4-local_12.4.1-550.54.15-1_amd64.deb
# RUN cp /var/cuda-repo-debian12-12-4-local/cuda-*-keyring.gpg /usr/share/keyrings/
# RUN add-apt-repository contrib && apt-get update 
# RUN install_packages cuda-runtime-12.4
RUN python3 -m venv .venv
ADD runpod_httpx_proxy /runpod_httpx_proxy/runpod_httpx_proxy
ADD pyproject.toml /runpod_httpx_proxy
RUN .venv/bin/python3 -m pip install -e ./runpod_httpx_proxy

COPY examples/worker/handler.py handler.py

CMD [".venv/bin/python3", "handler.py"]
