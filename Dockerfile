FROM python:3.9 AS base

WORKDIR /src
COPY ./ /src

RUN apt update -qq && \
    apt install -y libsodium23 && \
    pip3 install -r requirements.txt

# kli binary image
FROM base AS kli

ENTRYPOINT ["kli"]

# keri binary image
FROM base AS keri

ENTRYPOINT ["keri"]
