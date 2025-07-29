"""Entry point for text-lens when run as a module or script."""

def main():
    """Main entry point that imports and runs the app."""
    # Import the app module, which runs the GUI
    from . import app

if __name__ == "__main__":
    main()