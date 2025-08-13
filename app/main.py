import sys
import os
from app.agents.sales_assistants.orchestrator_agent import orchestrator_agent


def print_banner():
    """Print a welcome banner."""
    print("=" * 60)
    print("🤖 Sales Assistant - Terminal Interface")
    print("=" * 60)
    print("Type 'quit', 'exit', or 'bye' to end the conversation")
    print("Type 'help' for available commands")
    print("-" * 60)


def print_help():
    """Print help information."""
    print("\n📋 Available commands:")
    print("  help     - Show this help message")
    print("  clear    - Clear the screen")
    print("  quit     - Exit the application")
    print("  exit     - Exit the application")
    print("  bye      - Exit the application")
    print("\n💬 Just type your questions or requests naturally!")
    print("   Example: 'Find information about fiber optic products'")
    print("   Example: 'Send an email about our latest MEMS switches'")
    print("-" * 60)


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def main():
    """Main conversational loop."""
    try:
        # Initialize the orchestrator agent
        print("🚀 Initializing Sales Assistant...")
        print("✅ Sales Assistant ready!")

        # Print welcome banner
        print_banner()

        # Main conversation loop
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()

                # Handle empty input
                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("\n👋 Thanks for using Sales Assistant! Goodbye!")
                    break

                elif user_input.lower() == "help":
                    print_help()
                    continue

                elif user_input.lower() == "clear":
                    clear_screen()
                    print_banner()
                    continue

                # Process user input with orchestrator
                print("\n🤖 Assistant: ", end="", flush=True)

                # Get response from orchestrator
                response = orchestrator_agent.print_response(user_input)

                # Print the response
                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 Conversation interrupted. Goodbye!")
                break

            except Exception as e:
                print(f"\n❌ Error processing request: {str(e)}")
                print(
                    "💡 Please try rephrasing your request or type 'help' for guidance."
                )

    except Exception as e:
        print(f"❌ Failed to initialize Sales Assistant: {str(e)}")
        print("💡 Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
