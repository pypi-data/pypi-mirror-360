#!/usr/bin/env python
"""
DaggerML Demo Script

This unified script handles:
1. Setting up a moto server for AWS service mocking
2. Creating sample DAGs using the mock services
3. Running a UI server to view the DAGs
4. Gracefully handling exit and cleanup

Usage:
  python dev/demo.py             # Run everything and wait for Ctrl+C to exit
  python dev/demo.py --debug     # Run moto and create DAGs only, then exit
"""

import argparse
import logging
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import boto3
from daggerml import Dml
from dml_util import S3Store, funkify

# Set up basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("daggerml_demo")

# Default directory structure and constants
SCRIPT_DIR = Path(__file__).parent.absolute()
ROOT_DIR = SCRIPT_DIR / "root"
CACHE_DIR = ROOT_DIR / "cache"
CONFIG_DIR = ROOT_DIR / "config"
PROJECT_DIR = ROOT_DIR / "project"
S3_BUCKET = "daggerml-demo-bucket"
S3_PREFIX = "demo/data"
LOG_GROUP = "dml"


class MotoServer:
    """Manages a moto server for AWS service mocking"""

    def __init__(self):
        self.server = None
        self.moto_endpoint = None
        self.aws_env = {}
        self.original_env = {}

    def start(self):
        """Start the moto server and configure environment"""
        # Store original AWS environment variables
        self.original_env = {k: v for k, v in os.environ.items() if k.startswith("AWS_")}

        # Clear out AWS environment variables
        for k in list(os.environ.keys()):
            if k.startswith("AWS_"):
                del os.environ[k]
        # import moto here because moto will read AWS_* envvars
        from moto.server import ThreadedMotoServer

        region = "us-east-1"
        self.server = ThreadedMotoServer(port=0)
        self.server.start()
        moto_host, moto_port = self.server._server.server_address
        self.moto_endpoint = f"http://{moto_host}:{moto_port}"

        # Set AWS environment for moto
        self.aws_env = {
            "AWS_ACCESS_KEY_ID": "test_access_key",
            "AWS_SECRET_ACCESS_KEY": "test_secret_key",
            "AWS_REGION": region,
            "AWS_DEFAULT_REGION": region,
            "AWS_ENDPOINT_URL": self.moto_endpoint,
        }
        for k, v in self.aws_env.items():
            os.environ[k] = v
        logger.info("Moto server started on %s", self.moto_endpoint)

    def setup_resources(self):
        """Create required AWS resources in moto"""
        # Create S3 bucket
        s3_client = boto3.client("s3", endpoint_url=self.moto_endpoint)
        s3_client.create_bucket(Bucket=S3_BUCKET)
        os.environ["DML_S3_BUCKET"] = S3_BUCKET
        os.environ["DML_S3_PREFIX"] = S3_PREFIX
        logger.info("Created S3 bucket: %s", S3_BUCKET)

        # Create CloudWatch log group
        logs_client = boto3.client("logs", endpoint_url=self.moto_endpoint)
        logs_client.create_log_group(logGroupName=LOG_GROUP)
        logger.info("Created CloudWatch log group: %s", LOG_GROUP)

    def stop(self):
        """Stop the moto server and restore environment"""
        if self.server:
            # Cleanup resources
            try:
                s3 = S3Store(bucket=S3_BUCKET, prefix=S3_PREFIX)
                s3.rm(*s3.ls(recursive=True))
                boto3.client("logs", endpoint_url=self.moto_endpoint).delete_log_group(logGroupName=LOG_GROUP)
            except Exception as e:
                logger.warning("Error during AWS resource cleanup: %s", e)

            # Stop server
            logger.info("Stopping moto server...")
            self.server.stop()
            self.server = None

            # Restore original environment
            for k in list(os.environ.keys()):
                if k.startswith("AWS_"):
                    del os.environ[k]

            for k, v in self.original_env.items():
                os.environ[k] = v

            logger.info("Moto server stopped and environment restored")


# Example 1: Simple Function DAG
@funkify
def add_numbers(dag):
    """Simple function that adds numbers together"""
    import sys

    print("Adding numbers:", dag.argv[1:].value())
    print("Debug information to stderr", file=sys.stderr)
    dag.result = sum(dag.argv[1:].value())
    return dag.result


# Example 2: Function with calculations and logging
@funkify
def calculate_statistics(dag):
    """Calculate basic statistics on a list of numbers"""
    import sys
    from statistics import mean, median, stdev

    numbers = dag.argv[1].value()
    print(f"Calculating statistics for {len(numbers)} values", file=sys.stderr)

    if not numbers:
        print("ERROR: Empty input list", file=sys.stderr)
        raise RuntimeError("Cannot calculate statistics on an empty list")

    dag.count = len(numbers)
    dag.sum = sum(numbers)
    dag.mean = mean(numbers)
    dag.median = median(numbers)

    try:
        dag.stdev = stdev(numbers)
    except:
        print("WARNING: Could not calculate standard deviation", file=sys.stderr)
        dag.stdev = None

    # Create a results dictionary
    dag.results = {
        "count": dag.count,
        "sum": dag.sum,
        "mean": dag.mean,
        "median": dag.median,
        "stdev": dag.stdev,
    }

    print(f"Results computed: {dag.results}")
    dag.result = dag.results
    return dag.result


