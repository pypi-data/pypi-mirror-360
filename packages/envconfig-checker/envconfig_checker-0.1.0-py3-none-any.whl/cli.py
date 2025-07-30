import argparse
from env_checker import check_env

def main():
    parser = argparse.ArgumentParser(description="Check required environment variables.")
    parser.add_argument('--required', nargs='+', help='List of required environment variables', required=True)
    parser.add_argument('--no-dotenv', action='store_true', help="Do not load .env file")

    args = parser.parse_args()
    check_env(args.required, load_dotenv_file=not args.no_dotenv)

if __name__ == "__main__":
    main()
