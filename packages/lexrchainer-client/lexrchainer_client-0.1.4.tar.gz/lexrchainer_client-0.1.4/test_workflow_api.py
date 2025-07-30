import os
from dotenv import load_dotenv
from lexrchainer_client import ClientInterface, models
import traceback
import uuid
from datetime import datetime, timedelta
from lexrchainer_client.agent_builder import AgentBuilder

def setup_client():
    os.environ["LEXRCHAINER_API_KEY"] = "hF32ac2435DcimhDt8AETBxuVrKwPy7kBoarFD8deWc"
    os.environ["LEXRCHAINER_API_URL"] = "http://localhost:8000"
    load_dotenv()
    return ClientInterface()

def to_isoformat_dict(model):
    def convert(obj):
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(i) for i in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj.total_seconds())
        else:
            return obj
    return convert(model.model_dump())

def test_create_workflow(client):
    try:
        # Create agent user with chain using AgentBuilder
        agent_name = f"agent_{uuid.uuid4().hex[:8]}"
        agent_builder = AgentBuilder(agent_name, client)
        agent_builder.with_model("lexr/gpt-4o").with_system_prompt("You are a helpful agent.")
        agent_wrapper = agent_builder.create_agent()
        agent_id = agent_wrapper.agent_user_id

        # Create human user with chain using AgentBuilder (but do not create conversation)
        human_name = f"human_{uuid.uuid4().hex[:8]}"
        from lexrchainer_client.models import UserCreate, UserType
        human_user = client.create_user(UserCreate(
            username=human_name,
            email=f"{human_name}@test.com",
            phone=f"+91123456{uuid.uuid4().hex[:4]}",
            user_type=UserType.HUMAN))
        
        human_id = human_user["id"] if isinstance(human_user, dict) else getattr(human_user, "id", None)

        goal = "Test workflow goal"
        instructions = ["Step 1: Do something", "Step 2: Do something else"]
        workflow_req = models.WorkflowCreateRequest(
            owner_agent_id=agent_id,
            owner_human_id=human_id,
            goal=goal,
            instructions=instructions,
            workspace_id=None
        )
        payload = to_isoformat_dict(workflow_req)
        workflow = client.create_workflow(models.WorkflowCreateRequest(**payload))
        print(f"Workflow created: {workflow}")
        return workflow
    except Exception as e:
        traceback.print_exc()
        print(f"Error creating workflow: {e}")
        return None

def test_create_workflow_run(client, workflow_id, owner_agent_id, owner_human_id):
    try:
        goal = "Test workflow run goal"
        instructions = ["Run step 1", "Run step 2"]
        workflow_run_req = models.WorkflowRunCreateRequest(
            workflow_id=workflow_id,
            owner_agent_id=owner_agent_id,
            owner_human_id=owner_human_id,
            goal=goal,
            instructions=instructions,
            workspace_id=None
        )
        payload = to_isoformat_dict(workflow_run_req)
        workflow_run = client.create_workflow_run(models.WorkflowRunCreateRequest(**payload))
        print(f"WorkflowRun created: {workflow_run}")
        return workflow_run
    except Exception as e:
        traceback.print_exc()
        print(f"Error creating workflow run: {e}")
        return None

def test_trigger_workflow(client, workflow_run_id):
    try:
        trigger_req = models.RunWorkflowRequest(workflow_run_id=workflow_run_id)
        payload = to_isoformat_dict(trigger_req)
        result = client.trigger_workflow(models.RunWorkflowRequest(**payload))
        print(f"Workflow triggered: {result}")
        return result
    except Exception as e:
        traceback.print_exc()
        print(f"Error triggering workflow: {e}")
        return None

def test_send_message_to_default_conversation(client, workflow_run_id, sender_id):
    try:
        message_req = models.SendMessageRequest(
            workflow_run_id=workflow_run_id,
            sender_id=sender_id,
            message_content="Hello from test!",
            output_handler_config=None
        )
        payload = to_isoformat_dict(message_req)
        result = client.send_message_to_default_conversation(models.SendMessageRequest(**payload))
        print(f"Message sent to default workflow conversation: {result}")
        return result
    except Exception as e:
        traceback.print_exc()
        print(f"Error sending message to default workflow conversation: {e}")
        return None

if __name__ == "__main__":
    client = setup_client()
    print("\n--- Creating Workflow ---")
    workflow = test_create_workflow(client)
    if workflow and hasattr(workflow, "workflow_id"):
        workflow_id = workflow["workflow_id"] if isinstance(workflow, dict) else getattr(workflow, "workflow_id", None)
        owner_agent_id = workflow["owner_agent_id"] if isinstance(workflow, dict) else getattr(workflow, "owner_agent_id", None)
        owner_human_id = workflow["owner_human_id"] if isinstance(workflow, dict) else getattr(workflow, "owner_human_id", None)
        print("\n--- Creating Workflow Run ---")
        workflow_run = test_create_workflow_run(client, workflow_id, owner_agent_id, owner_human_id)
        if workflow_run and ("workflow_run_id" in workflow_run or hasattr(workflow_run, "workflow_run_id")):
            workflow_run_id = workflow_run["workflow_run_id"] if isinstance(workflow_run, dict) else getattr(workflow_run, "workflow_run_id", None)
            print("\n--- Triggering Workflow ---")
            test_trigger_workflow(client, workflow_run_id)
            print("\n--- Sending Message to Default Workflow Conversation ---")
            test_send_message_to_default_conversation(client, workflow_run_id, owner_human_id)
        else:
            print("Workflow run creation failed; skipping further workflow tests.")
    else:
        print("Workflow creation failed; skipping further tests.")
