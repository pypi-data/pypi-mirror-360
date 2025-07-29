from pathlib import Path
import shutil
import tempfile
import subprocess


def run_c_program(program: str, stdin: str|None = None) -> str:
    """
    Executes a C program in a sandboxed container.
    """
    # Check if podman is available
    if not shutil.which("podman"):
        raise Exception("podman command not found. Please install podman.")
    
    # Create temporary /tmp/c-runners directory
    runners_dir = Path("/tmp/c-runners")
    runners_dir.mkdir(exist_ok=True)
    
    # Create Dockerfile
    dockerfile_path = runners_dir / "Dockerfile"
    dockerfile_path.write_text("FROM alpine\nRUN apk add build-base")
    
    # Build the container image
    print("Preparing container...")
    build_cmd = ["podman", "build", "-t", "alpine-build", "-f", str(dockerfile_path)]
    try:
        result = subprocess.run(build_cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to build container: stdout={e.stdout}, stderr={e.stderr}")
    
    # Create temporary directory for this execution
    with tempfile.TemporaryDirectory(dir=runners_dir) as temp_dir:
        temp_path = Path(temp_dir)
        
        # Save program to program.c
        program_file = temp_path / "program.c"
        program_file.write_text(program)
        
        # Save stdin to stdin.txt (or empty file if None)
        stdin_file = temp_path / "stdin.txt"
        stdin_file.write_text(stdin if stdin is not None else "")
        
        # Run the container with the compilation and execution command
        container_cmd = [
            "podman", "run", "--rm",
            "-v", f"{temp_path}:/app:Z",
            "-w", "/app",
            "alpine-build",
            "sh", "-c",
            "gcc program.c -o program && cat stdin.txt | ./program"
        ]
        
        result = subprocess.run(container_cmd, capture_output=True, text=True)
        
        # Return result as JSON string
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    
    

if __name__ == "__main__":
    code = """
#include <stdio.h>

int main(int argc, char** argv)
{
    printf("Hello world :)\\n");
    return 0;
}
"""
    print()
    print(code)
    print()
    print(run_c_program(code))
