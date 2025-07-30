#!/usr/bin/env bash

WORKDIR=$(cd $(dirname $(dirname $0)) && pwd)

SCHEMA=${1:-"https://stage.haplohub.com/api/v1/openapi.json"}

docker run --rm -v "${WORKDIR}:/local" -w "/local" \
  openapitools/openapi-generator-cli generate \
  -i "$SCHEMA" \
  -g python-pydantic-v1 \
  --package-name haplohub \
  --invoker-package haplohub \
  --template-dir /local/template \
  --auth apikey
