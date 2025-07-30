#!/usr/bin/env bash

WORKDIR=$(cd $(dirname $(dirname $0)) && pwd)

docker run --rm -v "${WORKDIR}:/local" -w "/local" \
  openapitools/openapi-generator-cli \
  author \
  template \
  -g python-pydantic-v1 \
  -o /local/template/
