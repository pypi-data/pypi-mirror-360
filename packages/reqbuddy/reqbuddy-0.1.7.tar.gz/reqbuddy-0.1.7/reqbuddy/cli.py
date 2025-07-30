import argparse
from .main import get_requirement, find_requirement

def main():
    parser = argparse.ArgumentParser(description="ReqBuddy CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("get", help="Get dependencies from requirements.txt")
    get_parser.add_argument("-s", action="store_true", help="Strip versions")
    get_parser.add_argument("-d", action="store_true", help="Deduplicate")
    get_parser.add_argument("-p", type=str, default=None, help="Path to requirements.txt")

    find_parser = subparsers.add_parser("find", help="List installed packages")
    find_parser.add_argument("-s", action="store_true", help="Strip versions")
    find_parser.add_argument("-save", action="store_true", help="Save the requirement as txt file")

    args = parser.parse_args()

    if args.command == "get":
        result = get_requirement(
            path=args.p,
            strip=args.s,
            deduplicate=args.d
        )
    elif args.command == "find":
        result = find_requirement(
            strip=args.s,
            save=args.save
        )
    else:
        parser.print_help()
        return

    if result is not None:
        print(result)

if __name__ == "__main__":
    main()