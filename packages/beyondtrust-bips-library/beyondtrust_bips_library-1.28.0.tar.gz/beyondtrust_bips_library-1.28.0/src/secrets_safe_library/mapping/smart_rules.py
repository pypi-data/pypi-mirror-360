"""
This file contains the fields mapping for each endpoint and version related to Smart
Rules.

More info for the fields included in each endpoint and version:
- https://docs.beyondtrust.com/bips/docs/beyondinsight-api
- https://docs.beyondtrust.com/bips/docs/passwordsafe-api
- https://docs.beyondtrust.com/bips/docs/secrets-safe-api
"""

from secrets_safe_library.constants.endpoints import GET_SMARTRULES_ID
from secrets_safe_library.constants.versions import Version

fields = {
    GET_SMARTRULES_ID: {
        Version.DEFAULT: [
            "SmartRuleID",
            "OrganizationID ",
            "Title",
            "Description",
            "Category",
            "Status",
            "LastProcessedDate",
            "IsReadOnly",
            "RuleType",
        ],
    },
}
