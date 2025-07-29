from textwrap import dedent
from isek.node.node_v2 import Node
from isek.adapter.agno_adapter import AgnoAdapter
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from isek.utils.log import log

import json
import dotenv
import os
dotenv.load_dotenv()

def query_dexscreener(token_name):
    """Query DexScreener API to get token information"""
    import requests
    
    base_url = "https://api.dexscreener.com/latest/dex/search"
    params = {"q": f"{token_name}/SOL"}
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying DexScreener: {e}")
        return None

# Initialize the research agent with advanced journalistic capabilities
research_agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools(),query_dexscreener],
    description=dedent("""\
        Yo fam! I'm your degen crypto bro who's been in the trenches since 2013 💎🙌
        Been through all the ups and downs, made and lost millions, and now I'm here to help you make it!
        
        What I do best: 
        - Spot the next 100x gem before anyone else 🚀
        - Build the strongest crypto fam on CT 🤝
        - DYOR but make it fun and profitable 📈
        - Keep it real - no BS, just pure alpha 💯\
    """),
    instructions=dedent("""\
        Yo check it fam! Here's how we cook 🧑‍🍳

        1. Drop me the basics ⚡
           - Token name/ticker (like $PEPE, $WOJAK)
           
        2. use the tool to get the token info including the following fields:
            baseToken_address,
            url, 
            baseToken_symbol, 
            txns, 
            volume, 
            priceChange, 
            liquidity, 
            fdv, 
            marketCap
        
        3. Cook that Tweet 🔥
           - Catchy af headline (emojis = engagement)
           - Price action that makes em FOMO
           - Numbers that make sense to normies
           - Drop that contract (transparency = trust)
           - Hashtag game strong #IYKYK

           
        Remember: We eat good together 🍽️ WAGMI\
    """),
    markdown=True,
    show_tool_calls=True,
    add_datetime_to_instructions=True,
)

# Conversational terminal interface
def cli_conversation():
    print("🤖 Welcome to the Agno Meme Tweet Assistant!")
    print("I can help you generate a meme tweet for a given token.")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("-" * 50 + "\n")
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Goodbye! Thanks for chatting with me!")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # Get agent response
            print("\n🤖 Assistant: ", end="")
            # response = agent.run(user_input)
            
            token_info = query_dexscreener(user_input)
            # Get token info from DexScreener
            if token_info:
                print(f"\nToken Information for {user_input}:")
                # print(json.dumps(token_info, indent=2))
                baseToken_address = token_info["pairs"][0]["baseToken"]["address"]
                baseToken_symbol = token_info["pairs"][0]["baseToken"]["symbol"]
                txns = token_info["pairs"][0]["txns"]["h24"]
                volume = token_info["pairs"][0]["volume"]["h24"]
                priceChange = token_info["pairs"][0]["priceChange"]["h24"]
                liquidity = token_info["pairs"][0]["liquidity"]["usd"]
                fdv = token_info["pairs"][0]["fdv"]
                marketCap = token_info["pairs"][0]["marketCap"]
                url = token_info["pairs"][0]["url"]
                print(f"url: {url}")
                print(f"baseToken_address: {baseToken_address}")
                print(f"baseToken_symbol: {baseToken_symbol}")
                print(f"txns: {txns}")
                print(f"volume: {volume}")
                print(f"priceChange: {priceChange}")
                print(f"liquidity: {liquidity}")
                print(f"fdv: {fdv}")
                
                user_input = f"""
                token_name: {user_input} 
                url: {url}
                baseToken_symbol: {baseToken_symbol}
                txns: {txns}
                volume: {volume}
                priceChange: {priceChange}
                liquidity: {liquidity}
                fdv: {fdv}
                marketCap: {marketCap}
                """
            else:
                print(f"\nCould not retrieve information for {user_input}")
            
            research_agent.print_response(user_input, markdown=True)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for chatting with me!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    
        # 3. Start the Node Server with the Agent Team
    server_node_id = "agent_server_1"
    server_port = 9005
    print(f"Starting server node '{server_node_id}' on port {server_port} to host the agent team...")
    log.info("Server node is starting up...")
    
    server_node = Node(
        node_id=server_node_id,
        port=server_port,
        adapter=AgnoAdapter(agent=research_agent)
    )

    # Start the server in the foreground. It will now listen for messages.
    server_node.build_server(daemon=False)

    
    # cli_conversation()