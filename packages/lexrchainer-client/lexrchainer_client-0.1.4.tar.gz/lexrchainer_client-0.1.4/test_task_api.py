import os
from dotenv import load_dotenv
from lexrchainer_client import ClientInterface, models
import traceback
import uuid
from datetime import datetime, timedelta

def setup_client():
    os.environ["LEXRCHAINER_API_KEY"] = "hF32ac2435DcimhDt8AETBxuVrKwPy7kBoarFD8deWc"
    os.environ["LEXRCHAINER_API_URL"] = "http://localhost:8000"
    load_dotenv()
    return ClientInterface()

def to_isoformat_dict(model):
    # Recursively convert all datetime fields in a dict to isoformat strings
    def convert(obj):
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(i) for i in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            # Convert timedelta to total seconds or string
            return str(obj.total_seconds())
        else:
            return obj
    return convert(model.model_dump())

def test_create_tasklist(client):
    try:
        tasklist_name = f"test_tasklist_{uuid.uuid4().hex[:8]}"
        deadline = datetime.now() + timedelta(days=7)
        owner = "test_owner"
        actor = models.TaskActor(name="test_actor")
        tasklist_req = models.TaskListCreateRequest(
            name=tasklist_name,
            deadline=deadline,
            owner=owner,
            actors=[actor],
            tasks=[]
        )
        payload = to_isoformat_dict(tasklist_req)
        tasklist = client.create_tasklist(models.TaskListCreateRequest(**payload))
        print(f"TaskList created: {tasklist}")
        return tasklist
    except Exception as e:
        traceback.print_exc()
        print(f"Error creating tasklist: {e}")
        return None

def test_create_task(client, tasklist_id):
    try:
        task_name = f"test_task_{uuid.uuid4().hex[:8]}"
        deadline = datetime.now() + timedelta(days=3)
        actor = models.TaskActor(name="test_actor")
        task_req = models.TaskCreateRequest(
            tasklist_id=tasklist_id,
            task_name=task_name,
            task_description="A test task.",
            deadline=deadline,
            actor=actor
        )
        payload = to_isoformat_dict(task_req)
        task = client.create_task(models.TaskCreateRequest(**payload))
        print(f"Task created: {task}")
        return task
    except Exception as e:
        traceback.print_exc()
        print(f"Error creating task: {e}")
        return None

def test_get_task(client, task_id):
    try:
        task = client.get_task(task_id)
        print(f"Fetched task: {task}")
        return task
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching task: {e}")
        return None

def test_update_task(client, task_id):
    try:
        update_req = models.TaskUpdateRequest(task_name=f"updated_{uuid.uuid4().hex[:6]}")
        payload = to_isoformat_dict(update_req)
        task = client.update_task(task_id, models.TaskUpdateRequest(**payload))
        print(f"Updated task: {task}")
        return task
    except Exception as e:
        traceback.print_exc()
        print(f"Error updating task: {e}")
        return None

def test_get_all_tasks(client, tasklist_id):
    try:
        tasks = client.get_all_tasks(tasklist_id)
        print(f"All tasks in tasklist: {tasks}")
        return tasks
    except Exception as e:
        traceback.print_exc()
        print(f"Error getting all tasks: {e}")
        return None

def test_delete_task(client, task_id):
    try:
        client.delete_task(task_id)
        print(f"Deleted task with id: {task_id}")
        return True
    except Exception as e:
        traceback.print_exc()
        print(f"Error deleting task: {e}")
        return False

if __name__ == "__main__":
    client = setup_client()
    print("\n--- Creating TaskList ---")
    tasklist = test_create_tasklist(client)
    if tasklist and hasattr(tasklist, "tasklist_id"):
        tasklist_id = tasklist.tasklist_id
        print("\n--- Creating Task ---")
        task = test_create_task(client, tasklist_id)
        if task and hasattr(task, "task_id"):
            task_id = task.task_id
            print("\n--- Getting Task ---")
            test_get_task(client, task_id)
            print("\n--- Updating Task ---")
            test_update_task(client, task_id)
            print("\n--- Listing All Tasks in TaskList ---")
            test_get_all_tasks(client, tasklist_id)
            print("\n--- Deleting Task ---")
            test_delete_task(client, task_id)
        else:
            print("Task creation failed; skipping further task tests.")
    else:
        print("TaskList creation failed; skipping further tests.")
