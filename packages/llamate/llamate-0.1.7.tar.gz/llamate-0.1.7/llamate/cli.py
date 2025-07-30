import argparse
from llamate.agent import MemoryAgent
from llamate import get_vectorstore_from_env
from llamate.commands.init import run_init

def main():
    parser = argparse.ArgumentParser(description="LLAMate - Memory agent CLI")
    parser.add_argument("--user", type=str, help="User ID")
    parser.add_argument("--init", action="store_true", help="Initialize .env and DB table")
    args = parser.parse_args()

    if args.init:
        return run_init()

    if not args.user:
        print("❌ Please provide --user or run --init")
        return

    store = get_vectorstore_from_env(args.user)
    agent = MemoryAgent(user_id=args.user, vectorstore=store)

    print("\nLLAMate CLI: Type 'exit' to quit\n")
    while True:
        prompt = input("You: ")
        if prompt.lower() in ["exit", "quit"]:
            break
        response = agent.chat(prompt)
        print("LLAMate:", response)

if __name__ == "__main__":
    main()
