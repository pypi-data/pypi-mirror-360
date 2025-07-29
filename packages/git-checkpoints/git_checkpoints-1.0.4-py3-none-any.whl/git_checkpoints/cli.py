"""Command line interface for Git Checkpoints."""

import argparse
import sys
from pathlib import Path

from .core import GitCheckpoints


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Git Checkpoints - Automatic Git checkpoints with zero configuration",
        prog="git-checkpoints",
    )

    # Add positional argument for command
    parser.add_argument(
        "command",
        nargs="?",
        choices=["create", "list", "delete", "load"],
        help="Command to execute (create, list, delete, load)",
    )

    # Add remaining arguments for the command
    parser.add_argument("args", nargs="*", help="Arguments for the command")

    # Legacy flag-based interface for backward compatibility
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run automatic checkpoint (used by cron job)",
    )

    parser.add_argument(
        "--create", metavar="NAME", help="Create a manual checkpoint with optional name"
    )

    parser.add_argument("--list", action="store_true", help="List all checkpoints")

    parser.add_argument(
        "--delete",
        metavar="NAME",
        nargs="+",
        help="Delete checkpoint(s) (use * for all)",
    )

    parser.add_argument("--load", metavar="NAME", help="Load a checkpoint")

    parser.add_argument(
        "--dir",
        metavar="PATH",
        help="Project directory (defaults to current directory)",
    )

    parser.add_argument("--version", action="version", version="git-checkpoints 1.0.0")

    args = parser.parse_args()

    # Initialize Git Checkpoints
    project_dir = Path(args.dir) if args.dir else Path.cwd()
    git_cp = GitCheckpoints(project_dir)

    # Handle legacy flag-based commands first
    if args.auto:
        git_cp.auto_checkpoint()
        return
    elif args.create is not None:
        name = args.create if args.create else None
        git_cp.create_checkpoint(name)
        return
    elif args.list:
        checkpoints = git_cp.list_checkpoints()
        if checkpoints:
            for cp in checkpoints:
                print(cp)
        else:
            print("No checkpoints found")
        return
    elif args.delete:
        for name in args.delete:
            if name == "*":
                git_cp.delete_all_checkpoints()
            else:
                git_cp.delete_checkpoint(name)
        return
    elif args.load:
        git_cp.load_checkpoint(args.load)
        return

    # Handle positional command-based interface
    if not args.command:
        # No command given, default to list
        checkpoints = git_cp.list_checkpoints()
        if checkpoints:
            for cp in checkpoints:
                print(cp)
        else:
            print("No checkpoints found")
    elif args.command == "create":
        name = args.args[0] if args.args else None
        git_cp.create_checkpoint(name)
    elif args.command == "list":
        checkpoints = git_cp.list_checkpoints()
        if checkpoints:
            for cp in checkpoints:
                print(cp)
        else:
            print("No checkpoints found")
    elif args.command == "delete":
        if not args.args:
            print("Error: delete command requires checkpoint names")
            sys.exit(1)
        for name in args.args:
            if name == "*":
                git_cp.delete_all_checkpoints()
                break
            else:
                git_cp.delete_checkpoint(name)
    elif args.command == "load":
        if not args.args:
            print("Error: load command requires a checkpoint name")
            sys.exit(1)
        git_cp.load_checkpoint(args.args[0])


if __name__ == "__main__":
    main()
