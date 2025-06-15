import os
import subprocess
import tempfile
import textwrap
from typing import List, Tuple, Optional

# Simulate database
exercises = {
    1: {
        "python": {
            "func_name": "get_even_numbers",
            "body": """def get_even_numbers(arr):""",
            "test": """
                    import sys
                    from solution import get_even_numbers
                    arr = list(map(int, sys.stdin.read().strip().split()))
                    print(get_even_numbers(arr))
"""
        },
        "java": {
            "func_name": "getEventNumbers",
            "body": """
                import java.util.*;

                class Solution {
                    public List<Integer> getEvenNumbers(int[] a) {}
                }
            }""",
            "test": """
                import java.util.*;
                public class Main {
                    public static void main(String[] args) {
                        Scanner sc = new Scanner(System.in);
                        String[] parts = sc.nextLine().split(" ");
                        int[] a = new int[parts.length];
                        for (int i = 0; i < parts.length; i++) {
                            a[i] = Integer.parseInt(parts[i]);
                        }
                        Solution s = new Solution();
                        List<Integer> result = s.getEvenNumbers(a);
                        System.out.println(result);
                    }
                }"""
        },
        "test_cases": [
            ("1 2 3 4 5 6", "[2, 4, 6]"),
            ("1 3 5 7", "[]"),
            ("0 8 10", "[0, 8, 10]"),
            ("1 2", "[2]"),
            ("4 5", "[4]"),
            ("3 6 9", "[6, 9]")  # <- Invalid on purpose (to trigger fail)
        ]
    }
}


## Java
def run_java_solution(f: List[Tuple[str, str]], main_class: str, tests: List[Tuple[str, str]]) -> Tuple[bool, Tuple[str, str, str] | None]:
    """
    Run Java code with a Main class that tests a user-defined Solution class.
    Exits on the first failure.

    :param f: List of tuples (filename, java_code)
    :param main_class: The Java class that contains the main method to run
    :param tests: List of (stdin_input, expected_output)
    :return: (all_passed, (input, actual_output, expected_output) if failed else None)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write all provided Java files
        for filename, code in f:
            with open(os.path.join(tmpdir, filename), "w") as f:
                f.write(code)

        # Dockerfile
        dockerfile = f"""
        FROM openjdk:21-slim
        WORKDIR /app
        COPY . /app
        RUN javac *.java
        CMD ["tail", "-f", "/dev/null"]
        """
        with open(os.path.join(tmpdir, "Dockerfile"), "w") as f:
            f.write(dockerfile)

        image_name = "java-multi-test"

        cmd = lambda input_str: f"echo '{input_str}' | java " + main_class

        return execute_container(image_name, tmpdir, tests, cmd)


def run_python_solution(f: List[Tuple[str, str]], main_file: str, tests: List[Tuple[str, str]]) -> Tuple[bool, Optional[Tuple[str, str, str]]]:
    """
    Run Java code with a Main class that tests a user-defined Solution class.
    Exits on the first failure.

    :param f: List of tuples (filename, code)
    :param main_file: The python class that contains the main method to run
    :param tests: List of (stdin_input, expected_output)
    :return: (all_passed, (input, actual_output, expected_output) if failed else None)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        for filename, code in f:
            with open(os.path.join(tmpdir, filename), "w") as f:
                f.write(textwrap.dedent(code).strip() + "\n")

        dockerfile = f"""
        FROM python:3.12-slim
        WORKDIR /app
        COPY . /app
        CMD ["tail", "-f", "/dev/null"]
        """
        with open(os.path.join(tmpdir, "Dockerfile"), "w") as f:
            f.write(dockerfile)

        image_name = "python-solution-runner"

        cmd = lambda input_str: f"echo '{input_str}' | python " + main_file

        return execute_container(image_name, tmpdir, tests, cmd)


def execute_container(image_name: str, tmpdir: str, tests: List[Tuple[str, str]], cmd: callable) -> Tuple[bool, Tuple[str, str, str] | None]:
    subprocess.run(["docker", "build", "-t", image_name, tmpdir], check=True)

    container_id = subprocess.check_output(["docker", "run", "-d", image_name]).decode().strip()

    try:
        for input_str, expected_output in tests:
            output = subprocess.check_output(
                ["docker", "exec", container_id, "sh", "-c", cmd(input_str)],
                stderr=subprocess.STDOUT
            ).decode().strip()

            if output != expected_output:
                return False, (input_str, output, expected_output)

    finally:
        subprocess.run(["docker", "rm", "-f", container_id], stdout=subprocess.DEVNULL)

    return True, None


if __name__ == "__main__":
    ex = exercises[1]

    # Java
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
        "language": "java",
    }

    files = [
        ("Solution.java", user_input["code"]),
        ("Main.java", ex[user_input["language"]]["test"])
    ]

    passed, failure = run_java_solution(files, "Main", ex["test_cases"])
    if passed:
        print("✅ All tests passed.")
    else:
        inp, out, exp = failure
        print("❌ Test failed:")
        print(f"  Input:    {inp}")
        print(f"  Expected: {exp}")
        print(f"  Got:      {out}")

    # Python
    user_input = {
        "code": """
            def get_even_numbers(arr):
                return [x for x in arr if x % 2 == 0]
                """,
        "language": "python",
    }

    files = [
        ("solution.py", user_input["code"]),
        ("main.py", ex[user_input["language"]]["test"])
    ]

    passed, failure = run_python_solution(files, "main.py", ex["test_cases"])
    if passed:
        print("✅ All tests passed.")
    else:
        inp, out, exp = failure
        print("❌ Test failed:")
        print(f"  Input:    {inp}")
        print(f"  Expected: {exp}")
        print(f"  Got:      {out}")
