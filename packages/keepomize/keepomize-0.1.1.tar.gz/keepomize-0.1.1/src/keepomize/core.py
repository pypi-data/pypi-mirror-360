"""
Core functionality for resolving Keeper URIs in Kubernetes Secret manifests.
"""

import base64
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, Optional, Pattern

# Pattern to match Keeper URIs using Keeper notation
# Matches keeper://<title_or_uid>/<selector>/<parameters>[[predicates]]
# Allows for spaces, special characters, and escaped characters in titles
KEEPER_URI_PATTERN: Pattern[str] = re.compile(r"^keeper://(.+)$")


def resolve_keeper_uri(uri: str) -> str:
    """
    Resolve a Keeper URI using ksm secret notation command.

    Args:
        uri: A Keeper URI using Keeper notation, such as:
             - "keeper://MySQL Database/field/password"
             - "keeper://API Keys/field/api_key"
             - "keeper://Contact/field/name[first]"
             - "keeper://Record/custom_field/phone[1][number]"

    Returns:
        The resolved secret value

    Raises:
        subprocess.CalledProcessError: If ksm fails to resolve the URI
        FileNotFoundError: If ksm command is not found
    """
    # Find the full path to ksm
    ksm_path: Optional[str] = shutil.which("ksm")
    if not ksm_path:
        raise FileNotFoundError("ksm command not found in PATH")

    # Use ksm secret notation command to resolve the URI directly
    cmd = [ksm_path, "secret", "notation", uri]

    # Pass through KSM_* environment variables
    env: Dict[str, str] = {}
    for key, value in os.environ.items():
        if key.startswith("KSM_"):
            env[key] = value

    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            cmd, env=env, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to resolve Keeper URI '{uri}'", file=sys.stderr)
        print(f"ksm stderr: {e.stderr}", file=sys.stderr)
        raise


def process_secret(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a Kubernetes Secret document, resolving any Keeper URIs.

    Args:
        doc: A dict representing a Kubernetes Secret

    Returns:
        The modified document
    """
    # Process stringData if present
    if "stringData" in doc:
        for key, value in doc["stringData"].items():
            if isinstance(value, str) and KEEPER_URI_PATTERN.match(value):
                resolved = resolve_keeper_uri(value)
                doc["stringData"][key] = resolved
                # print(f"Resolved keeper URI in stringData.{key}", file=sys.stderr)

    # Process data if present (base64 encoded values)
    if "data" in doc:
        for key, value in doc["data"].items():
            if isinstance(value, str) and KEEPER_URI_PATTERN.match(value):
                # The value is a cleartext Keeper URI that needs to be resolved
                # and then base64 encoded
                resolved = resolve_keeper_uri(value)
                encoded = base64.b64encode(resolved.encode("utf-8")).decode("ascii")
                doc["data"][key] = encoded
                # print(f"Resolved keeper URI in data.{key} (base64 encoded)", file=sys.stderr)

    return doc
