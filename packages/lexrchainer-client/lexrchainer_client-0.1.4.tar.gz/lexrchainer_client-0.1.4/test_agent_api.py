import os
from lexrchainer_client import ClientInterface, AgentBuilder, AgentWrapper
from lexrchainer_client.models import ChainMeta, ModelParams, AgentCreate, UserType
from dotenv import load_dotenv
import uuid
import traceback
import json

def setup_client():
    # Set API key for authentication
    os.environ["LEXRCHAINER_API_KEY"] = "BpXlQI4iLYNI95KLKi9oPhWyVTZbfTHf-fUQ95duJGI"
    # Optionally set API URL if needed, e.g.:
    os.environ["LEXRCHAINER_API_URL"] = "http://localhost:8000"
    load_dotenv()
    return ClientInterface()

def make_minimal_chain_meta():
    return ChainMeta(
        id=str(uuid.uuid4()),
        name="test_agent_chain_" + str(uuid.uuid4())[:8],
        description="Test chain for agent CRUD",
        version="1.0.0",
        default_system_prompt="You are a test agent.",
        static_meta={},
        tools=[],
        models=[],
        default_model_params=ModelParams(
            model="gpt-4o",
            max_tokens=100,
            temperature=0.5,
            top_p=0.9,
            top_k=10
        )
    )

def test_create_agent(client):
    print("\n--- test_create_agent ---")
    chain_meta = make_minimal_chain_meta()
    agent_req = AgentCreate(agent_name="TestAgentAPI", config=chain_meta)
    try:
        # The API expects a dict, not a pydantic object
        resp = client.create_user({
            "username": agent_req.agent_name.lower(),
            "email": agent_req.agent_name.lower() + "@lexr.ai",
            "phone": "9999999999",
            "user_type": UserType.AGENT.value,
            "chain_config": {"json_content": json.dumps(agent_req.config.model_dump())}
        })
        print("Agent created:", resp)
        return resp
    except Exception as e:
        print("Error creating agent:", e)
        traceback.print_exc()
        return None

def test_list_agents(client):
    print("\n--- test_list_agents ---")
    try:
        agents = client.get_agents()
        print(f"Found {len(agents)} agents.")
        for a in agents:
            print(a)
        return agents
    except Exception as e:
        print("Error listing agents:", e)
        traceback.print_exc()
        return None

def test_update_agent(client, agent_id, new_name):
    print("\n--- test_update_agent ---")
    chain_meta = make_minimal_chain_meta()
    agent_update = {
        "agent_name": new_name,
        "config": chain_meta.model_dump()
    }
    try:
        resp = client.update_agent(agent_id, agent_update)
        print("Agent updated:", resp)
        return resp
    except Exception as e:
        print("Error updating agent:", e)
        traceback.print_exc()
        return None

def test_delete_agent(client, agent_id):
    print("\n--- test_delete_agent ---")
    try:
        client.delete_user(agent_id)
        print(f"Agent {agent_id} deleted.")
        return True
    except Exception as e:
        print("Error deleting agent:", e)
        traceback.print_exc()
        return False

def test_invalid_agent_creation(client):
    print("\n--- test_invalid_agent_creation (missing name) ---")
    try:
        chain_meta = make_minimal_chain_meta()
        # Missing agent_name
        agent_req = {"config": chain_meta.model_dump()}
        resp = client.create_user(agent_req)
        print("Unexpected success:", resp)
    except Exception as e:
        print("Expected error (missing name):", e)
    print("\n--- test_invalid_agent_creation (missing config) ---")
    try:
        agent_req = {"username": "bad_agent", "user_type": UserType.AGENT.value}
        resp = client.create_user(agent_req)
        print("Unexpected success:", resp)
    except Exception as e:
        print("Expected error (missing config):", e)

def test_agent_builder(agent_name: str, msg: str):
    try:
        '''
        .with_system_prompt("""You are a VP of marketing. Your job is to manage the marketing team of agents and create a marketing strategy for a new Legal AI product. 
                            Always use SequentialThinking tool to think step by step to create the execution plan.
                            Always use TaskManagerTool to create tasks and assign them to yourself or other agents. Create separate conversations with agents to give them tasks and get their outcomes.
                            Always provide tools to the agents to use. This will empower them to do more and be more productive.

                            You have following tools at your disposal to provide to the agents: SerpTool, ScraperTool, SequentialThinking, TaskManagerTool, AgentConversationTool.
                            "SerpTool" to search web and "ScraperTool" to get Website content to answer the user's question. Make sure you visit the website to get the latest information. 
                            "AgentConversationTool" to create a new agents, conversations and send messages to an existing agent or conversation. Use this to create teams of agents to discuss and collaborate.
                            "LexrIndex" to search for caselaw, statutes, rules and regulations and other legal documents.
                                """)
        '''
        agent = (AgentBuilder(agent_name)
            .with_model("lexr/gpt-4o")
            .with_system_prompt("You are a helpful assistant. Use AgentConversationTool to create a new agents, conversations and send messages to an existing agent or conversation. Use this to create teams of agents to discuss and collaborate.")
            .with_tool("AgentConversationTool")
            .create_agent())
        print("Sending message to agent...")
        response = None
        response = agent.send_message(msg, streaming=False)
        print("Agent response:", response)
        print(f"Final Message:\n{json.loads(response[-1].replace('data: ', ''))['content']}")
        return agent, response
    except Exception as e:
        traceback.print_exc()
        print("Error testing agent:", e)
        return None, None

