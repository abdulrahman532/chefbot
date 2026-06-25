"""ChefBot - Interactive CLI for the Recipe & Cooking AI Assistant.

This is the main entry point for interacting with ChefBot.
It provides an interactive command-line interface for asking
cooking questions powered by RAG.
"""

import os
import sys

# ANSI color codes
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_banner():
    """Print the ChefBot welcome banner."""
    banner = f"""
{BOLD}{GREEN}╔══════════════════════════════════════════════════╗
║          🍳  ChefBot - Cooking Assistant  🍳      ║
║     Your AI-powered recipe & cooking helper       ║
╚══════════════════════════════════════════════════╝{RESET}

{DIM}Commands:{RESET}
  {CYAN}/help{RESET}        - Show this help message
  {CYAN}/hyde on|off{RESET} - Toggle HyDE retrieval (default: on)
  {CYAN}/reindex{RESET}     - Rebuild the recipe index
  {CYAN}/quit{RESET}        - Exit ChefBot
"""
    print(banner)


def ensure_index():
    """Check if the ChromaDB index exists; if not, build it."""
    from rag.indexing import get_collection, index_documents

    try:
        collection = get_collection()
        count = collection.count()
        print(f"{GREEN}✓ Recipe index loaded ({count} chunks){RESET}")
        return collection
    except ValueError:
        print(f"{YELLOW}⚠ No recipe index found. Building index...{RESET}")
        collection = index_documents()
        print(f"{GREEN}✓ Index built successfully ({collection.count()} chunks){RESET}")
        return collection


def main():
    """Main interactive loop."""
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    print_banner()

    # Ensure index is built
    try:
        collection = ensure_index()
    except Exception as e:
        print(f"{RED}✗ Failed to load/build index: {e}{RESET}")
        sys.exit(1)

    use_hyde = True

    from rag.retrieval import ask

    print(f"\n{DIM}Ask me anything about cooking and recipes!{RESET}\n")

    while True:
        try:
            query = input(f"{BOLD}{BLUE}You:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{GREEN}Goodbye! Happy cooking! 🍽️{RESET}")
            break

        if not query:
            continue

        # Handle commands
        if query.startswith("/"):
            cmd = query.lower()

            if cmd == "/quit" or cmd == "/exit":
                print(f"\n{GREEN}Goodbye! Happy cooking! 🍽️{RESET}")
                break

            elif cmd == "/help":
                print_banner()
                continue

            elif cmd == "/reindex":
                print(f"{YELLOW}Rebuilding recipe index...{RESET}")
                from rag.indexing import index_documents
                collection = index_documents()
                print(f"{GREEN}✓ Index rebuilt ({collection.count()} chunks){RESET}\n")
                continue

            elif cmd.startswith("/hyde"):
                parts = cmd.split()
                if len(parts) == 2:
                    if parts[1] == "on":
                        use_hyde = True
                        print(f"{GREEN}✓ HyDE retrieval enabled{RESET}\n")
                    elif parts[1] == "off":
                        use_hyde = False
                        print(f"{YELLOW}✓ HyDE retrieval disabled (using basic retrieval){RESET}\n")
                    else:
                        print(f"{RED}Usage: /hyde on|off{RESET}\n")
                else:
                    status = "on" if use_hyde else "off"
                    print(f"{DIM}HyDE is currently: {status}{RESET}\n")
                continue

            else:
                print(f"{RED}Unknown command: {query}. Type /help for available commands.{RESET}\n")
                continue

        # Process query
        try:
            method_label = "HyDE" if use_hyde else "Basic"
            print(f"{DIM}[Retrieving with {method_label}...]{RESET}")

            result = ask(
                query=query,
                collection=collection,
                use_hyde=use_hyde,
            )

            # Print answer
            print(f"\n{BOLD}{GREEN}ChefBot:{RESET} {result['answer']}")

            # Print sources
            if result["sources"]:
                print(f"\n{DIM}📚 Sources ({result['method']}):")
                for src in result["sources"]:
                    cat_info = f" [{src['category']}]" if src.get('category') else ""
                    print(f"   • {src['title']}{cat_info}")
                print(RESET)

        except EnvironmentError as e:
            print(f"{RED}✗ {e}{RESET}\n")
        except Exception as e:
            print(f"{RED}✗ Error: {e}{RESET}\n")


if __name__ == "__main__":
    main()
