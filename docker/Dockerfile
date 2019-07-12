FROM ruby:2.5

WORKDIR /usr/local/iiif

RUN apt-get update && apt-get install -y imagemagick awscli

RUN gem install --no-user-install --no-document iiif_s3

COPY . .

ENTRYPOINT ["./createiiif.sh"]
