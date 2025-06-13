import subprocess
import tempfile
import os
import urllib.request
import re

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
        },
        "java": {
            "func_name": "getEventNumbers",
            "body": """
                import java.util.*;
                
                class Solution {
                    public List<Integer> getEvenNumbers(int[] a) {}
                }
            }""",
            "test_cases": {
                "MainTest.java": """
                import org.junit.jupiter.api.Test;
                import static org.junit.jupiter.api.Assertions.*;
                import java.util.*;

                public class MainTest {
                    Solution s = new Solution();

                    @Test
                    public void test1() {
                        assertEquals(List.of(2,4,6), s.getEvenNumbers(new int[]{1, 2, 3, 4, 5, 6}));
                    }
                }
                """
            }
        }
    }
}

## Python
user_input = {
    "code": """def get_even_numbers(arr):
                return [x for x in arr if x % 2 == 0]
""",
    "id": 1,
    "language": "python",
}

ex = exercises[user_input["id"]][user_input["language"]]

# User submitted solution as a function
user_sol = user_input["code"]

# 1. Build the Python script to be executed inside Docker
user_code = f"""
{user_sol}

for test_id, test_data in {ex["test_cases"]}.items():
    result = {ex["func_name"]}(test_data['input'])
    expected = test_data['expected']
    assert result == expected, f"Test {{test_id}} failed: expected {{expected}}, got {{result}}"
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


def parse_failures_python(out):
    messages = []
    matches = re.finditer(r"AssertionError:\s*(Test \d+)\sfailed:\s*(.+)", out)
    for match in matches:
        test_name, message = match.groups()
        messages.append({"test": test_name, "message": message})

    return messages


# 4. Output the result
print("=== OUTPUT ===")

if result.stderr:
    print("=== ERROR ===")
    print(parse_failures_python(result.stderr.strip()))
else:
    print("All tests passed!")

## Java
DOCKER_IMAGE = "junit_java_runner"
JUNIT_JAR_URL = "https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.10.1/junit-platform-console-standalone-1.10.1.jar"
JUNIT_JAR_NAME = "junit-platform-console-standalone-1.10.1.jar"


def write_dockerfile(temp_dir):
    dockerfile_content = f"""
FROM openjdk:17-slim
WORKDIR /app
COPY . .
RUN mkdir -p out

# Compile all Java files
RUN javac -cp libs/{JUNIT_JAR_NAME} src/*.java -d out

# Run tests with JUnit Console
CMD ["java", "-jar", "libs/{JUNIT_JAR_NAME}", "--class-path=out", "--scan-class-path"]
"""
    with open(os.path.join(temp_dir, "Dockerfile"), "w") as f:
        f.write(dockerfile_content)


def build_and_run_container(temp):
    subprocess.run(["docker", "build", "-t", DOCKER_IMAGE, temp], check=True)
    return subprocess.run(
        ["docker", "run", "--rm", DOCKER_IMAGE],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    ).stdout.strip()


def download_junit(lib):
    junit_path = os.path.join(lib, JUNIT_JAR_NAME)
    if not os.path.exists(junit_path):
        print("⬇️  Downloading JUnit...")
        urllib.request.urlretrieve(JUNIT_JAR_URL, junit_path)
    return junit_path


def write_java_files(temp):
    src_dir = os.path.join(temp, "src")
    os.makedirs(src_dir, exist_ok=True)
    for filename, code in java_files.items():
        with open(os.path.join(src_dir, filename), "w") as f:
            f.write(code)


user_input = {
    "code": """
                import java.util.*;
                
                class Solution {
                    public List<Integer> getEvenNumbers(int[] a) {
                        List<Integer> l = new ArrayList<>();
                        for(int v : a) {
                            if(v % 2 == 0) {
                                l.add(v);
                            }
                        }
                        return l;
                }
            }""",
    "id": 1,
    "language": "java",
}

ex = exercises[user_input["id"]][user_input["language"]]

java_files = {"Solution.java": user_input["code"], **ex["test_cases"]}


def parse_failures_java(test_output):
    # Regex to find failure blocks
    results = []
    failure_blocks = re.findall(r"Failures \(\d+\):\n(.*?)(?=\n\S|$)", test_output, re.DOTALL)

    for block in failure_blocks:
        # Extract test class and method
        test_match = re.search(r"JUnit Jupiter:([\w$]+):([\w$]+)", block)
        test_name = f"{test_match.group(2)}" if test_match else "UnknownTest"

        # Extract failure message
        expected_actual_match = re.search(r"expected:\s*<(.+?)>\s*but was:\s*<(.+?)>", block)
        if expected_actual_match:
            expected = expected_actual_match.group(1)
            actual = expected_actual_match.group(2)
            message = f"expected <{expected}> but was <{actual}>"
            results.append({"test": test_name, "message": message})

    return results


with tempfile.TemporaryDirectory() as temp_dir:
    print(f"📂 Using temp dir: {temp_dir}")
    # Prepare dirs
    write_java_files(temp_dir)
    lib_dir = os.path.join(temp_dir, "libs")
    os.makedirs(lib_dir, exist_ok=True)
    download_junit(lib_dir)
    write_dockerfile(temp_dir)
    output = build_and_run_container(temp_dir)
    failures = parse_failures_java(output)
    print("=== OUTPUT ===")
    if failures:
        print(failures)
    else:
        print("All tests passed")
