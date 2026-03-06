#!/bin/bash
# Loads GEMINI_API_KEY from project's .env.local, then starts mcp-image.
# Falls back to already-set environment variable if .env.local is absent.

for envfile in .env.local .env; do
  if [ -f "$envfile" ]; then
    while IFS='=' read -r key value; do
      case "$key" in
        GEMINI_API_KEY|IMAGE_OUTPUT_DIR|IMAGE_QUALITY|SKIP_PROMPT_ENHANCEMENT)
          value="${value#\"}" ; value="${value%\"}"
          value="${value#\'}" ; value="${value%\'}"
          export "$key=$value"
          ;;
      esac
    done < <(grep -v '^\s*#' "$envfile" | grep -v '^\s*$')
    break
  fi
done

if [ -z "$GEMINI_API_KEY" ]; then
  echo "Error: GEMINI_API_KEY not found in .env.local, .env, or environment" >&2
  exit 1
fi

exec npx -y mcp-image
