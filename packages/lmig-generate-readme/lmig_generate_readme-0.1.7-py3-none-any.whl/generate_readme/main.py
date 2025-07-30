"""
Enhanced README Generator
------------------------
Scans a Python project, builds the project tree and extracts key file contents,
sends them to Liberty GPT AI for analysis, and writes a high-quality README.md.

Features:
- Automatic directory and file scanning with sensible ignores
- Limits size for API context
- Friendly and actionable error reporting
- Step-by-step user feedback with emoji status
- Package dependency self-checking and install
- Designed as a package: importable or CLI-usable

Typical Usage:
    from automate_readme.main import run
    run(token="YOUR_API_KEY", custom_readme="...optional instructions...")

Or, see instructions with:
    python -m automate_readme
"""

import os
import subprocess
import sys
import importlib.util
import platform
from pathlib import Path
from typing import Optional, List

# -- Dependency List for Self-Installation --
REQUIRED_PACKAGES = [
    "certifi",
    "charset-normalizer",
    "python-decouple",
    "requests",
    "urllib3",
]

def list_directory_contents(dir_path: str) -> str:
    """
    Recursively lists the contents of a directory as a tree.

    Args:
        dir_path: Path to directory (string)

    Returns:
        A string representation of the project directory tree.
    """
    if not os.path.exists(dir_path):
        return f"Directory '{dir_path}' does not exist."
    output_lines = []
    for root, dirs, files in os.walk(dir_path):
        level = root.replace(dir_path, '').count(os.sep)
        indent = ' ' * 4 * level
        output_lines.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            output_lines.append(f"{subindent}{f}")
    return '\n'.join(output_lines)

def should_ignore_path(path: Path) -> bool:
    """
    Determines if a given path should be ignored (file or directory).

    Args:
        path: Path object

    Returns:
        True if the path is to be ignored.
    """
    name = path.name
    IGNORE_DIRS = {
        '__pycache__', '.git', 'node_modules', 'venv', 'env', 'build',
        'dist', 'migrations', 'static', '.pytest_cache', '.coverage', 'htmlcov',
        '.vscode', '.idea', 'logs', 'tmp', 'temp', '.DS_Store', 'Thumbs.db'
    }
    IGNORE_FILE_SUFFIXES = {
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib', '.log',
        '.sqlite', '.sqlite3', '.db', '.jpg', '.jpeg', '.png', '.gif',
        '.ico', '.svg', '.pdf', '.zip', '.tar.gz', '.exe', '.bin'
    }
    if path.is_dir() and name in IGNORE_DIRS:
        return True
    if path.is_file():
        for suf in IGNORE_FILE_SUFFIXES:
            if name.endswith(suf):
                return True
    # Ignore hidden files (except some important ones)
    if name.startswith('.') and name not in {'.env.example', '.gitignore', '.dockerignore'}:
        return True
    return False

def extract_file_contents(project_path: str) -> str:
    """
    Extracts the text content of relevant files under project_path.

    Args:
        project_path: Project directory as string

    Returns:
        Concatenated file data, each section labeled with the relative path.
    """
    INCLUDE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.sass',
        '.md', '.txt', '.yml', '.yaml', '.json', '.xml', '.sql', '.sh', '.bat',
        '.dockerfile', '.gitignore', '.env.example', '.conf', '.ini', '.toml',
        '.config'
    }
    # Also include these filenames (no extension)
    INCLUDE_FILENAMES = {
        'Dockerfile', 'Makefile', 'requirements.txt', 'package.json',
        'setup.py', 'pyproject.toml', 'README', 'LICENSE'
    }
    try:
        print(f"📄 Extracting file contents from: {project_path}")
        project_path = Path(project_path)
        all_content = []
        file_count = 0
        for file_path in project_path.rglob("*"):
            if not file_path.is_file() or should_ignore_path(file_path):
                continue
            if file_path.suffix.lower() in INCLUDE_EXTENSIONS or file_path.name in INCLUDE_FILENAMES:
                try:
                    relative_path = file_path.relative_to(project_path)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    # Truncate very large files
                    if len(content) > 50000:
                        content = content[:50000] + "\n... [File truncated - too large] ..."
                    all_content.append(f"\n{'='*80}\nFILE: {relative_path}\n{'='*80}\n{content}")
                    file_count += 1
                    if file_count >= 100:
                        all_content.append("\n... [Stopped after 100 files to prevent overwhelming the API] ...")
                        break
                except Exception as e:
                    print(f"⚠️  Could not read {file_path}: {e}")
                    continue
        print(f"💾 File contents extracted ({file_count} files).")
        return '\n'.join(all_content)
    except Exception as e:
        print(f"❌ Error extracting file contents: {e}")
        return f"Error extracting file contents: {e}"

def create_gpt_prompt(tree: str, file_contents: str, custom_readme: Optional[str] = None) -> str:
    """
    Creates the prompt text to send to Liberty GPT.

    Args:
        tree: Project structure as string
        file_contents: All extracted file content
        custom_readme: Optional custom readme template

    Returns:
        Formatted prompt string
    """
    max_tree_length = 5000
    max_content_length = 100000
    if len(tree) > max_tree_length:
        tree = tree[:max_tree_length] + "\n... [Tree truncated] ..."
    if len(file_contents) > max_content_length:
        file_contents = file_contents[:max_content_length] + "\n... [Content truncated] ..."
    if not custom_readme:
        instructions = """1. Project title and clear description
2. Key features and functionality
3. Technology stack used (according to the file contents)
4. Installation instructions
5. Usage examples and documentation
6. Project structure overview
7. Configuration details (if applicable)
8. Contributing guidelines (if applicable)
9. License information (if applicable)"""
    else:
        instructions = custom_readme
    return f"""Write a comprehensive README.md file for this project.

PROJECT STRUCTURE:
{tree}

FILE CONTENTS:
{file_contents}


Create a professional README.md with the following sections:
{instructions}

Analyze the code structure and dependencies to provide accurate setup instructions.
Make the README informative, well-structured, and professional.
Use appropriate markdown formatting with headers, code blocks, and lists.

Return only the README content in markdown format - no additional text or wrapping.
"""

