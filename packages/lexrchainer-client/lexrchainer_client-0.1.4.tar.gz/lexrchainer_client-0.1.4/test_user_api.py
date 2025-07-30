import os
from dotenv import load_dotenv
from lexrchainer_client import ClientInterface, models
import traceback
import uuid

def setup_client():
    # Set API key for authentication
    os.environ["LEXRCHAINER_API_KEY"] = "hF32ac2435DcimhDt8AETBxuVrKwPy7kBoarFD8deWc"
    # Optionally set API URL if needed, e.g.:
    os.environ["LEXRCHAINER_API_URL"] = "http://localhost:8000"
    load_dotenv()
    return ClientInterface()

def test_create_user(client):
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    user_data = models.UserCreate(
        username=username,
        email=f"{username}@example.com",
        phone=f"+91123456{uuid.uuid4().hex[:4]}",
        user_type=models.UserType.HUMAN
    )
    try:
        user = client.create_user(user_data)
        print(f"User created: {user}")
        return user
    except Exception as e:
        traceback.print_exc()
        print(f"Error creating user: {e}")
        return None

def test_get_user(client, user_id):
    try:
        user = client.get_user(user_id)
        print(f"Fetched user: {user}")
        return user
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching user: {e}")
        return None

def test_update_user(client, user_id):
    try:
        update_data = {"username": f"updated_{uuid.uuid4().hex[:6]}"}
        user = client.update_user(user_id, update_data)
        print(f"Updated user: {user}")
        return user
    except Exception as e:
        traceback.print_exc()
        print(f"Error updating user: {e}")
        return None

def test_list_users(client):
    try:
        users = client.list_users()
        print(f"User list: {users}")
        return users
    except Exception as e:
        traceback.print_exc()
        print(f"Error listing users: {e}")
        return None

def test_get_current_user(client):
    try:
        user = client.get_current_user()
        print(f"Current user: {user}")
        return user
    except Exception as e:
        traceback.print_exc()
        print(f"Error getting current user: {e}")
        return None

def test_delete_user(client, user_id):
    try:
        client.delete_user(user_id)
        print(f"Deleted user with id: {user_id}")
        return True
    except Exception as e:
        traceback.print_exc()
        print(f"Error deleting user: {e}")
        return False

if __name__ == "__main__":
    client = setup_client()
    print("\n--- Creating User ---")
    user = test_create_user(client)
    if user and "id" in user:
        user_id = user["id"]
        print("\n--- Getting User by ID ---")
        test_get_user(client, user_id)
        print("\n--- Updating User ---")
        test_update_user(client, user_id)
        print("\n--- Listing Users ---")
        test_list_users(client)
        print("\n--- Getting Current User ---")
        test_get_current_user(client)
        print("\n--- Deleting User ---")
        test_delete_user(client, user_id)
    else:
        print("User creation failed; skipping further tests.")
