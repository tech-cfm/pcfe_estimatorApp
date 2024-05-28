FROM ubuntu:latest
LABEL authors="kasan"

ENTRYPOINT ["top", "-b"]