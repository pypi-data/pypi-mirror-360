"""
WinningVariant Python Client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WinningVariant is a client for running experiments created in the Winning Variant Snowflake Native App.

Basic usage:

   >>> from winningvariant import WinningVariant
   >>> wv = WinningVariant(conn=session) # Snowflake session
   >>>
   >>> variant = wv.create_assignment("<subject_id>", "<experiment_id>")
   >>> if variant == "TREATMENT-A":
   >>>     print("Do something for the treatment A group")
   >>> elif variant == "TREATMENT-B":
   >>>     print("Do something for the treatment B group")
   >>> else:
   >>>     print("Do something for the control group")

Full documentation is at <https://docs.winningvariant.com>.

:copyright: (c) 2025 Winning Variant LLC
:license: GPL-3.0
"""

from .client import WinningVariantClient, SnowflakeExecutionError
from .assignment import Assignment