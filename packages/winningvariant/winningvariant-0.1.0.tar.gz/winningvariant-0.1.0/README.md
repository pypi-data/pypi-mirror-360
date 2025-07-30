# Winning Variant Python SDK

**This SDK is currently in Public Preview**

This package provides a Python SDK for interacting with the Winning Variant Snowflake Native App.

## Install
```bash
pip install winningvariant
```

## Basic Usage

```python
from winningvariant import WinningVariantClient

# `session` is a Snowflake Snowpark session object
wv = WinningVariantClient(session)

# Get an assignment for a subject inside of an experiment
assignment = wv.get_assignment(subject_id="user_123", experiment_id="my-experiment")
print('Existing assignment:', assignment)

# Get or create an assignment
assignment = wv.create_assignment(subject_id="user_123", experiment_id="my-experiment")
print('New assignment:', assignment)
```

## Resources

* [Documentation](https://docs.winningvariant.com/sdk/python)
* [Snowflake Marketplace Listing](https://app.snowflake.com/marketplace/listing/GZTYZ5CUYB)
* [Homepage](https://www.winningvariant.com)

## Copyright

Copyright (c) 2025 Winning Variant LLC. All Rights Reserved.

## License

GNU GENERAL PUBLIC LICENSE v3