from isek.utils.log import team_log
import uvicorn
import threading
import time
from typing import Dict, Any, Optional, Tuple

from flask import Flask, request, jsonify, Blueprint

# --- Global State & Configuration ---
isek_center_blueprint = Blueprint(
    "isek_center_blueprint", __name__, url_prefix="/isek_center"
)

# In-memory storage for registered nodes.
# Structure: { "node_id": {"node_id": str, "host": str, "port": int, "metadata": dict, "expires_at": float} }
nodes: Dict[str, Dict[str, Any]] = {}
NODE_LOCK = threading.Lock()

LEASE_DURATION: int = 30

# --- Type Alias ---
FlaskResponse = Tuple[Dict[str, Any], int]


# --- Response Helper Class ---
class CommonResponse:
    """A helper class to standardize JSON API responses."""

    def __init__(self, data: Optional[Any], code: int, message: str):
        self.data: Optional[Any] = data
        self.code: int = code
        self.message: str = message

    @classmethod
    def success(
        cls, data: Optional[Any] = None, code: int = 200, message: str = "success"
    ) -> FlaskResponse:
        return jsonify(cls(data, code, message).to_dict()), code

    @classmethod
    def fail(
        cls, message: str, code: int = 400, data: Optional[Any] = None
    ) -> FlaskResponse:
        return jsonify(cls(data, code, message).to_dict()), code

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message, "data": self.data}


# --- Flask Route Definitions ---
@isek_center_blueprint.route("/register", methods=["POST"])
def register_node_route() -> FlaskResponse:
    data = request.json
    if not data:
        return CommonResponse.fail(message="Request body must be JSON.", code=400)

    node_id = data.get("node_id")
    host = data.get("host")
    port = data.get("port")
    metadata = data.get("metadata")

    if not all([node_id, host, port]):
        return CommonResponse.fail(
            message="'node_id', 'host', and 'port' are required fields.", code=400
        )

    if not isinstance(port, int):
        return CommonResponse.fail(message="'port' must be an integer.", code=400)

    with NODE_LOCK:
        nodes[node_id] = {
            "node_id": node_id,
            "host": host,
            "port": port,
            "metadata": metadata or {},
            "expires_at": time.time() + LEASE_DURATION,
        }
    team_log.info(f"Node registered/updated: {node_id}")
    return CommonResponse.success(message=f"Node '{node_id}' registered successfully.")


@isek_center_blueprint.route("/deregister", methods=["POST"])
def deregister_node_route() -> FlaskResponse:
    data = request.json
    if not data:
        return CommonResponse.fail(message="Request body must be JSON.", code=400)

    node_id = data.get("node_id")

    if not node_id:
        return CommonResponse.fail(message="'node_id' is required.", code=400)

    with NODE_LOCK:
        if node_id not in nodes:
            return CommonResponse.fail(
                message=f"Node '{node_id}' not found for deregistration.", code=404
            )
        removed_node = nodes.pop(node_id)
    team_log.debug(f"Node deregistered: {node_id}, Details: {removed_node}")
    return CommonResponse.success(
        message=f"Node '{node_id}' deregistered successfully."
    )


@isek_center_blueprint.route("/available_nodes", methods=["GET"])
def get_available_nodes_route() -> FlaskResponse:
    current_time = time.time()
    with NODE_LOCK:
        active_nodes = {
            k: v for k, v in nodes.items() if v.get("expires_at", 0) > current_time
        }

    response_payload = {"available_nodes": active_nodes}
    team_log.debug(f"Returning {len(active_nodes)} available nodes.")
    return CommonResponse.success(data=response_payload)


@isek_center_blueprint.route("/renew", methods=["POST"])
def renew_lease_route() -> FlaskResponse:
    data = request.json
    if not data:
        return CommonResponse.fail(message="Request body must be JSON.", code=400)

    node_id = data.get("node_id")

    if not node_id:
        return CommonResponse.fail(message="'node_id' is required.", code=400)

    with NODE_LOCK:
        if node_id in nodes:
            nodes[node_id]["expires_at"] = time.time() + LEASE_DURATION
            team_log.debug(f"Lease renewed for node: {node_id}")
            return CommonResponse.success(
                message=f"Lease for node '{node_id}' renewed successfully."
            )
        else:
            return CommonResponse.fail(
                message=f"Node '{node_id}' not found for lease renewal.", code=404
            )


# --- Background Task ---
def cleanup_expired_nodes():
    """Periodically removes expired nodes from the registry."""
    while True:
        time.sleep(LEASE_DURATION / 2)
        current_time = time.time()
        with NODE_LOCK:
            expired_node_ids = [
                node_id
                for node_id, data in nodes.items()
                if data.get("expires_at", 0) < current_time
            ]
            for node_id in expired_node_ids:
                team_log.info(f"Node lease expired, removing: {node_id}")
                del nodes[node_id]


# --- Main Application Factory and Entry Point ---
def main():
    """Main function to run the Isek Center."""
    app = Flask(__name__)
    app.register_blueprint(isek_center_blueprint)

    # Start the background task for cleaning up expired nodes
    cleanup_thread = threading.Thread(target=cleanup_expired_nodes, daemon=True)
    cleanup_thread.start()

    team_log.info("Starting Isek Center...")
    # Use uvicorn to run the Flask app for better performance
    uvicorn.run(app, host="0.0.0.0", port=8088, log_level="info")


if __name__ == "__main__":
    main()
