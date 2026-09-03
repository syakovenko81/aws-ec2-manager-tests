"""Simple EC2 management helpers for demonstration and testing."""

from __future__ import annotations

import re
from typing import Any

import boto3
from botocore.exceptions import ClientError

INSTANCE_ID_PATTERN = re.compile(r"^i-(?:[0-9a-f]{8}|[0-9a-f]{17})$")


def _get_ec2_client(ec2_client: Any = None) -> Any:
    """Return the provided client or create a default boto3 EC2 client."""
    return ec2_client or boto3.client("ec2")


def _validate_instance_id(instance_id: str) -> None:
    """Ensure the EC2 instance ID is present and uses a valid format."""
    if not instance_id or not instance_id.strip():
        raise ValueError("Instance ID must not be empty.")

    if not INSTANCE_ID_PATTERN.fullmatch(instance_id):
        raise ValueError(f"Invalid EC2 instance ID: {instance_id}")


def _handle_client_error(error: ClientError, instance_id: str | None = None) -> None:
    """Raise a simple, readable exception based on the AWS error code."""
    error_code = error.response.get("Error", {}).get("Code", "Unknown")
    target = f" for instance {instance_id}" if instance_id else ""

    if error_code in {"AccessDenied", "AccessDeniedException", "UnauthorizedOperation"}:
        raise PermissionError(f"AWS access denied{target}.") from error

    if error_code in {"InvalidInstanceID.NotFound", "ResourceNotFoundException"}:
        raise LookupError(f"EC2 instance not found{target}.") from error

    raise RuntimeError(f"AWS EC2 operation failed{target}: {error_code}") from error


def list_instances(ec2_client: Any = None) -> list[dict[str, Any]]:
    """Return a flattened list of EC2 instances from describe_instances."""
    client = _get_ec2_client(ec2_client)

    try:
        response = client.describe_instances()
    except ClientError as error:
        _handle_client_error(error)

    instances: list[dict[str, Any]] = []
    for reservation in response.get("Reservations", []):
        instances.extend(reservation.get("Instances", []))
    return instances


def start_instance(instance_id: str, ec2_client: Any = None) -> dict[str, Any]:
    """Start an EC2 instance and return the first state-change record."""
    _validate_instance_id(instance_id)
    client = _get_ec2_client(ec2_client)

    try:
        response = client.start_instances(InstanceIds=[instance_id])
    except ClientError as error:
        _handle_client_error(error, instance_id=instance_id)

    return response.get("StartingInstances", [{}])[0]


def stop_instance(instance_id: str, ec2_client: Any = None) -> dict[str, Any]:
    """Stop an EC2 instance and return the first state-change record."""
    _validate_instance_id(instance_id)
    client = _get_ec2_client(ec2_client)

    try:
        response = client.stop_instances(InstanceIds=[instance_id])
    except ClientError as error:
        _handle_client_error(error, instance_id=instance_id)

    return response.get("StoppingInstances", [{}])[0]