def test_agent_conversation(agent: AgentWrapper):
    try:
        response1 = agent.send_message("What is your name?")
        print("First response:", response1)
        response2 = agent.send_message("Can you help me with a task?")
        print("Second response:", response2)
        return response1, response2
    except Exception as e:
        print("Error in conversation test:", e)
        return None, None

def test_agent_memory(agent: AgentWrapper):
    try:
        response = agent.send_message("Can you summarize our previous conversation?")
        print("Memory test response:", response)
        return response
    except Exception as e:
        print("Error in memory test:", e)
        return None

def test_agent_capabilities(agent: AgentWrapper):
    try:
        code_response = agent.send_message("Write a simple Python function to calculate factorial")
        print("Code generation response:", code_response)
        explain_response = agent.send_message("Explain how a binary search works")
        print("Explanation response:", explain_response)
        return code_response, explain_response
    except Exception as e:
        print("Error in capabilities test:", e)
        return None, None

def test_agent_chain_operations(agent: AgentWrapper):
    try:
        list_response = agent.send_message("Generate a list of 5 random numbers between 1 and 100")
        print("List generation response:", list_response)
        sort_response = agent.send_message("Now sort those numbers in ascending order")
        print("Sorting response:", sort_response)
        stats_response = agent.send_message("Calculate the mean and median of these sorted numbers")
        print("Statistics response:", stats_response)
        return list_response, sort_response, stats_response
    except Exception as e:
        print("Error in chain operations test:", e)
        return None, None, None

def test_invalid_agent_creation():
    try:
        print("\n--- test_invalid_agent_creation (missing model) ---")
        agent = (AgentBuilder("BadAgent")
            .with_system_prompt("Missing model should fail.")
            .create_agent())
        print("Unexpected success:", agent)
    except Exception as e:
        print("Expected error (missing model):", e)
    try:
        print("\n--- test_invalid_agent_creation (invalid tool) ---")
        agent = (AgentBuilder("BadAgent2")
            .with_model("lexr/gpt-4o")
            .with_tool("NonExistentTool")
            .create_agent())
        print("Unexpected success:", agent)
    except Exception as e:
        print("Expected error (invalid tool):", e)

def main():
    load_dotenv()
    client = setup_client()
    # Create agent
    #agent = test_create_agent(client)
    #agent_id = agent["id"] if agent and "id" in agent else None
    #agent, initial_response = test_agent_builder("test_agent_" + str(uuid.uuid4())[:8], "Design a marketing strategy for a new Legal AI product. Create agents with varied backgrounds and tool access to discuss and collaborate on the strategy. After detailed research, create a report in MD format.")
    agent, initial_response = test_agent_builder("test_agent_" + str(uuid.uuid4())[:8], "Create multiple agents of different backgrounds and expertise. Always provide them with tools (SerpTool, ScraperTool, SequentialThinking). Analyse the market size for an AI based event planning app, targeting women aged 20-40 in India who purchase online regularly. Create multiple conversations with these agents to discuss on different topics. Keep asking agents to provide more details and perspectives. Your job is to make sure that the topic is discussed in detail and a lot of perspectives are considered. Instruct agents to use tools to do their job. Encourage them to provide new perspectives and insights by conducting research. Create a report with detailed reasoning and citations in MD format.")
    '''
    if agent:
        test_agent_conversation(agent)
        test_agent_memory(agent)
        test_agent_capabilities(agent)
        test_agent_chain_operations(agent)
    test_invalid_agent_creation()

    
    # List agents
    test_list_agents(client)
    # Update agent
    if agent_id:
        test_update_agent(client, agent_id, "TestAgentAPIUpdated")
    # Invalid agent creation
    test_invalid_agent_creation(client)
    # Delete agent
    if agent_id:
        test_delete_agent(client, agent_id)
    '''
if __name__ == "__main__":
    main()
