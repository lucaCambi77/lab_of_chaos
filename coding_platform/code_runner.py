import subprocess
import tempfile
import os
import urllib.request

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


def build_and_run_container(temp_dir):
    subprocess.run(["docker", "build", "-t", DOCKER_IMAGE, temp_dir], check=True)
    subprocess.run(["docker", "run", "--rm", DOCKER_IMAGE], check=True)


def download_junit(lib_dir):
    junit_path = os.path.join(lib_dir, JUNIT_JAR_NAME)
    if not os.path.exists(junit_path):
        print("⬇️  Downloading JUnit...")
        urllib.request.urlretrieve(JUNIT_JAR_URL, junit_path)
    return junit_path


def write_java_files(temp_dir):
    src_dir = os.path.join(temp_dir, "src")
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

with tempfile.TemporaryDirectory() as temp_dir:
    print(f"📂 Using temp dir: {temp_dir}")
    # Prepare dirs
    write_java_files(temp_dir)
    lib_dir = os.path.join(temp_dir, "libs")
    os.makedirs(lib_dir, exist_ok=True)
    download_junit(lib_dir)
    write_dockerfile(temp_dir)
    build_and_run_container(temp_dir)
