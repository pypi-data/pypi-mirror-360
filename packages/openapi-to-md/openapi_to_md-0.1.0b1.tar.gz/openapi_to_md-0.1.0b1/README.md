# OpenAPI to Markdown Converter

A simple, zero-dependency CLI tool to convert OpenAPI 3.x specifications (JSON or YAML) into a clean, Redoc-style Markdown file.

> this project is inspired by [openapi-markdown](https://github.com/vrerv/openapi-markdown)

## Features

- Converts OpenAPI 3.x JSON or YAML files.
- Generates a single, self-contained Markdown file.
- Creates a human-readable output similar to ReDoc's layout.
- Includes sections for API info, servers, paths (with parameters, request bodies, and responses), and schemas.

## Installation

For direct use as a CLI tool, `pipx` is recommended:
```bash
pipx install openapi-to-markdown
```

Alternatively, you can install it with pip:
```bash
pip install openapi-to-markdown
```

## Usage

The CLI tool uses options for all arguments. You must provide either `--input_file` or `--curl_url` to specify the OpenAPI spec source. The output path is set with `--output_file` (default: `output.md`).

```bash
openapi-to-markdown --input_file <path-to-openapi-spec> [--output_file <output-markdown-file>]
openapi-to-markdown --curl_url <openapi-spec-url> [--output_file <output-markdown-file>]
```

### Examples

**Convert a local JSON file:**
```bash
openapi-to-markdown --input_file my-api.json
```
This command generates `output.md` in the current directory.

**Convert a YAML file and specify the output path:**
```bash
openapi-to-markdown --input_file openapi.yaml --output_file docs/reference.md
```

**Convert a remote OpenAPI spec:**
```bash
openapi-to-markdown --curl_url https://petstore3.swagger.io/api/v3/openapi.json --output_file petstore.md
```

## Filtering Only Specific APIs

You can generate documentation for only specific API paths using the `--filter-paths` option. This option can be used multiple times to include multiple paths. Only the APIs whose paths start with the given values will be included in the output.

**Example:**

```bash
openapi-to-markdown --input_file my-api.json \
  --filter-paths /agent/apps \
  --filter-paths /agent/graph \
  --output_file filtered.md
```

Or with a remote OpenAPI spec:

```bash
openapi-to-markdown --curl_url https://example.com/openapi.json \
  --filter-paths /agent/apps \
  --filter-paths /agent/graph \
  --output_file filtered.md
```

- You can specify as many `--filter-paths` options as needed.
- Only the endpoints whose path starts with any of the given values will be included in the generated Markdown.

## Options

- `--input_file PATH` : Path to the OpenAPI spec file (json/yaml)
- `--curl_url URL` : URL to fetch the OpenAPI spec (json/yaml)
- `--output_file PATH` : Path to the output Markdown file (default: output.md)
- `--templates-dir PATH` : Path to a custom templates directory
- `--filter-paths PATH` : Only document APIs whose path starts with the given value (can be used multiple times)

---

For more options, check the help:
```bash
openapi-to-markdown --help
```
