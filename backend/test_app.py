import urllib.request
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def request(endpoint, data=None, token=None, method='GET'):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            return resp.status, res_data
    except urllib.error.HTTPError as e:
        res_data = json.loads(e.read().decode('utf-8'))
        return e.code, res_data

def run_tests():
    print("[TESTS] Running API Integration Tests for Student Task Planner...\n")

    # 1. Register User 1 (Shubham)
    status, res = request('/auth/register', {
        'username': 'Shubham Singh',
        'email': 'shubham@example.com',
        'password': 'password123'
    }, method='POST')
    assert status == 201, f"Register User 1 failed: {res}"
    token_user1 = res['token']
    print("[OK] Test 1: User 1 Registration & JWT Token generation passed.")

    # 2. Login User 1
    status, res = request('/auth/login', {
        'email': 'shubham@example.com',
        'password': 'password123'
    }, method='POST')
    assert status == 200, f"Login User 1 failed: {res}"
    print("[OK] Test 2: User 1 Login passed.")

    # 3. Create Task 1 for User 1
    status, res = request('/tasks', {
        'title': 'Mathematics Assignment Ch 4',
        'description': 'Solve calculus problem set 1-15',
        'category': 'Mathematics',
        'priority': 'High',
        'status': 'Pending',
        'due_date': '2026-08-30'
    }, token=token_user1, method='POST')
    assert status == 201, f"Create Task failed: {res}"
    task1_id = res['task']['id']
    print(f"[OK] Test 3: Task creation passed (Task ID: {task1_id}).")

    # 4. Create Task 2 for User 1 (Overdue Task)
    status, res = request('/tasks', {
        'title': 'Physics Lab Report',
        'description': 'Circuit analysis lab write-up',
        'category': 'Physics',
        'priority': 'Medium',
        'status': 'In Progress',
        'due_date': '2026-08-20'
    }, token=token_user1, method='POST')
    assert status == 201, f"Create Task 2 failed: {res}"
    print("[OK] Test 4: Overdue task creation passed.")

    # 5. Fetch Tasks for User 1
    status, res = request('/tasks', token=token_user1)
    assert status == 200 and len(res['tasks']) == 2, f"Fetch Tasks failed: {res}"
    print("[OK] Test 5: Fetch user tasks passed.")

    # 6. Fetch Dashboard Summary for User 1
    status, res = request('/tasks/summary', token=token_user1)
    assert status == 200, f"Summary failed: {res}"
    assert res['summary']['total'] == 2 and res['summary']['overdue'] == 1
    print("[OK] Test 6: Dashboard summary metrics passed.")

    # 7. Register User 2 (Alex) - Test User Isolation
    status, res = request('/auth/register', {
        'username': 'Alex Student',
        'email': 'alex@example.com',
        'password': 'password123'
    }, method='POST')
    token_user2 = res['token']

    # User 2 tries to fetch tasks -> Should see 0 tasks!
    status, res = request('/tasks', token=token_user2)
    assert status == 200 and len(res['tasks']) == 0, f"User isolation test failed for User 2: {res}"
    
    # User 2 tries to fetch or edit User 1's task -> Should be 404!
    status, res = request(f"/tasks/{task1_id}", token=token_user2)
    assert status == 404, f"User isolation broken! User 2 accessed User 1's task: {res}"
    print("[OK] Test 7: Strict User Data Isolation passed (User 2 cannot access User 1 tasks).")

    # 8. Update Task Status & Edit Task
    status, res = request(f"/tasks/{task1_id}/status", {'status': 'Completed'}, token=token_user1, method='PATCH')
    assert status == 200 and res['task']['status'] == 'Completed', f"Update status failed: {res}"
    print("[OK] Test 8: Task status update passed.")

    # 9. Delete Task
    status, res = request(f"/tasks/{task1_id}", token=token_user1, method='DELETE')
    assert status == 200, f"Delete task failed: {res}"
    print("[OK] Test 9: Task deletion passed.")

    print("\n[SUCCESS] ALL 9 API INTEGRATION TESTS PASSED SUCCESSFULLY!\n")

if __name__ == '__main__':
    run_tests()
