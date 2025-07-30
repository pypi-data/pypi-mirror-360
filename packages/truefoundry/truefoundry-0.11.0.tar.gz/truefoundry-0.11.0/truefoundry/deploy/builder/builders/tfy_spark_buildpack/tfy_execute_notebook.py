# This script is used as the main application file for spark applications
# when the application to be run is a notebook, the actual notebook to be
# executed is passed as an argument to this script.


import argparse
import os
import sys

import boto3
import nbformat
import papermill as pm
from botocore.client import Config
from nbconvert import HTMLExporter


def convert_notebook_to_html(notebook_path, output_html_path):
    """
    Convert a Jupyter notebook to an HTML file.

    Args:
        notebook_path: Path to the input notebook (.ipynb)
        output_html_path: Path for the output HTML file (.html)
    """
    print(f"Converting notebook {notebook_path} to HTML...")
    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook_content = nbformat.read(f, as_version=4)

        html_exporter = HTMLExporter()
        # Use lab for https://nbconvert.readthedocs.io/en/latest/customizing.html#where-are-nbconvert-templates-installed
        html_exporter.template_name = "lab"
        (body, _) = html_exporter.from_notebook_node(notebook_content)

        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(body)
        print(f"Successfully converted notebook to HTML: {output_html_path}")
    except Exception as e:
        print(f"Error converting notebook to HTML: {e}")
        raise


def upload_file_to_s3(file_path, bucket_name, s3_key):
    print(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}...")
    # Use s3proxy for pushing data to s3
    # The JWT token is already available in the pod
    aws_access_key_id = os.environ.get("SPARK_APPLICATION_EVENT_LOG_JWT_TOKEN")
    aws_secret_access_key = "__token__"
    s3_endpoint_url = os.environ.get("S3_PROXY_URL")

    if not aws_access_key_id:
        raise ValueError(
            "SPARK_APPLICATION_EVENT_LOG_JWT_TOKEN environment variable is not set"
        )
    if not s3_endpoint_url:
        raise ValueError("S3_PROXY_URL environment variable is not set")

    # Needed for the issue https://github.com/gaul/s3proxy/issues/765
    s3_config = Config(
        request_checksum_calculation="when_required",
        response_checksum_validation="when_required",
    )
    try:
        client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=s3_endpoint_url,
            config=s3_config,
        )

        with open(file_path, "rb") as data:
            client.put_object(Bucket=bucket_name, Key=s3_key, Body=data)
        print(f"Successfully uploaded {file_path} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        raise


def execute_notebook(notebook_path, output_path="/tmp/output.ipynb", parameters=None):
    """
    Execute a Jupyter notebook using papermill.

    Args:
        notebook_path: Path to the input notebook
        output_path: Path for the output notebook
        parameters: Dictionary of parameters to pass to the notebook

    Raises:
        Exception: If notebook execution fails
    """
    if parameters is None:
        parameters = {}

    print(f"Starting execution of notebook: {notebook_path}")
    pm.execute_notebook(
        input_path=notebook_path,
        output_path=output_path,
        parameters=parameters,
        # TODO(gw): Replace with kernel name for venv
        kernel_name="python3",
        # Log cell by cell execution output
        # TODO(gw): Output logs to a file instead, so that they aren't merged with the container's logs
        log_output=True,
        stdout_file=sys.stdout,
        stderr_file=sys.stderr,
    )
    print(f"Successfully executed notebook: {notebook_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Execute a Jupyter notebook using papermill for Spark applications"
    )
    parser.add_argument("notebook_path", help="Path to the notebook file to execute")
    args = parser.parse_args()

    output_notebook_path = "/tmp/output.ipynb"

    # This would be the same as the default bucket used by servicefoundry-server
    s3_bucket = os.environ.get("TFY_NOTEBOOK_OUTPUT_S3_BUCKET")
    # This would be something like sparkjob-events/<tenant-id>
    s3_key_prefix = os.environ.get("TFY_NOTEBOOK_OUTPUT_S3_KEY_PREFIX")

    try:
        executed_notebook_path = execute_notebook(
            args.notebook_path, output_path=output_notebook_path
        )

        # The following may also be modeled as an entrypoint
        # https://papermill.readthedocs.io/en/latest/extending-entry-points.html
        # Will take that up with next iteration where we save the executed notebook periodically
        if s3_bucket and s3_key_prefix:
            print("Converting notebook to HTML and uploading to S3...")
            html_output_path = "/tmp/output.html"
            convert_notebook_to_html(
                notebook_path=executed_notebook_path, output_html_path=html_output_path
            )

            # Construct S3 key: use the original notebook name for the HTML file
            notebook_name = os.path.basename(args.notebook_path)
            s3_html_key = f"{s3_key_prefix}/output.html"
            upload_file_to_s3(
                file_path=html_output_path, bucket_name=s3_bucket, s3_key=s3_html_key
            )
            print(f"Successfully uploaded HTML to s3://{s3_bucket}/{s3_html_key}")

    except Exception as e:
        print(f"Error executing notebook {args.notebook_path}: {e}")
        print(
            "Exiting with status code 1 to signal failure to parent process/orchestrator"
        )
        sys.exit(1)