# Example 3: Multi-step process demonstrating subdag execution
@funkify
def process_data(dag):
    """Process data through multiple steps"""
    import sys

    # Extract data and function reference
    data = dag.argv[1].value()
    stats_function = dag.argv[2]

    print(f"Processing {len(data)} data points", file=sys.stderr)

    # First transform the data
    dag.transformed = [x * 2 for x in data]
    print(f"Transformed data: {dag.transformed}")

    # Then run statistics on both original and transformed
    dag.original_stats = stats_function(data)
    dag.transformed_stats = stats_function(dag.transformed)

    # Final output is a comparison
    dag.comparison = {
        "original": dag.original_stats.value(),
        "transformed": dag.transformed_stats.value(),
        "scale_factor": 2,
    }

    dag.result = dag.comparison
    return dag.result


def clean_root_dir():
    """Clean out the root directory and create necessary subdirectories"""
    # Clean out root directory if it exists
    if ROOT_DIR.exists():
        logger.info("Cleaning existing root directory: %s", ROOT_DIR)
        shutil.rmtree(ROOT_DIR)

    # Create directories
    logger.info("Creating directory structure in %s", ROOT_DIR)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)


def create_sample_dags():
    """Create sample DAGs with different functions and data flows"""
    # Ensure environment and directories are prepared
    os.environ["DML_DEBUG"] = "1"

    # Clean and prepare directories
    clean_root_dir()
    logger.info(
        "Using directory structure: %s (cache), %s (config), %s (project)",
        CACHE_DIR,
        CONFIG_DIR,
        PROJECT_DIR,
    )

    # Create a DML instance for our demo with our directory structure
    dml = Dml(
        cache_path=str(CACHE_DIR),
        config_dir=str(CONFIG_DIR),
        project_dir=str(PROJECT_DIR),
    )
    dml("config", "user", "demo_user")
    dml("repo", "create", "demo")
    dml("config", "repo", "demo")
    dml("config", "branch", "main")
    logger.info("Creating sample DAGs...")

    # Example 1: Simple Addition DAG
    with dml.new("simple_addition", "Basic addition example") as dag:
        logger.info("Creating simple addition DAG")
        dag.add_fn = add_numbers

        # Create several nodes with different arguments
        dag.small_sum = dag.add_fn(1, 2, 3)
        dag.large_sum = dag.add_fn(10, 20, 30, 40, 50)
        dag.mixed_sum = dag.add_fn(5, 10.5, -3, 7.25)

        # Set the result node
        dag.result = dag.large_sum

    # Example 2: Statistics Calculation
    with dml.new("statistics", "Statistical calculations on datasets") as dag:
        logger.info("Creating statistics calculation DAG")
        dag.stats_fn = calculate_statistics

        # Create datasets
        dag.small_dataset = [1, 2, 3, 4, 5]
        dag.large_dataset = list(range(100))
        dag.edge_case = [42]  # Single value

        # Calculate statistics on datasets
        dag.small_stats = dag.stats_fn(dag.small_dataset)
        dag.large_stats = dag.stats_fn(dag.large_dataset)
        dag.edge_stats = dag.stats_fn(dag.edge_case)

        # Set the result to the small dataset statistics
        dag.result = dag.small_stats

    # Example 3: Multi-step Processing
    with dml.new("data_processing", "Multi-step data processing pipeline") as dag:
        logger.info("Creating data processing pipeline DAG")
        dag.process_fn = process_data
        dag.stats_fn = calculate_statistics

        # Define datasets
        dag.dataset1 = [10, 20, 30, 40, 50]
        dag.dataset2 = [5, 15, 25, 35, 45]

        # Process the datasets
        dag.process1 = dag.process_fn(dag.dataset1, dag.stats_fn)
        dag.process2 = dag.process_fn(dag.dataset2, dag.stats_fn)

        # Combine results
        dag.combined = {
            "dataset1": dag.process1.value(),
            "dataset2": dag.process2.value(),
        }

        # Set final result
        dag.result = dag.combined

        created_dags = [x["name"] for x in dml("dag", "list")]
        logger.info("Sample DAGs created successfully: %s", created_dags)

    return created_dags


def run_ui_server(port=5000):
    """Run the UI server with the demo DAGs"""

    # Check if directories exist
    if not CACHE_DIR.exists() or not CONFIG_DIR.exists() or not PROJECT_DIR.exists():
        logger.error("Required directory structure not found. Cannot start UI server.")
        return False

    logger.info(
        "Starting UI server with directory structure: %s (cache), %s (config), %s (project)",
        CACHE_DIR,
        CONFIG_DIR,
        PROJECT_DIR,
    )

    # Initialize DML instance with our directory structure
    dml = Dml(
        cache_path=str(CACHE_DIR),
        config_dir=str(CONFIG_DIR),
        project_dir=str(PROJECT_DIR),
    )

    # Create and run the Flask app
    with patch.dict(os.environ, {f"DML_{k.upper()}": v for k, v in dml.kwargs.items()}):
        logger.info("UI server starting on http://127.0.0.1:%d", port)
        logger.info("Press Ctrl+C to exit")
        subprocess.run(["dml-ui-dev", "--port", str(port), "--debug"], check=True)
    return True


def main(debug_only=False):
    """Main function that ties everything together"""
    moto = MotoServer()

    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal, shutting down...")
        moto.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start moto server and set up AWS resources
        moto.start()
        moto.setup_resources()

        # Create sample DAGs
        dags = create_sample_dags()
        logger.info("Created %d DAGs", len(dags))

        # If debug mode, exit now
        if debug_only:
            logger.info("Debug mode: Exiting after DAG creation")
            return

        # Run UI server (blocks until Ctrl+C)
        run_ui_server()

    except Exception as e:
        logger.exception("Error in demo: %s", e)
    finally:
        # Always clean up
        moto.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run DaggerML demo with moto server")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode: only start moto and create DAGs, then exit",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=5000,
        help="Port for the UI server (default: 5000)",
    )
    args = parser.parse_args()

    main(debug_only=args.debug)
