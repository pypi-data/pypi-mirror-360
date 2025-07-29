"""SmartRules module, all the logic to manage Smart Rules from BeyondInsight API"""

import logging

from cerberus import Validator

from secrets_safe_library import exceptions, utils
from secrets_safe_library.authentication import Authentication
from secrets_safe_library.core import APIObject


class SmartRule(APIObject):

    def __init__(self, authentication: Authentication, logger: logging.Logger = None):
        super().__init__(authentication, logger)

        # Schema rules used for validations
        self._schema = {
            "title": {"type": "string", "maxlength": 256, "nullable": True},
            "rule_id": {"type": "integer", "nullable": True},
        }
        self._validator = Validator(self._schema)

    def get_smart_rule_by_id(self, rule_id: int) -> dict:
        """
        Returns a SmartRule by ID.

        API: GET SmartRules/{id}

        Args:
            rule_id (int): The SmartRule ID.

        Returns:
            dict: SmartRule.
        """

        attributes = {"rule_id": rule_id}

        if not self._validator.validate(attributes, update=True):
            raise exceptions.OptionsError(f"Please check: {self._validator.errors}")

        endpoint = f"/smartrules/{rule_id}"

        utils.print_log(
            self._logger,
            f"Calling get_smart_rule_by_id endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()

    def get_smart_rule_by_title(self, title: str) -> dict:
        """
        Returns a SmartRule by Title.

        API: GET SmartRules?title={title}

        Args:
            title (str): The SmartRule title.

        Returns:
            dict: SmartRule.
        """

        attributes = {"title": title}

        if not self._validator.validate(attributes, update=True):
            raise exceptions.OptionsError(f"Please check: {self._validator.errors}")

        query_string = self.make_query_string(attributes)
        endpoint = f"/smartrules/?{query_string}"

        utils.print_log(
            self._logger,
            f"Calling get_smart_rule_by_title endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()

    def list_assets_by_smart_rule_id(
        self, smart_rule_id: int, limit: int = None, offset: int = None
    ) -> list:
        """
        Returns a list of assets for the given smart rule ID.

        API: GET SmartRules/{id}/Assets

        Args:
            smart_rule_id (int): The Smart Rule ID.
            limit (int, optional): limit the results.
            offset (int, optional): skip the first (offset) number of assets.

        Returns:
            list: List of assets for the specified smart_rule_id.
        """

        attributes = {"rule_id": smart_rule_id}

        if not self._validator.validate(attributes, update=True):
            raise exceptions.OptionsError(f"Please check: {self._validator.errors}")

        params = {
            "limit": limit,
            "offset": offset,
        }
        query_string = self.make_query_string(params)

        endpoint = f"/smartrules/{smart_rule_id}/assets?{query_string}"

        utils.print_log(
            self._logger,
            f"Calling list_assets_by_smart_rule_id endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint)

        return response.json()

    def get_quick_rule_by_id(self, rule_id: int) -> dict:
        """
        Returns a QuickRule by ID.

        API: GET QuickRules/{id}

        Args:
            rule_id (int): The QuickRule ID.

        Returns:
            dict: QuickRule.
        """

        attributes = {"rule_id": rule_id}

        if not self._validator.validate(attributes, update=True):
            raise exceptions.OptionsError(f"Please check: {self._validator.errors}")

        endpoint = f"/quickrules/{rule_id}"

        utils.print_log(
            self._logger,
            f"Calling get_quick_rule_by_id endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()

    def get_quick_rule_by_title(self, title: str) -> dict:
        """
        Returns a QuickRule by Title.

        API: GET QuickRules?title={title}

        Args:
            title (str): The QuickRule title.

        Returns:
            dict: QuickRule.
        """

        attributes = {"title": title}

        if not self._validator.validate(attributes, update=True):
            raise exceptions.OptionsError(f"Please check: {self._validator.errors}")

        query_string = self.make_query_string(attributes)
        endpoint = f"/quickrules/?{query_string}"

        utils.print_log(
            self._logger,
            f"Calling get_quick_rule_by_title endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()
