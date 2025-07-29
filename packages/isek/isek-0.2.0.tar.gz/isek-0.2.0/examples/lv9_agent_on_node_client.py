from isek.utils.log import log
from isek.node.node_v2 import Node

def main():
    """
    This script acts as a client to interact with the agent hosted on the server node.
    Run this script in a separate terminal after starting the lv9 server.
    """
    # Logging is now automatically configured.
    # You can set the log level via the LOG_LEVEL environment variable.
    # e.g., export LOG_LEVEL=DEBUG

    # Server details must match the running server script
    server_node_id = "agent_server_1"
    server_host = "localhost"
    server_port = 9005

    # Create a client node to send messages
    client_node = Node(node_id="lv9_client")
    
    # Manually add the server's info to the client's local cache
    client_node.all_nodes[server_node_id] = {
        "host": server_host,
        "port": server_port,
        "metadata": {"url": f"http://{server_host}:{server_port}"}
    }
    
    print("--- LV9 Agent Client ---")
    print("This client will test the agent's memory and tool use.")
    print("------------------------\n")
    log.info("Client is ready to send messages.")

    # --- Test 1: Memory ---
    print("Test 1: Storing a fact in the agent's memory...")
    prompt1 = "Hi there, please remember that my favorite color is blue."
    print(f"CLIENT: {prompt1}")
    response1 = client_node.send_message(server_node_id, prompt1)
    print(f"AGENT: {response1}\n")

    # --- Test 2: Retrieval and Tool Use ---
    print("Test 2: Asking a question that requires both memory and a tool...")
    prompt2 = "What is 15 plus 8? And what is my favorite color?"
    print(f"CLIENT: {prompt2}")
    response2 = client_node.send_message(server_node_id, prompt2)
    print(f"AGENT: {response2}\n")

    print("--- Test Complete ---")

if __name__ == "__main__":
    main() 