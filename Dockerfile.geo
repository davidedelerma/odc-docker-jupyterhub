FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal


RUN apt-get update && \
 apt-get install -y software-properties-common && \
 add-apt-repository ppa:nextgis/ppa && \
 apt-get update

RUN apt-get install -y --no-install-recommends \
      git \
      curl \
      build-essential \
      python3 \
      python3-dev \
      python3-pip \
      python3-numpy \
      python3-matplotlib

RUN apt-get install -y --no-install-recommends\
      gdal-bin \
      libgdal-dev \
      libgdal20 \
      libudunits2-0

RUN apt-get clean

RUN pip3 install --no-cache pip --upgrade && \
    pip3 install --no-cache wheel setuptools && \
    pip3 install --no-cache --upgrade dateutils

RUN pip3 install --no-cache GDAL fiona shapely && \
    pip3 install --no-cache --upgrade cython && \
    pip3 install --no-cache git+https://github.com/mapbox/rasterio.git@1.0a12

