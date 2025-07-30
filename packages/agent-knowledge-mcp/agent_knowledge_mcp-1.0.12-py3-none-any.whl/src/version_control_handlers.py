"""
Version Control tool handlers for Git and SVN.
"""
import subprocess
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import mcp.types as types
from .config import load_config


def get_vcs_type() -> Optional[str]:
    """Get version control type from config."""
    config = load_config()
    vc_config = config.get("version_control", {})
    if not vc_config.get("enabled", False):
        return None
    return vc_config.get("type", "git")


def get_base_directory() -> Path:
    """Get base directory from config."""
    config = load_config()
    base_directory = config.get("security", {}).get("allowed_base_directory", ".")
    return Path(base_directory).resolve()


def run_command(cmd: List[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run command in specified directory."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True
    )


async def handle_setup_version_control(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle setup_version_control tool."""
    try:
        base_path = get_base_directory()
        vcs_type = arguments.get("vcs_type") or get_vcs_type() or "git"
        force = arguments.get("force", False)
        initial_commit = arguments.get("initial_commit", True)
        
        # Check if VCS is installed
        try:
            run_command([vcs_type, "--version"], base_path)
        except (subprocess.CalledProcessError, FileNotFoundError):
            install_cmd = {
                "git": "git (usually pre-installed on macOS/Linux)",
                "svn": "brew install subversion (on macOS)"
            }
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Error: {vcs_type.upper()} is not installed.\n"
                         f"Please install: {install_cmd.get(vcs_type, vcs_type)}"
                )
            ]
        
        # Check if VCS already exists
        vcs_dir = base_path / f".{vcs_type}"
        if vcs_dir.exists() and not force:
            return [
                types.TextContent(
                    type="text",
                    text=f"⚠️  {vcs_type.upper()} repository already exists in {base_path}\n"
                         "Use force=true to reinitialize"
                )
            ]
        
        message = f"🚀 Setting up {vcs_type.upper()} in {base_path}\n\n"
        
        if vcs_type == "git":
            message += await _setup_git(base_path, force, initial_commit)
        elif vcs_type == "svn":
            message += await _setup_svn(base_path, force, initial_commit)
        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Error: Unsupported VCS type: {vcs_type}"
                )
            ]
        
        # Update config
        config = load_config()
        config.setdefault("version_control", {})
        config["version_control"]["enabled"] = True
        config["version_control"]["type"] = vcs_type
        
        # Save config
        import json
        config_path = base_path.parent / "src" / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        message += f"\n✅ Updated config to use {vcs_type.upper()}"
        
        return [
            types.TextContent(
                type="text",
                text=f"🎉 {vcs_type.upper()} setup completed successfully!\n\n{message}"
            )
        ]
        
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error setting up version control: {str(e)}"
            )
        ]


async def _setup_git(base_path: Path, force: bool, initial_commit: bool) -> str:
    """Setup Git repository."""
    message = ""
    
    # Remove existing .git if force
    git_dir = base_path / ".git"
    if git_dir.exists() and force:
        run_command(["rm", "-rf", str(git_dir)], base_path)
        message += "✅ Removed existing Git repository\n"
    
    # Initialize Git repository
    run_command(["git", "init"], base_path)
    message += "✅ Initialized Git repository\n"
    
    # Set user config if not set globally
    try:
        run_command(["git", "config", "user.name"], base_path)
    except subprocess.CalledProcessError:
        run_command(["git", "config", "user.name", "Knowledge Base"], base_path)
        run_command(["git", "config", "user.email", "knowledge@base.local"], base_path)
        message += "✅ Set Git user configuration\n"
    
    # Create .gitignore
    gitignore_path = base_path / ".gitignore"
    gitignore_content = """# Temporary files
*.tmp
*.temp
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Editor files
.vscode/
.idea/
"""
    gitignore_path.write_text(gitignore_content)
    message += "✅ Created .gitignore\n"
    
    if initial_commit:
        # Add all files
        run_command(["git", "add", "."], base_path)
        
        # Initial commit
        run_command(["git", "commit", "-m", "Initial commit - setup knowledge base"], base_path)
        message += "✅ Created initial commit\n"
        
        # Show status
        result = run_command(["git", "status", "--porcelain"], base_path)
        if result.stdout.strip():
            message += f"📝 Untracked files remain: {len(result.stdout.strip().split())}\n"
        else:
            message += "📝 Working directory is clean\n"
    
    return message


async def _setup_svn(base_path: Path, force: bool, initial_commit: bool) -> str:
    """Setup SVN repository."""
    message = ""
    
    # Create repository directory
    repo_path = base_path.parent / ".svn_repo"
    if repo_path.exists() and force:
        run_command(["rm", "-rf", str(repo_path)], base_path)
    
    if not repo_path.exists():
        run_command(["svnadmin", "create", str(repo_path)], base_path)
        message += f"✅ Created SVN repository at {repo_path}\n"
    
    # Remove existing .svn if force
    svn_dir = base_path / ".svn"
    if svn_dir.exists() and force:
        run_command(["rm", "-rf", str(svn_dir)], base_path)
        message += "✅ Removed existing SVN working copy\n"
    
    # Checkout working copy
    repo_url = f"file://{repo_path}"
    run_command(["svn", "checkout", repo_url, ".", "--force"], base_path)
    message += f"✅ Checked out working copy from {repo_url}\n"
    
    if initial_commit:
        # Add all files except .svn
        files_to_add = []
        for item in base_path.iterdir():
            if not item.name.startswith('.') and item.is_file():
                files_to_add.append(item.name)
        
        if files_to_add:
            run_command(["svn", "add"] + files_to_add, base_path)
            run_command(["svn", "commit", "-m", "Initial commit - setup knowledge base"], base_path)
            message += f"✅ Added and committed {len(files_to_add)} files\n"
        else:
            message += "📝 No files found for initial commit\n"
    
    return message


async def handle_commit_file(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle commit_file tool."""
    try:
        base_path = get_base_directory()
        vcs_type = get_vcs_type()
        
        if not vcs_type:
            return [
                types.TextContent(
                    type="text",
                    text="❌ Error: Version control is not enabled in config"
                )
            ]
        
        file_path = arguments.get("file_path")
        message = arguments.get("message")
        add_if_new = arguments.get("add_if_new", True)
        
        if not file_path or not message:
            return [
                types.TextContent(
                    type="text",
                    text="❌ Error: file_path and message are required"
                )
            ]
        
        # Check if file exists
        full_file_path = base_path / file_path
        if not full_file_path.exists():
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Error: File {file_path} does not exist"
                )
            ]
        
        if vcs_type == "git":
            return await _commit_file_git(base_path, file_path, message, add_if_new)
        elif vcs_type == "svn":
            return await _commit_file_svn(base_path, file_path, message, add_if_new)
        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Error: Unsupported VCS type: {vcs_type}"
                )
            ]
            
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error committing file: {str(e)}"
            )
        ]


