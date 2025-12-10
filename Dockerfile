# Use CUDA 12.8 base image with build tools (devel)
FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    TORCH_CUDA_ARCH_LIST="7.5;8.0;8.6;8.9;9.0" \
    MAX_JOBS=8

# Set working directory
WORKDIR /

# Install Python 3.11 and build tools
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-dev python3-pip python3.11-venv \
    build-essential git ninja-build cmake curl \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Upgrade pip/setuptools/wheel
RUN python3 -m pip install --upgrade pip setuptools wheel packaging

# Install PyTorch 2.7.0 with CUDA 12.8 wheels
RUN pip install --index-url https://download.pytorch.org/whl/cu128 \
    torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0

# Install project requirements (excluding torch stack)
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

# Install flash-attn (build from source against CUDA 12.8 + PyTorch 2.7)
RUN pip install --no-build-isolation flash-attn

# Install triton (matching wheel for Linux)
RUN pip install triton

# Copy handler script
COPY handler.py /handler.py

# Start the container
CMD ["python3", "-u", "handler.py"]
