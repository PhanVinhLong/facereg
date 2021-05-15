  
FROM nvidia/cuda:10.2-cudnn8-devel

RUN mkdir /app
WORKDIR /app

RUN apt update && \
    apt install -y postgresql-client

RUN apt-get install -y apt-utils

RUN apt-get update && \
	apt-get install -y --no-install-recommends ca-certificates curl netbase wget && \
	rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends git mercurial openssh-client subversion procps && \
	rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
	apt-get install -y --no-install-recommends autoconf automake bzip2 dpkg-dev file g++ gcc imagemagick libbz2-dev libc6-dev libcurl4-openssl-dev libdb-dev libevent-dev libffi-dev libgdbm-dev libglib2.0-dev libgmp-dev libjpeg-dev libkrb5-dev liblzma-dev libmagickcore-dev libmagickwand-dev libmaxminddb-dev libncurses5-dev libncursesw5-dev libpng-dev libpq-dev libreadline-dev libsqlite3-dev libssl-dev libtool libwebp-dev libxml2-dev libxslt-dev libyaml-dev make patch unzip xz-utils zlib1g-dev

ENV LANG=C.UTF-8

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
	apt-get install -y --no-install-recommends libbluetooth-dev tk-dev uuid-dev && \
	rm -rf /var/lib/apt/lists/*

RUN apt-get update

ENV GPG_KEY=E3FF2839C048B25C084DEBE9B26995E310250568
ENV PYTHON_VERSION=3.8.7

RUN wget -O python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" && \
	wget -O python.tar.xz.asc "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" && \
	export GNUPGHOME="$(mktemp -d)" && \
	gpg --batch --keyserver ha.pool.sks-keyservers.net --recv-keys "$GPG_KEY" && \
	gpg --batch --verify python.tar.xz.asc python.tar.xz && \
	{ command -v gpgconf > /dev/null && gpgconf --kill all || :; } && \
	rm -rf "$GNUPGHOME" python.tar.xz.asc && mkdir -p /usr/src/python && \
	tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz	&& \
	rm python.tar.xz && \
	cd /usr/src/python && \
	gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)" && \
	./configure --build="$gnuArch" --enable-loadable-sqlite-extensions --enable-optimizations --enable-option-checking=fatal --enable-shared --with-system-expat --with-system-ffi --without-ensurepip && \
	make -j "$(nproc)" && \
	make install && \
	rm -rf /usr/src/python && find /usr/local -depth \( \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) -o \( -type f -a -name 'wininst-*.exe' \) \) -exec rm -rf '{}' + && ldconfig && python3 --version

RUN ln -s idle3 idle && \
	ln -s pydoc3 pydoc && \
	ln -s python3 python && \
	ln -s python3-config python-config

ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV PYTHON_PIP_VERSION=21.0.1
ENV PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/4be3fe44ad9dedc028629ed1497052d65d281b8e/get-pip.py
ENV PYTHON_GET_PIP_SHA256=8006625804f55e1bd99ad4214fd07082fee27a1c35945648a58f9087a714e9d4

RUN wget -O get-pip.py "$PYTHON_GET_PIP_URL" && \
	python3 get-pip.py --disable-pip-version-check --no-cache-dir "pip==$PYTHON_PIP_VERSION" && \
	pip --version && \
	find /usr/local -depth \( \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) -o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \) -exec rm -rf '{}' + && \
	rm -f get-pip.py

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
	apt-get install -y libboost-all-dev

RUN apt-get update && \
	apt-get install -y libatlas-base-dev graphviz

RUN pip install --no-cache-dir mxnet-cu102 graphviz

RUN pip install --no-cache-dir tensorflow-gpu
RUN pip install --upgrade numpy

RUN apt-get update && \
    apt-get install libsm6 libxext6 x264 libx264-dev -y && \
	apt-get install ffmpeg -y

COPY . .