"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import tarfile
import os
import json
import base64
import click

from qalita.internal.logger import init_logging

logger = init_logging()


def get_version():
    return "2.1.3"


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def ask_confirmation(message):
    """This function just asks for confirmation interactively from the user"""
    return click.confirm(message, default=False)


def validate_token(token: str):
    try:
        # Step 1: Split the token
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        # Step 2: Decode base64 (adding padding if necessary)
        payload_encoded = parts[1]
        missing_padding = len(payload_encoded) % 4
        if missing_padding:
            payload_encoded += "=" * (4 - missing_padding)

        payload_json = base64.urlsafe_b64decode(payload_encoded).decode("utf-8")

        # Step 3: Parse as JSON
        payload = json.loads(payload_json)

        # Step 4: Extract the user ID
        user_id = payload.get("sub")

        # Step 5: Check if role is "admin" or "dataengineer"
        role = payload.get("role")
        valid_roles = {"admin", "dataengineer"}
        has_valid_role = role in valid_roles

        # Step 6: Check if scopes contain required permissions
        required_scopes = {"agent.get", "pack.create", "source.create"}
        scopes = set(payload.get("scopes", []))
        has_required_scopes = required_scopes.issubset(scopes)

        return {
            "user_id": user_id,
            "role_valid": has_valid_role,
            "scopes_valid": has_required_scopes,
        }

    except Exception as e:
        return {"error": str(e)}
