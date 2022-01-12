FROM ubuntu:20.04
RUN mkdir /app
WORKDIR /app
COPY . /app

#
RUN apt-get update && \
    apt-get install -y \
    wget \
    curl \
    rsyslog \
    python3-pip \
    rustc \
    git \
    vim

# install gdown
RUN pip3 uninstall -y  enum34
RUN pip3 install gdown

#
RUN pip3 install -r requirements.txt
RUN python3 -c"import stanza;stanza.download('en')"
RUN python3 server.py

#
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt install -y nodejs
RUN cd react&&npm install&&npm run build

EXPOSE 8000
CMD sh -c "uvicorn server:app --host 0.0.0.0 --port 8000 || bash"