async def _commit_file_git(base_path: Path, file_path: str, message: str, add_if_new: bool) -> List[types.TextContent]:
    """Commit file using Git."""
    status_message = ""
    
    # Check file status
    result = run_command(["git", "status", "--porcelain", file_path], base_path)
    status = result.stdout.strip()
    
    # Add file if needed
    if status.startswith("??") and add_if_new:
        run_command(["git", "add", file_path], base_path)
        status_message += f"✅ Added {file_path} to Git\n"
    elif status.startswith(("M", "A", "D")):
        run_command(["git", "add", file_path], base_path)
        status_message += f"✅ Staged changes for {file_path}\n"
    
    # Commit
    run_command(["git", "commit", "-m", message, file_path], base_path)
    
    # Get commit hash
    result = run_command(["git", "rev-parse", "HEAD"], base_path)
    commit_hash = result.stdout.strip()[:8]
    
    return [
        types.TextContent(
            type="text",
            text=f"{status_message}✅ File committed successfully!\n"
                 f"File: {file_path}\n"
                 f"Message: {message}\n"
                 f"Commit: {commit_hash}"
        )
    ]


async def _commit_file_svn(base_path: Path, file_path: str, message: str, add_if_new: bool) -> List[types.TextContent]:
    """Commit file using SVN."""
    status_message = ""
    
    # Check file status
    result = run_command(["svn", "status", file_path], base_path)
    status = result.stdout.strip()
    
    # Add file if needed
    if status.startswith("?") and add_if_new:
        run_command(["svn", "add", file_path], base_path)
        status_message += f"✅ Added {file_path} to SVN\n"
    
    # Commit
    result = run_command(["svn", "commit", file_path, "-m", message], base_path)
    
    return [
        types.TextContent(
            type="text",
            text=f"{status_message}✅ File committed successfully!\n"
                 f"File: {file_path}\n"
                 f"Message: {message}\n\n"
                 f"SVN Output:\n{result.stdout}"
        )
    ]


