import hashlib
import importlib.util
import logging
import os
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from typing import Any, TypeVar

import yaml


class MisconfigurationError(Exception):
    pass


KeyType = TypeVar("KeyType")


def deep_update(
    mapping: dict[KeyType, Any],
    *updating_mappings: dict[KeyType, Any],
    skip_nones: bool = False,
) -> dict[KeyType, Any]:
    """Deep update a mapping with other mappings.

    If `skip_nones` is True, then the values that are None in the updating mappings are
    not updated.
    """
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if (
                k in updated_mapping
                and isinstance(updated_mapping[k], dict)
                and isinstance(v, dict)
            ):
                updated_mapping[k] = deep_update(
                    updated_mapping[k], v, skip_nones=skip_nones
                )
            else:
                if skip_nones and v is None:
                    continue
                updated_mapping[k] = v
    return updated_mapping


def dotlist_to_dict(dotlist: list[str]) -> dict:
    """Resolve dot-list style key-value pairs with YAML.

    Helper for overriding configuration values using command-line arguments in dot-list style.
    """
    dotlist_dict = {}
    for override in dotlist:
        parts = override.strip().split("=", 1)
        if len(parts) == 2:
            key = parts[0].strip()
            raw_value = parts[1].strip()

            # If the value starts with a quote but doesn't end with the same quote,
            # it means we have a malformed string. In this case, we'll treat it as a raw string.
            if (raw_value.startswith('"') and not raw_value.endswith('"')) or (
                raw_value.startswith("'") and not raw_value.endswith("'")
            ):
                value = raw_value
            else:
                try:
                    value = yaml.safe_load(raw_value)
                except yaml.YAMLError:
                    # If YAML parsing fails, treat it as a raw string
                    value = raw_value

            keys = key.split(".")
            temp = dotlist_dict
            for k in keys[:-1]:
                temp = temp.setdefault(k, {})
            temp[keys[-1]] = value
    return dotlist_dict


def is_package_installed(package_name: str) -> bool:
    return importlib.util.find_spec(package_name) is not None


def run_command(command, cwd=None, verbose=False):
    if verbose:
        print(f"Running command: {command}")
        if cwd:
            print(f"Current working directory set to: {cwd}")

    with tempfile.TemporaryDirectory() as tmpdirname:
        if verbose:
            print(f"Temporary directory created at: {tmpdirname}")

        file = os.path.join(
            tmpdirname, hashlib.sha1(command.encode("utf-8")).hexdigest() + ".sh"
        )
        if verbose:
            print(f"Script file created: {file}")

        with open(file, "w") as f:
            f.write(command)
            f.flush()
            if verbose:
                print("Command written to script file.")

        master, slave = os.openpty()
        process = subprocess.Popen(
            f"bash {file}",
            stdout=slave,
            stderr=slave,
            stdin=subprocess.PIPE,
            cwd=cwd,
            shell=True,
            executable="/bin/bash",
        )

        if verbose:
            print("Subprocess started.")

        os.close(slave)

        while True:
            try:
                output = os.read(master, 1024)
                if not output:
                    break
                print(output.decode(errors="ignore"), end="", flush=True)
            except OSError as e:
                if e.errno == 5:  # Input/output error is expected at the end of output
                    break
                raise

        if verbose:
            print("Output reading completed.")

        rc = process.wait()

        if verbose:
            print(f"Subprocess finished with return code: {rc}")

        return rc


def get_token_usage_from_cache_db(cache_db_path: str | Path) -> dict:
    """Extract token usage metrics from the cache database.

    Args:
        cache_db_path: Path to the SQLite cache database file

    Returns:
        Dictionary containing token usage metrics:
        {
            "total_tokens": int,
            "prompt_tokens": int,
            "completion_tokens": int,
            "total_cached_requests": int
        }
        Returns empty dict if no data found or error occurs.
    """
    try:
        with sqlite3.connect(cache_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    SUM(json_extract(value, '$.usage.total_tokens')) as total_tokens,
                    SUM(json_extract(value, '$.usage.prompt_tokens')) as prompt_tokens,
                    SUM(json_extract(value, '$.usage.completion_tokens')) as completion_tokens,
                    COUNT(*) as total_requests
                FROM cache
                WHERE json_extract(value, '$.usage') IS NOT NULL
            """
            )
            row = cursor.fetchone()

            if row and row[0] is not None:  # Check if we got any results
                return {
                    "total_tokens": row[0],
                    "prompt_tokens": row[1],
                    "completion_tokens": row[2],
                    "total_cached_requests": row[3],
                }
    except Exception as e:
        logging.warning(f"Failed to read token usage from cache: {e}")

    return {}
