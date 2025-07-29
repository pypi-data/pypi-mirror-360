import json
from typing import Optional, Dict, Any  # Added Any

import requests  # type: ignore # If requests doesn't have stubs or for explicit ignoring
from requests.exceptions import RequestException  # For better error handling

from isek.utils.log import log  # Assuming logger is configured
from isek.node.registry import Registry  # Assuming Registry is an ABC or base class

# Type alias for node metadata and node info
NodeMetadata = Dict[str, str]
NodeInfo = Dict[
    str, Any
]  # e.g., {"node_id": str, "host": str, "port": int, "metadata": NodeMetadata}


class IsekCenterRegistry(Registry):
    """
    An implementation of the :class:`~isek.node.registry.Registry` interface
    that interacts with a centralized "Isek Center" service via HTTP API calls.

    This registry delegates node registration, deregistration, lease renewal,
    and discovery to an external Isek Center. All operations involve sending
    HTTP requests to predefined endpoints on this central service.
    """

    def __init__(
        self,
        host: str = "localhost",  # Made non-optional with default
        port: int = 8088,  # Made non-optional with default
    ):
        """
        Initializes the IsekCenterRegistry.

        :param host: The hostname or IP address of the Isek Center service.
                     Defaults to "localhost".
        :type host: str
        :param port: The port number on which the Isek Center service is listening.
                     Defaults to 8088.
        :type port: int
        """
        if not host:  # Should not happen with default, but good practice
            raise ValueError("Host for Isek Center cannot be empty.")
        if not isinstance(port, int) or not (0 < port < 65536):
            raise ValueError(f"Invalid port number for Isek Center: {port}")

        self.center_address: str = f"http://{host}:{port}"
        # self.node_info: NodeInfo = {} # This instance variable seems to store the last registered node's info
        # by this instance, which might be confusing if multiple nodes use
        # the same registry instance. Consider if this state is necessary at instance level.
        # For now, I'll assume it's for the node this client represents.
        log.info(
            f"IsekCenterRegistry initialized. Center address: {self.center_address}"
        )

    def _handle_response(
        self, response: requests.Response, operation_name: str
    ) -> Dict[str, Any]:
        """
        Helper method to handle HTTP responses from the Isek Center.

        Checks for successful HTTP status codes and expected JSON structure.

        :param response: The `requests.Response` object.
        :type response: requests.Response
        :param operation_name: A string describing the operation (e.g., "register node").
        :type operation_name: str
        :return: The parsed JSON response data if successful.
        :rtype: typing.Dict[str, typing.Any]
        :raises HTTPError: If the HTTP request itself failed (e.g., 4xx, 5xx status codes).
        :raises ConnectionError: If there was a network problem.
        :raises Timeout: If the request timed out.
        :raises RuntimeError: If the Isek Center returns a non-200 'code' in its JSON response.
        :raises ValueError: If the response content is not valid JSON.
        """
        response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
        try:
            response_json: Dict[str, Any] = response.json()
        except json.JSONDecodeError as e:
            log.error(
                f"Failed to decode JSON response during {operation_name} "
                f"from {response.url}. Response text: '{response.text[:200]}...'"
            )
            raise ValueError(
                f"Invalid JSON response received during {operation_name}."
            ) from e

        if response_json.get("code") != 200:
            error_message = response_json.get(
                "message", "Unknown error from Isek Center."
            )
            log.error(
                f"{operation_name.capitalize()} failed at Isek Center. "
                f"Code: {response_json.get('code')}, Message: {error_message}, "
                f"Full response: {response_json}"
            )
            raise RuntimeError(
                f"{operation_name.capitalize()} failed at Isek Center: {error_message} (Code: {response_json.get('code')})"
            )
        return response_json

    def register_node(
        self,
        node_id: str,
        host: str,
        port: int,
        metadata: Optional[NodeMetadata] = None,
    ) -> None:
        """
        Registers a node with the Isek Center.

        Sends a POST request with node information to the center's `/isek_center/register` endpoint.

        :param node_id: The unique identifier for the node.
        :type node_id: str
        :param host: The hostname or IP address where the node can be reached.
        :type host: str
        :param port: The port number on which the node is listening.
        :type port: int
        :param metadata: Optional dictionary of key-value pairs providing additional
                         information about the node. Defaults to an empty dictionary.
        :type metadata: typing.Optional[NodeMetadata]
        :raises RuntimeError: If the Isek Center returns an error code in its response.
        :raises requests.exceptions.RequestException: For network errors or HTTP error statuses.
        """
        register_url = f"{self.center_address}/isek_center/register"
        current_node_info: NodeInfo = {  # Use a local variable for current operation
            "node_id": node_id,
            "host": host,
            "port": port,
            "metadata": metadata or {},
        }
        # self.node_info = current_node_info # If self.node_info is intended to store this

        try:
            log.debug(
                f"Registering node '{node_id}' at {register_url} with data: {current_node_info}"
            )
            response = requests.post(
                url=register_url, json=current_node_info, timeout=10
            )  # Added timeout
            response_data = self._handle_response(
                response, f"register node '{node_id}'"
            )
            # Assuming response_data might contain useful info, e.g., lease ID or confirmation details
            log.info(
                f"Node '{node_id}' registered successfully. "
                f"Isek Center response: {response_data.get('message', 'OK')}"
            )
        except RequestException as e:
            log.error(
                f"Failed to register node '{node_id}' due to a network/HTTP error: {e}",
                exc_info=True,
            )
            raise  # Re-raise the requests exception
        except (RuntimeError, ValueError) as e:  # From _handle_response
            log.error(
                f"Failed to register node '{node_id}' due to Isek Center error: {e}",
                exc_info=True,
            )
            raise  # Re-raise the application-level error

    def lease_refresh(self, node_id: str) -> None:
        """
        Refreshes the lease for a registered node with the Isek Center.

        Sends a POST request with the `node_id` to the center's `/isek_center/renew` endpoint.

        :param node_id: The ID of the node whose lease needs to be refreshed.
        :type node_id: str
        :raises RuntimeError: If the Isek Center returns an error code in its response.
        :raises requests.exceptions.RequestException: For network errors or HTTP error statuses.
        """
        lease_refresh_url = f"{self.center_address}/isek_center/renew"
        payload = {"node_id": node_id}

        try:
            log.debug(f"Refreshing lease for node '{node_id}' at {lease_refresh_url}")
            response = requests.post(
                url=lease_refresh_url, json=payload, timeout=5
            )  # Added timeout
            response_data = self._handle_response(
                response, f"refresh lease for node '{node_id}'"
            )
            log.debug(
                f"Node '{node_id}' lease refreshed successfully. "
                f"Isek Center response: {response_data.get('message', 'OK')}"
            )
        except RequestException as e:
            log.error(
                f"Failed to refresh lease for node '{node_id}' due to a network/HTTP error: {e}",
                exc_info=True,
            )
            raise
        except (RuntimeError, ValueError) as e:
            log.error(
                f"Failed to refresh lease for node '{node_id}' due to Isek Center error: {e}",
                exc_info=True,
            )
            raise

    def get_available_nodes(self) -> Dict[str, NodeInfo]:
        """
        Retrieves information about all currently available nodes from the Isek Center.

        Sends a GET request to the center's `/isek_center/available_nodes` endpoint.
        The expected response structure from Isek Center is a JSON object with a 'data' key,
        which in turn has an 'available_nodes' key containing the dictionary of nodes.

        :return: A dictionary where keys are node IDs and values are dictionaries
                 containing the node information (host, port, metadata, etc.)
                 as provided by the Isek Center.
        :rtype: typing.Dict[str, NodeInfo]
        :raises RuntimeError: If the Isek Center returns an error code or an unexpected data structure.
        :raises requests.exceptions.RequestException: For network errors or HTTP error statuses.
        """
        available_nodes_url = f"{self.center_address}/isek_center/available_nodes"
        try:
            log.debug(f"Fetching available nodes from {available_nodes_url}")
            response = requests.get(
                url=available_nodes_url, timeout=10
            )  # Added timeout
            response_data = self._handle_response(response, "get available nodes")

            nodes_data = response_data.get("data", {}).get("available_nodes")
            if nodes_data is None or not isinstance(nodes_data, dict):
                log.error(
                    "Isek Center response for available nodes is missing 'data.available_nodes' "
                    f"or it's not a dictionary. Response: {response_data}"
                )
                raise RuntimeError(
                    "Invalid data structure for available nodes received from Isek Center."
                )
            log.debug(f"Successfully fetched {len(nodes_data)} available nodes.")
            return nodes_data  # type: ignore # If linter complains about Dict[str, NodeInfo] vs Dict[str, Any]
        except RequestException as e:
            log.error(
                f"Failed to get available nodes due to a network/HTTP error: {e}",
                exc_info=True,
            )
            raise
        except (RuntimeError, ValueError) as e:
            log.error(
                f"Failed to get available nodes due to Isek Center error: {e}",
                exc_info=True,
            )
            raise

    def deregister_node(self, node_id: str) -> None:
        """
        Deregisters a node from the Isek Center.

        Sends a POST request with the `node_id` to the center's `/isek_center/deregister` endpoint.

        :param node_id: The ID of the node to deregister.
        :type node_id: str
        :raises RuntimeError: If the Isek Center returns an error code in its response.
        :raises requests.exceptions.RequestException: For network errors or HTTP error statuses.
        """
        deregister_url = f"{self.center_address}/isek_center/deregister"
        payload = {"node_id": node_id}

        try:
            log.debug(f"Deregistering node '{node_id}' at {deregister_url}")
            response = requests.post(
                url=deregister_url, json=payload, timeout=10
            )  # Added timeout
            response_data = self._handle_response(
                response, f"deregister node '{node_id}'"
            )
            log.info(
                f"Node '{node_id}' deregistered successfully. "
                f"Isek Center response: {response_data.get('message', 'OK')}"
            )
        except RequestException as e:
            log.error(
                f"Failed to deregister node '{node_id}' due to a network/HTTP error: {e}",
                exc_info=True,
            )
            raise
        except (RuntimeError, ValueError) as e:
            log.error(
                f"Failed to deregister node '{node_id}' due to Isek Center error: {e}",
                exc_info=True,
            )
            raise
