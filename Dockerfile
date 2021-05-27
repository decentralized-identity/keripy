FROM python:3.9

WORKDIR /src
COPY ./ /src

RUN apt update -qq && \
    apt install -y libsodium23 && \
    pip3 install -r requirements.txt

ENTRYPOINT ["kli"]