async def handle_get_previous_file_version(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle get_previous_file_version tool."""
    try:
        base_path = get_base_directory()
        vcs_type = get_vcs_type()
        
        if not vcs_type:
            return [
                types.TextContent(
                    type="text",
                    text="❌ Error: Version control is not enabled in config"
                )
            ]
        
        file_path = arguments.get("file_path")
        commits_back = arguments.get("commits_back", 1)
        
        if not file_path:
            return [
                types.TextContent(
                    type="text",
                    text="❌ Error: file_path is required"
                )
            ]
        
        if vcs_type == "git":
            return await _get_previous_file_git(base_path, file_path, commits_back)
        elif vcs_type == "svn":
            return await _get_previous_file_svn(base_path, file_path, commits_back)
        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Error: Unsupported VCS type: {vcs_type}"
                )
            ]
            
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Error getting previous file version: {str(e)}"
            )
        ]


async def _get_previous_file_git(base_path: Path, file_path: str, commits_back: int) -> List[types.TextContent]:
    """Get previous file version using Git."""
    try:
        # Get commit hash
        result = run_command(["git", "log", "--oneline", "-n", str(commits_back + 1), file_path], base_path)
        commits = result.stdout.strip().split('\n')
        
        if len(commits) <= commits_back:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Error: File {file_path} doesn't have {commits_back} previous commits"
                )
            ]
        
        target_commit = commits[commits_back].split()[0]
        
        # Get file content from that commit
        result = run_command(["git", "show", f"{target_commit}:{file_path}"], base_path)
        content = result.stdout
        
        # Get commit info
        result = run_command(["git", "show", "--no-patch", "--format=%H %s %an %ad", target_commit], base_path)
        commit_info = result.stdout.strip()
        
        return [
            types.TextContent(
                type="text",
                text=f"📄 Previous version of {file_path} ({commits_back} commits back):\n"
                     f"Commit: {commit_info}\n"
                     f"{'='*60}\n\n{content}"
            )
        ]
        
    except subprocess.CalledProcessError as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ Git error: {e.stderr or e.stdout or str(e)}"
            )
        ]


async def _get_previous_file_svn(base_path: Path, file_path: str, commits_back: int) -> List[types.TextContent]:
    """Get previous file version using SVN."""
    try:
        # Get current revision
        result = run_command(["svn", "info", file_path], base_path)
        for line in result.stdout.split('\n'):
            if line.startswith('Revision:'):
                current_rev = int(line.split()[1])
                break
        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Error: Could not determine current revision for {file_path}"
                )
            ]
        
        target_rev = current_rev - commits_back
        if target_rev < 1:
            return [
                types.TextContent(
                    type="text",
                    text=f"❌ Error: File {file_path} doesn't have {commits_back} previous revisions"
                )
            ]
        
        # Get file content from that revision
        result = run_command(["svn", "cat", "-r", str(target_rev), file_path], base_path)
        content = result.stdout
        
        # Get commit info
        result = run_command(["svn", "log", "-r", str(target_rev), "-v"], base_path)
        commit_info = result.stdout.strip()
        
        return [
            types.TextContent(
                type="text",
                text=f"📄 Previous version of {file_path} (revision {target_rev}):\n"
                     f"Commit info:\n{commit_info}\n"
                     f"{'='*60}\n\n{content}"
            )
        ]
        
    except subprocess.CalledProcessError as e:
        return [
            types.TextContent(
                type="text",
                text=f"❌ SVN error: {e.stderr or e.stdout or str(e)}"
            )
        ]
