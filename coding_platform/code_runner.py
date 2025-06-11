import subprocess

user_input = {
    "code": """def get_even_numbers(arr):
                return [x for x in arr if x % 2 == 0]
""",
    "id": 1,
    "language": "python",
}

# Simulate database
exercises = {
    1: {
        "python": {
            "func_name": "get_even_numbers",
            "body": """def get_even_numbers(arr):""",
            "test_cases": {
                1: {"input": [1, 2, 3, 4, 5, 6], "expected": [2, 4, 6]},
                2: {"input": [1, 3, 5], "expected": []},
            }
        }
    }
}

ex = exercises[user_input["id"]][user_input["language"]]

# User submitted solution as a function
user_sol = user_input["code"]

# 1. Build the Python script to be executed inside Docker
user_code = f"""
{user_sol}

tests = {ex["test_cases"]}
func_name = {ex["func_name"]}

for test_id, test_data in tests.items():
    result = func_name(test_data['input'])
    expected = test_data['expected']
    assert result == expected, f"Test {{test_id}} failed: expected {{expected}}, got {{result}}"

print("All tests passed!")
"""

# 2. Prepare Docker command
docker_cmd = [
    "docker", "run", "--rm", "-i",  # -i keeps STDIN open
    "python:3.10", "python"
]

# 3. Run the command, piping in the code via stdin
result = subprocess.run(
    docker_cmd,
    input=user_code,
    capture_output=True,
    text=True
)

# 4. Output the result
print("=== OUTPUT ===")
print(result.stdout.strip())

if result.stderr:
    print("=== ERROR ===")
    print(result.stderr.strip())
