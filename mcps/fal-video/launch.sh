#!/bin/bash
# Loads FAL_KEY from project's .env.local, then starts fal-image-video-mcp.
# Falls back to already-set environment variable if .env.local is absent.

for envfile in .env.local .env; do
  if [ -f "$envfile" ]; then
    while IFS='=' read -r key value; do
      case "$key" in
        FAL_API_KEY)
          value="${value#\"}" ; value="${value%\"}"
          value="${value#\'}" ; value="${value%\'}"
          export "FAL_KEY=$value"
          ;;
        FAL_KEY)
          value="${value#\"}" ; value="${value%\"}"
          value="${value#\'}" ; value="${value%\'}"
          export "FAL_KEY=$value"
          ;;
      esac
    done < <(grep -v '^\s*#' "$envfile" | grep -v '^\s*$')
    break
  fi
done

if [ -z "$FAL_KEY" ]; then
  echo "Error: FAL_KEY or FAL_API_KEY not found in .env.local, .env, or environment" >&2
  exit 1
fi

# Disable auto-open in headless/CI environments
export AUTOOPEN=false

exec npx -y fal-image-video-mcp
