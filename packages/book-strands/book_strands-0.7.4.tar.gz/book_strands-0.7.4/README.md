# Book Strands

[![Current version](https://badge.fury.io/py/book-strands.svg)](https://badge.fury.io/py/book-strands)
[![Downloads](https://pepy.tech/badge/book-strands/month)](https://pepy.tech/project/book-strands)

[![Build status](https://github.com/justin8/book-strands/actions/workflows/build-test.yml/badge.svg)](https://github.com/justin8/book-strands/actions/workflows/build-test.yml)
[![codecov](https://codecov.io/gh/justin8/book-strands/branch/master/graph/badge.svg)](https://codecov.io/gh/justin8/book-strands)

A powerful CLI tool for managing e-book metadata and organizing your digital library.

## Overview

Book Strands is designed to help you manage your e-book collection by providing tools to read, modify, and organize e-book metadata. It supports popular e-book formats and can automatically organize your files based on author, series, and other metadata.

## Features

- **Read metadata** from e-books including title, author, series info, and ISBN
- **Write/modify metadata** in your e-books
- **Organize your library** by automatically renaming and moving files based on customizable patterns
- **Support for multiple formats**: EPUB, MOBI, AZW and AZW3
- **Intelligent processing** using AI-powered tools to manage your collection

## Installation

```bash
# Install from PyPI
pip install book-strands
```

## Requirements

- Python 3.12 or higher
- [Calibre](https://calibre-ebook.com/) installed

## Usage

```bash
book-strands run /path/to/your/ebooks /path/to/organized/library \
  --output-format "{{author}}/{{series}}/{{title}}.{{extension}}"
```

Output format can be described in plain language as it is an interpreted format.

You can also import and organize existing e-book files:

```bash
book-strands import-local-books /path/to/existing/books /path/to/organized/library
```

## Configuration

Book Strands uses a configuration file located at `~/.config/book-strands.conf`. Here's an example configuration:

```ini
[zlib-logins]
user1@example.com = password1
user2@example.com = password2
```

The `zlib-logins` section contains email and password pairs for Z-Library accounts used for downloading books.

## Local LLMs

You can also use any local (or remote) Ollama-hosted LLM by setting `--ollama` and configuring it with the below parameters:

```bash
--ollama-model TEXT   Ollama model to use  [default: qwen3:8b]
--ollama-url TEXT     Ollama server URL  [default: http://localhost:11434]
```

## Development

To enable tracing of agent requests, start a Jaeger instance and set the below environment variable, then access Jaeger on <http://localhost:16686>

```
docker run -d --name jaeger \
  -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 14250:14250 \
  -p 14268:14268 \
  -p 14269:14269 \
  -p 9411:9411 \
  jaegertracing/all-in-one:latest

export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
