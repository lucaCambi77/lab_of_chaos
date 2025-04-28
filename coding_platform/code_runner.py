import subprocess

# 1. Simulate user-submitted function and test case
user_code = """
def get_even_numbers(arr):
    return [x for x in arr if x % 2 == 0]

import json
print(json.dumps(get_even_numbers([1, 2, 3, 4, 5, 6])))
"""

# 2. Prepare Docker command
docker_cmd = [
    "docker", "run", "--rm", "-i",  # -i keeps STDIN open
    "python:3.10", "python"         # Run Python interpreter
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
