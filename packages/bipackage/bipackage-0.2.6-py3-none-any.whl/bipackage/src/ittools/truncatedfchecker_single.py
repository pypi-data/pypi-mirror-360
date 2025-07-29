import argparse
import gzip
import zlib


# subcommand
def check_gzip_validity(file_path: str) -> None:
    """
    Check a compressed file validity, prints results to stdout.

    Parameters
    ----------
    file_path
        Path to the compressed file.

    Returns
    -------
    None
    """
    try:
        with gzip.open(file_path, "rb") as file:
            file.read()
        print("File read successfully.")
    except gzip.BadGzipFile:
        print("The file is truncated or invalid.")
    except zlib.error:
        print("The file is truncated or invalid.")
    except IOError:
        print("Error reading file")

    return


"""def _test_check_gzip_validity()
    parser = argparse.ArgumentParser(description="It checks a single compressed file in a specified directory")
    parser.add_argument("file_path", help="Location of the file")

    args = parser.parse_args()

    check_gzip_validity(args.file_path)
    return"""


if __name__ == "__main__":
    pass