def write_readme_to_repo(content: str, project_path: Path = Path.cwd()) -> bool:
    """
    Writes the README content to README.md in the specified project path.

    Args:
        content: The markdown to write
        project_path: Path object for the project directory

    Returns:
        True on success, False on error.
    """
    try:
        readme_path = project_path / "README.md"
        print(f"✏️ Writing README.md to: {readme_path}")
        lines = content.splitlines()
        # Remove leading/trailing markdown fences if present
        if lines and lines[0].strip() == '```markdown':
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        cleaned_content = "\n".join(lines)
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"✅ README.md written successfully.")
        return True
    except Exception as e:
        print(f"❌ Error writing README to repository: {e}")
        return False

def chat_with_liberty_gpt_for_readme(token: str, prompt: str) -> str:
    """
    Calls the Liberty GPT API to get a README based on the prompt.

    Args:
        token: API token for Liberty GPT
        prompt: Prompt text

    Returns:
        The generated README content as a string (may include markdown fences).
    """
    try:
        # Dynamically import from sibling request.py (in the package)
        from .request import chat_with_liberty_gpt
        response = chat_with_liberty_gpt(token, prompt)
        return str(response)
    except ImportError:
        msg = (
            "❌ Could not import the Liberty GPT API client. "
            "Please ensure 'request.py' exists in the package and contains 'chat_with_liberty_gpt(token, prompt)'."
        )
        print(msg)
        return f"# README Generation Failed\n\nError: Could not import API client."
    except Exception as e:
        print(f"❌ Error calling Liberty GPT API: {e}")
        return f"# README Generation Failed\n\nError: {e}"

def main(token: str, custom_readme: Optional[str] = None) -> bool:
    """
    Main entrypoint for README generation process.

    Args:
        token: API access token (from Liberty GPT)
        custom_readme: Optional custom readme instructions (markdown string)

    Returns:
        True if successful, False otherwise.
    """
    try:
        project_path = Path.cwd()
        print(f"🚀 Starting README generation for: {project_path.resolve()}")
        # Step 1: Build tree
        tree_content = list_directory_contents(".")
        # Step 2: Extract code and config
        file_contents = extract_file_contents(str(project_path))
        # Step 3: Compose prompt
        prompt = create_gpt_prompt(tree_content, file_contents, custom_readme)
        print("🤖 Creating README with Liberty GPT...")
        ai_response = chat_with_liberty_gpt_for_readme(token, prompt)
        # Step 4: Write output file
        if not write_readme_to_repo(ai_response, project_path):
            return False
        print(f"🎉 README generation completed successfully! See: {project_path / 'README.md'}")
        return True
    except Exception as e:
        print(f"❌ Error in main process: {e}")
        return False

def is_package_installed(pkg_name: str) -> bool:
    """
    Checks if a Python package is installed.
    """
    return importlib.util.find_spec(pkg_name) is not None

def install_package(pkg_name: str):
    """
    Installs the package using pip. Exits on failure.
    """
    print(f"📦 Installing missing package: {pkg_name}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {pkg_name}: {e}")
        sys.exit(1)

def print_instructions():
    """
    Prints instructions for first-time users.
    """
    instructions = r"""
╔═════════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   🚀 Welcome to the Cortex Liberty GPT Enhanced README Generator!              ║
║                                                                               ║
║   Quick Setup Instructions:                                                   ║
║                                                                               ║
║   1. OBTAIN YOUR API ACCESS KEY:                                              ║
║      - Visit: https://cortex-lab.lmig.com/me                                  ║
║      - Register or log in, then copy your API access key.                     ║
║                                                                               ║
║   2. CREATE THE GENERATE SCRIPT:                                              ║
║      - In your project root, create a file named: generate_readme.py          ║
║      - Add the following content:                                             ║
║            from automate_readme.main import run                               ║
║            run(token="YOUR_API_KEY")                                          ║
║                                                                               ║
║   3. RUN THE GENERATOR:                                                       ║
║      - In your terminal, run:                                                 ║
║            python generate_readme.py                                          ║
║                                                                               ║
║   NOTES:                                                                      ║
║      • Ensure your .env file is present in the project root.                  ║
║      • The script will guide you through the README generation process.       ║
║      • For support or updates, visit: [Documentation or Support Link]         ║
║                                                                               ║
╚═════════════════════════════════════════════════════════════════════════════════╝
"""
    print(instructions)

def run(token: Optional[str] = None, custom_readme: Optional[str] = None):
    """
    Package main entrypoint. Installs requirements, prints OS, and runs the main process.

    Args:
        token: The Liberty GPT API access token (required).
        custom_readme: Optional custom README instructions.

    Side Effects:
        Exits program with status 1 on fatal errors.
    """
    current_os = platform.system()
    print(f"🖥️  Detected Operating System: {current_os}")
    # Install missing packages first
    for package in REQUIRED_PACKAGES:
        if not is_package_installed(package):
            install_package(package)
        else:
            print(f"✅ Package already installed: {package}")
    if not token:
        print("❗ Error: No API token provided. You must provide a valid API token to generate a README.")
        print_instructions()
        sys.exit(1)
    success = main(token, custom_readme)
    if not success:
        print("❌ The main function reported failure.")
        sys.exit(1)

