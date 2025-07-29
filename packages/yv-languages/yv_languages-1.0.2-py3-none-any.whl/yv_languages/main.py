"""Main to test package manually."""

import argparse

import yv_languages


def main():
    """script for testing a language tag."""
    parser = argparse.ArgumentParser(description="Used to view information about a language tag.")
    parser.add_argument("--language_tag", type=str, help="Language tag to parse")
    _args = parser.parse_args()

    _canonical = yv_languages.canonical(_args.language_tag)
    print(f"Original Tag: {_args.language_tag}")
    print(f"Canonical Tag: {_canonical}")


if __name__ == "__main__":
    main()
