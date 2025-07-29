#!/usr/bin/env sh

# Build the wheel.
uv sync
uv build
uv publish --token $pypi_token
