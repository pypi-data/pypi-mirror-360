import argparse
import sys
from . import __version__  # Import __version__ from the package's __init__.py

def bl_command():
    """Prints a greeting to everyone."""
    print("hi everyone")

def show_help(parser):
    """Shows the available commands."""
    parser.print_help()

def main():
    parser = argparse.ArgumentParser(
        description=f"bl9Test - A simple CLI tool (Version {__version__})"
    )
    # We won't use subparsers in the traditional sense for the interactive loop,
    # but we'll use the parser's help for our custom help.

    print("Welcome to bl9Test! Type 'help' for commands or 'exit' to quit.")
    print(f"Version: {__version__}") # Optionally display version on startup

    while True:
        try:
            # Prompt the user for input
            command_line = input("bl9Test> ").strip()

            if not command_line:
                continue # If input is empty, prompt again

            # Split the command into command and arguments
            parts = command_line.split(maxsplit=1)
            command = parts[0]
            # No actual arguments are handled by existing commands, but this structure is good for future expansion
            # args = parts[1:] if len(parts) > 1 else []

            if command == 'exit':
                print("Exiting bl9Test. Goodbye!")
                sys.exit(0) # Exit the program cleanly
            elif command == 'help':
                show_help(parser)
                print("\nAvailable internal commands:")
                print("  bl    - Print a greeting")
                print("  exit  - Exit the bl9Test tool")
                print("  help  - Show this help message")
            elif command == 'bl':
                bl_command()
            else:
                print(f"Error: Unknown command '{command}'. Type 'help' for available commands.")

        except EOFError: # Handles Ctrl+D
            print("\nExiting bl9Test. Goodbye!")
            sys.exit(0)
        except KeyboardInterrupt: # Handles Ctrl+C
            print("\nExiting bl9Test. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()