# Git Checkpoints

🔄 **Automatic Git checkpoints with zero configuration**

Git Checkpoints creates automatic snapshots of your work every 5 minutes when you're in a virtual environment. No manual commits, no clutter in your commit history, just seamless backup of your work-in-progress.

## Features

- ✅ **Zero Configuration**: One command setup, then forget about it
- 🤖 **Automatic**: Creates checkpoints every 5 minutes when virtual environment is active
- 🏷️ **Tagged**: Uses Git tags, not commits, so your history stays clean
- 🔄 **Team Sync**: Automatically pushes checkpoint tags to share with your team
- 📦 **Pip Installable**: Standard Python package installation
- 🎯 **Smart**: Only runs when you're actively working (virtual environment active)
- 🗑️ **Bulk Operations**: Delete multiple checkpoints at once, or all with `*`

## Quick Start

```bash
# Install the package
pip install git-checkpoints

# One-time setup (creates Git aliases and cron job)
git-checkpoints-setup

# That's it! Checkpoints will now be created automatically
```

## Installation

```bash
pip install git-checkpoints
```

## Setup

After installation, run the setup command **once** in your project directory:

```bash
cd your-project-directory
git-checkpoints-setup
```

This will:
- Create Git aliases for checkpoint commands
- Set up a cron job that runs every 5 minutes
- Configure automatic checkpoint creation when virtual environment is active

## Usage

### Automatic Checkpoints

Once setup is complete, checkpoints are created automatically every 5 minutes when:
- You're in a virtual environment (`$VIRTUAL_ENV` is set)
- You're in a Git repository
- There are uncommitted changes

### Manual Commands

After setup, you can use these Git commands:

#### Two Ways to Create Checkpoints
```bash
# Simple way - create a checkpoint directly
git checkpoint
git checkpoint "my work in progress"

# Explicit way - using the checkpoints command
git checkpoints create
git checkpoints create "my work in progress"
```

#### List Checkpoints
```bash
# Default action - just list all checkpoints
git checkpoints

# Explicit list command
git checkpoints list
```

#### Delete Checkpoints
```bash
# Delete a single checkpoint
git checkpoints delete checkpoint-name

# Delete multiple checkpoints
git checkpoints delete checkpoint-1 checkpoint-2 checkpoint-3

# Delete all checkpoints
git checkpoints delete *
```

#### Load Checkpoints
```bash
# Load a specific checkpoint
git checkpoints load checkpoint-name
```

### CLI Commands

You can also use the CLI directly with flags:

```bash
# Create manual checkpoint
git-checkpoints --create "my checkpoint"

# List checkpoints
git-checkpoints --list

# Load checkpoint
git-checkpoints --load checkpoint-name

# Delete single checkpoint
git-checkpoints --delete checkpoint-name

# Delete multiple checkpoints
git-checkpoints --delete checkpoint-1 checkpoint-2
```

## How It Works

### Smart Automation
- **Cron Job**: Runs every 5 minutes via system cron
- **Virtual Environment Detection**: Only creates checkpoints when `$VIRTUAL_ENV` is set
- **Change Detection**: Only creates checkpoints when there are uncommitted changes
- **Git Tags**: Uses tags (not commits) to avoid cluttering your commit history

### Checkpoint Format
Checkpoints are created as Git tags with this format:
- **Automatic**: `checkpoint/auto_YYYY_MM_DD_HH_MM_SS`
- **Manual**: `checkpoint/your-name`

### Team Collaboration
- Checkpoint tags are automatically pushed to your remote repository
- Team members can see and load each other's checkpoints
- Checkpoints don't interfere with normal Git workflow

## Examples

### Basic Workflow

```bash
# 1. Install and setup (once per project)
pip install git-checkpoints
cd my-project
git-checkpoints-setup

# 2. Activate virtual environment and start working
source venv/bin/activate
# Edit files...

# 3. Checkpoints are created automatically every 5 minutes
# No manual intervention needed!

# 4. List checkpoints anytime (defaults to list)
git checkpoints

# 5. Load a checkpoint if needed
git checkpoints load checkpoint/auto_2024_01_15_14_30_00
```

### Manual Checkpoints

```bash
# Create checkpoint before risky changes
git checkpoint "before refactoring user auth"

# Make changes...

# List all checkpoints to see what's available
git checkpoints

# If something goes wrong, load the checkpoint
git checkpoints load before-refactoring-user-auth
```

### Bulk Checkpoint Management

```bash
# Create a few test checkpoints
git checkpoint "test-1"
git checkpoint "test-2" 
git checkpoint "test-3"

# Delete multiple specific checkpoints
git checkpoints delete test-1 test-2

# Or delete all checkpoints at once
git checkpoints delete *
```

## Configuration

### Customizing Cron Schedule

The default cron job runs every 5 minutes. To change this:

```bash
# Edit your crontab
crontab -e

# Modify the git-checkpoints line
# For example, run every 10 minutes instead:
*/10 * * * * /usr/bin/python -m git_checkpoints.cli --auto --dir /path/to/your/project
```

### Disabling Automatic Checkpoints

```bash
# Remove the cron job
crontab -e
# Delete the git-checkpoints line

# Or temporarily disable by deactivating virtual environment
deactivate
```

## Troubleshooting

### Checking If Setup Worked

```bash
# Check if Git aliases were created
git config --local --get alias.checkpoint
git config --local --get alias.checkpoints

# Check if cron job was created
crontab -l | grep git-checkpoints
```

### Common Issues

**Cron job not running:**
- Make sure cron service is running: `sudo systemctl status cron`
- Check cron logs: `sudo journalctl -u cron`

**No checkpoints being created:**
- Ensure you're in a virtual environment: `echo $VIRTUAL_ENV`
- Check if you have uncommitted changes: `git status`
- Run manual checkpoint: `git checkpoint`

**Permission issues:**
- Ensure Git repository is properly initialized
- Check that you have write permissions to the project directory

**Command not found:**
- Make sure you ran `git-checkpoints-setup` in your project directory
- Verify aliases were created: `git config --local --list | grep alias`

## Requirements

- Python 3.8+
- Git
- Unix-like system (Linux, macOS)
- Cron service (usually pre-installed)
