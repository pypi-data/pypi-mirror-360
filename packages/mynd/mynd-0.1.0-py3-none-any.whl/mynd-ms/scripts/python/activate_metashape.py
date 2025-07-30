from argparse import ArgumentParser

import Metashape


def main():
    """Script to activate a license with the Metashape python API."""
    # Set up argument parser and add arguments
    parser = ArgumentParser(
        description="activates a Metashape license with the Python API",
    )
    parser.add_argument("key", type=str)

    # Parse arguments
    arguments = parser.parse_args()

    # Try to activate the license with given key
    try:
        license = Metashape.License()
        license.activate(arguments.key)
    except RuntimeError as error:
        print(error)


if __name__ == "__main__":
    main()
