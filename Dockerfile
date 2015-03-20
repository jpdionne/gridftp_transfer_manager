FROM ipython/ipython:latest


ADD . /tmp/build/
WORKDIR /tmp/build
RUN apt-get update && apt-get -y -q install myproxy swig daemon
RUN python setup.py install
RUN mkdir -p /root/.local/share/

