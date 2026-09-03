from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from ec2_manager import list_instances, start_instance, stop_instance


VALID_INSTANCE_ID = "i-1234567890abcdef0"


def make_client_error(code: str, message: str) -> ClientError:
    return ClientError(
        error_response={"Error": {"Code": code, "Message": message}},
        operation_name="TestOperation",
    )


def test_start_instance_success():
    client = MagicMock()
    client.start_instances.return_value = {
        "StartingInstances": [
            {
                "InstanceId": VALID_INSTANCE_ID,
                "CurrentState": {"Name": "pending"},
            }
        ]
    }

    result = start_instance(VALID_INSTANCE_ID, ec2_client=client)

    assert result["InstanceId"] == VALID_INSTANCE_ID
    assert result["CurrentState"]["Name"] == "pending"
    client.start_instances.assert_called_once_with(InstanceIds=[VALID_INSTANCE_ID])


def test_stop_instance_success():
    client = MagicMock()
    client.stop_instances.return_value = {
        "StoppingInstances": [
            {
                "InstanceId": VALID_INSTANCE_ID,
                "CurrentState": {"Name": "stopping"},
            }
        ]
    }

    result = stop_instance(VALID_INSTANCE_ID, ec2_client=client)

    assert result["InstanceId"] == VALID_INSTANCE_ID
    assert result["CurrentState"]["Name"] == "stopping"
    client.stop_instances.assert_called_once_with(InstanceIds=[VALID_INSTANCE_ID])


def test_list_instances_success():
    client = MagicMock()
    client.describe_instances.return_value = {
        "Reservations": [
            {
                "Instances": [
                    {"InstanceId": "i-aaaaaaaaaaaaaaaaa", "State": {"Name": "running"}},
                    {"InstanceId": "i-bbbbbbbbbbbbbbbbb", "State": {"Name": "stopped"}},
                ]
            }
        ]
    }

    result = list_instances(ec2_client=client)

    assert len(result) == 2
    assert result[0]["InstanceId"] == "i-aaaaaaaaaaaaaaaaa"
    assert result[1]["State"]["Name"] == "stopped"
    client.describe_instances.assert_called_once_with()


@pytest.mark.parametrize("instance_id", ["", "   ", "invalid-instance-id", "i-123"])
def test_invalid_instance_id_raises_value_error(instance_id):
    client = MagicMock()

    with pytest.raises(ValueError):
        start_instance(instance_id, ec2_client=client)

    client.start_instances.assert_not_called()


def test_stop_instance_empty_instance_id_does_not_call_aws():
    client = MagicMock()

    with pytest.raises(ValueError):
        stop_instance("", ec2_client=client)

    client.stop_instances.assert_not_called()


def test_start_instance_access_denied_error():
    client = MagicMock()
    client.start_instances.side_effect = make_client_error(
        "AccessDenied", "You are not authorized to perform this operation."
    )

    with pytest.raises(PermissionError, match="AWS access denied"):
        start_instance(VALID_INSTANCE_ID, ec2_client=client)

    client.start_instances.assert_called_once_with(InstanceIds=[VALID_INSTANCE_ID])


def test_stop_instance_resource_not_found_error():
    client = MagicMock()
    client.stop_instances.side_effect = make_client_error(
        "InvalidInstanceID.NotFound", "The instance ID does not exist."
    )

    with pytest.raises(LookupError, match="EC2 instance not found"):
        stop_instance(VALID_INSTANCE_ID, ec2_client=client)

    client.stop_instances.assert_called_once_with(InstanceIds=[VALID_INSTANCE_ID])


def test_list_instances_generic_client_error():
    client = MagicMock()
    client.describe_instances.side_effect = make_client_error(
        "InternalError", "An internal error occurred."
    )

    with pytest.raises(RuntimeError, match="AWS EC2 operation failed: InternalError"):
        list_instances(ec2_client=client)

    client.describe_instances.assert_called_once_with()
