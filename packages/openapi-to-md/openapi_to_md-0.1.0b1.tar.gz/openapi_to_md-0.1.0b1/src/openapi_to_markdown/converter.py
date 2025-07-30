import json
import pathlib
import click
import yaml
from jinja2 import Environment, FileSystemLoader
import requests

# from openapi_to_markdown.utils import resolve_ref, ref_to_link, to_json, ref_to_schema


def to_json(value):
    return json.dumps(value, indent=2)


def ref_to_link(ref):
    if not ref:
        return ""
    if ref.get("$ref"):
        parts = ref["$ref"].split("/")
        schema_name = parts[-1]
        return f"[{schema_name}](#{schema_name.lower()})"
    elif ref.get("type"):
        return f"{ref['type']}"
    return ""


def ref_to_schema(schema, spec_data):
    """Convert a schema reference to actual schema object, recursively resolving all
    nested references while preserving $ref."""
    if isinstance(schema, dict):
        if "$ref" in schema:
            # Get the referenced schema
            ref_path = schema["$ref"].split("/")
            current = spec_data
            for part in ref_path[1:]:  # Skip the first '#' element
                current = current[part]
            # Merge the referenced schema with the original, keeping $ref
            resolved = ref_to_schema(current, spec_data)
            return {**resolved, **schema}
        else:
            # Process all dictionary values recursively
            return {k: ref_to_schema(v, spec_data) for k, v in schema.items()}
    elif isinstance(schema, list):
        # Process all list items recursively
        return [ref_to_schema(item, spec_data) for item in schema]
    return schema


def resolve_ref(spec, ref):
    parts = ref.split("/")
    if parts[0] == "#":
        current = spec
        for part in parts[1:]:
            current = current.get(part)
            if current is None:
                return None
        return current
    return None


def load_openapi_json_file(input_file: pathlib.Path):
    input_file = pathlib.Path(input_file)
    # Load OpenAPI spec
    with open(input_file) as f:
        if input_file.suffix in (".yaml", ".yml"):
            spec = yaml.safe_load(f)
        else:
            spec = json.load(f)
    return spec


def fetch_openapi_spec(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


@click.command()
@click.option(
    "--input_file",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
    help="The path to the OpenAPI specification file",
)
@click.option(
    "--curl_url",
    type=click.STRING,
    help="URL to fetch OpenAPI spec (json/yaml)",
)
@click.option(
    "--output_file",
    type=click.Path(),
    default="output.md",
    help="The path to the output file",
    required=True,
)
@click.option(
    "--templates-dir",
    "-t",
    "templates_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Custom templates directory path",
)
@click.option(
    "--filter-paths",
    "-f",
    "filter_paths",
    type=click.STRING,
    multiple=True,
    help="Only generate apis that start with the given path, multiple paths are allowed",
)
def to_markdown(input_file, curl_url, output_file, templates_dir, filter_paths):
    """
    Convert an OpenAPI specification to a Redoc-style Markdown file.
    """
    print("filter_paths", filter_paths)
    if not input_file and not curl_url:
        raise click.UsageError("Either --input_file or --curl_url must be provided.")
    if input_file and curl_url:
        raise click.UsageError("Only one of --input_file or --curl_url can be used.")

    # Load OpenAPI spec from file or URL
    if input_file:
        spec = load_openapi_json_file(input_file)
        click.echo(f"Converting {input_file} to {output_file}...")
    elif curl_url:
        click.echo(f"Downloading OpenAPI spec from {curl_url} ...")
        # Download and parse OpenAPI spec from URL
        resp = requests.get(curl_url)
        resp.raise_for_status()
        if curl_url.endswith((".yaml", ".yml")):
            spec = yaml.safe_load(resp.text)
        else:
            try:
                spec = resp.json()
            except Exception:
                spec = yaml.safe_load(resp.text)
        click.echo(f"Converting {curl_url} to {output_file}...")

    if not spec:
        click.echo("Failed to load OpenAPI spec.")
        return

    output_file = pathlib.Path(output_file)

    # Setup Jinja2 environment
    if templates_dir:
        template_dir = pathlib.Path(templates_dir)
    else:
        template_dir = pathlib.Path(__file__).parent / "templates"

    env = Environment(loader=FileSystemLoader(template_dir))
    env.globals["ref_to_schema"] = resolve_ref
    env.filters["ref_to_link"] = ref_to_link
    env.filters["to_json"] = to_json
    env.filters["ref_to_schema"] = ref_to_schema

    template = env.get_template("base.md.jinja")

    # Filter paths
    if filter_paths and spec.get("paths"):
        spec["paths"] = {
            path: details
            for path, details in spec["paths"].items()
            if any(path.startswith(p) for p in filter_paths)
        }

    # Render Markdown
    rendered_md = template.render(spec=spec)

    # Write output file
    with open(output_file, "w") as f:
        f.write(rendered_md)

    click.echo("Conversion complete.")


if __name__ == "__main__":
    to_markdown()
