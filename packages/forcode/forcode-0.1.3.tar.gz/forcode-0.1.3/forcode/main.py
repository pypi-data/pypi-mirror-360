import os
import sys
from forgen.tool.node import InputPhase, OutputPhase
from forgen.tool.gen.phase import GenerativePhase
from forgen.tool.gen.tool import GenerativeTool
from openai import OpenAI

SYSTEM_PROMPT = "You are a helpful code summarizer. Generate README content for Python modules."

USER_PROMPT_TEMPLATE = """
You are given the contents of a Python module.
Summarize the purpose and functionality of this module for documentation purposes.

```python
{file_contents}
```

Output the result in markdown format, including a title, description, and any relevant functions or classes.
"""

# ⚒️ Step 2: Build a generative tool using forgen
def build_readme_writer_tool(openai_key=None):
    def structured_prompt_fn(input_data):
        return USER_PROMPT_TEMPLATE.format(**input_data)

    def generation_function(input_data, openai_client=None):
        from forgen.llm.openai_interface.interface import get_chat_completions_response
        return {"output": get_chat_completions_response(
            message_history=[],
            system_content=SYSTEM_PROMPT,
            user_content=structured_prompt_fn(input_data),
            ai_client=OpenAI(api_key=openai_key) if openai_key else openai_client,
            json_response=False
        )}

    input_schema = {"file_contents": str}
    output_schema = {"output": str}

    input_phase = InputPhase(
        input_schema=input_schema,
        output_schema=input_schema,
        code=(lambda x: x)
    )

    generative_phase = GenerativePhase(
        generative_function=generation_function,
        input_schema=input_schema,
        output_schema=output_schema
    )

    output_phase = OutputPhase(
        input_schema=output_schema,
        output_schema=output_schema,
        code=(lambda x: x)
    )

    tool = GenerativeTool(
        input_phase=input_phase,
        generative_phase=generative_phase,
        output_phase=output_phase,
        input_schema=input_schema,
        output_schema=output_schema,
        name="RecursiveReadmeWriter",
        description="Generates markdown README.md files for Python modules."
    )

    tool.use_standard_gen_framework = True
    tool.system_prompt = SYSTEM_PROMPT
    tool.user_prompt_template = USER_PROMPT_TEMPLATE

    return tool

# 🚀 Step 3: Walk the directory and write readmes
def run_recursive_readme_writer(directory: str):
    tool = build_readme_writer_tool()
    written_files = []

    for root, dirs, files in os.walk(directory):
        # Skip virtual environments, build, dist, and hidden dirs
        dirs[:] = [
            d for d in dirs 
            if not d.startswith('.') 
            and d not in {'__pycache__', 'venv', '.venv', 'dist', 'build'}
        ]

        # Only include directories with an __init__.py (i.e. real Python modules)
        if '__init__.py' not in files:
            continue
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    file_contents = f.read()

                input_data = {"file_contents": file_contents}
                result = tool.execute(input_data)
                readme_path = os.path.join(root, "README.md")

                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write((result.get("output") or result.get("summary") or "").rstrip() + "\n")

                written_files.append(readme_path)

    return written_files


def main():
    # Parse CLI args
    cli_args = {k.split('=')[0]: k.split('=')[1] for k in sys.argv[1:] if '=' in k}
    path_args = [arg for arg in sys.argv[1:] if '=' not in arg]
    target_dir = path_args[0] if path_args else os.getcwd()
    openai_key = cli_args.get("openai_key") or os.getenv("OPENAI_API_KEY")

    if not openai_key:
        print("ERROR: No OpenAI API key found. Use env var OPENAI_API_KEY or CLI like: forcode openai_key=sk-...")
        sys.exit(1)

    print(f"Scanning directory: {target_dir}")

    # Pre-scan files
    all_files = []
    total_chars = 0
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if
                   not d.startswith('.') and d not in {'__pycache__', 'venv', '.venv', 'dist', 'build'}]
        if '__init__.py' not in files:
            continue
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        contents = f.read()
                        all_files.append((full_path, contents))
                        total_chars += len(contents)
                except Exception as e:
                    print(f"WARNING: Skipped {full_path}: {e}")

    print(f"Found {len(all_files)} Python files totaling {total_chars:,} characters.")

    confirm = input("Proceed with generation using OpenAI? [y/N] ").strip().lower()
    if confirm != 'y':
        print("Operation aborted.")
        return

    tool = build_readme_writer_tool(openai_key)
    written_files = []

    for path, contents in all_files:
        result = tool.execute({"file_contents": contents})
        readme_path = os.path.join(os.path.dirname(path), "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(result.get("output") or result.get("summary") or "")
        written_files.append(readme_path)

    print("\nSUCCESS: Generated README.md files:")
    for file in written_files:
        print(f"  {file}")

if __name__ == "__main__":
    main()
