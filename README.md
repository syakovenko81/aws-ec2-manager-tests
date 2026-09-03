# aws-ec2-manager-tests

Small standalone Python project that demonstrates testing an AWS EC2 automation helper with `pytest` and mocked `boto3` clients.

## Project purpose

This project shows how to:

- write a simple AWS EC2 management module with `boto3`
- validate inputs before calling AWS APIs
- handle common AWS `ClientError` cases
- test AWS automation code safely with `pytest` and mocks

The focus is on practical testing techniques, not on building a production-grade tool.

## Project structure

```text
aws-ec2-manager-tests/
├── ec2_manager.py
├── test_ec2_manager.py
├── requirements.txt
└── README.md
```

## Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the tests

```bash
pytest -v
```

## Notes

- The module uses the standard `boto3` credential provider chain.
- No AWS credentials are hardcoded.
- All AWS API calls are mocked in the test suite.
- Running the tests does not modify any real AWS resources.