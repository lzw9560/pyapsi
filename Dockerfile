FROM homebrew/ubuntu20.04 as builder
#FROM ubuntu:20.04 as builder

RUN brew install cppzmq zeromq
RUN brew install flatbuffers \
	&& sudo ln -sf /home/linuxbrew/.linuxbrew/bin/flatc /usr/local/bin/flatc

USER root
RUN apt-get update && apt-get -y install cmake libtclap-dev libjsoncpp-dev libzmq3-dev \
	&& apt install -y software-properties-common \
	&& apt install -y python3 python3-distutils python3-dev python3-pip \
	&& rm -rf /var/lib/apt/lists/*

RUN python3 --version

RUN git clone https://github.com/log4cplus/log4cplus.git --recursive \
	&& cd log4cplus \
	&& mkdir build-cmake \
	&& cd build-cmake \
	&& cmake .. \
	&& make -j 4 \
	&& make install 

ADD . /app
WORKDIR /app/src

RUN mkdir build && cd build \
	&& cmake .. \
	&& make all -j

ARG TARGET_PATH=/app/src/build/lib

WORKDIR /app

RUN python3 -m pip install --upgrade pip \
	&& python3 -m pip install -r requirements.txt \
	&& python3 setup.py install 

# RUN python3 -m pip install tqdm	
# RUN python3 -c "from distutils import sysconfig"
RUN python -c "import pyapsi; print(pyapsi.__doc__)"
CMD ["/bin/bash"]
