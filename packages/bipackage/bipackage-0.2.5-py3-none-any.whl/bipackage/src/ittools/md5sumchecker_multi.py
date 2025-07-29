import argparse
import multiprocessing
import os
import subprocess

from bipackage.util.utilities import timer


'''Checks md5sums of files and validates if they match'''

class MD5SumChecker:
    def __init__(self, input_directory, file_extension, num_processes):
        self.input_directory = input_directory
        self.file_extension = file_extension
        self.num_processes = num_processes
        self.checker()

    def calculate_md5sum(self, file_path):
        try:
            result = subprocess.run(
                ["md5sum", file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            md5sum_value = result.stdout.split()[0]

            return md5sum_value
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return None

    def check_file(self, root, filename):
        md5sum_name = filename + ".md5sum"
        with open(os.path.join(root, md5sum_name), "r") as file:
            md5sum_file = file.read()
            md5sum_value = md5sum_file.split()[0]

        md5sum_path = os.path.join(root, md5sum_name)
        f_path = os.path.join(root, filename)

        calcmd5sum = self.calculate_md5sum(f_path)

        if calcmd5sum is not None and md5sum_value == calcmd5sum:
            print(f"For {f_path} {md5sum_path}, md5sums are same")
        else:
            print(f"For {f_path} {md5sum_path}, md5sums are different")

        return

    def checker(self):
        pool = multiprocessing.Pool(processes=self.num_processes)
        for root, dirs, files in os.walk(self.input_directory):
            for filename in files:
                if filename.endswith(self.file_extension):
                    pool.apply_async(self.check_file, args=(root, filename))
        pool.close()
        pool.join()

        return


# subcommand
@timer
def md5sumchecker(input_directory: str, file_extension, num_processes: int = 2) -> None:
    """
    MD5Sum Checker.

    Parameters
    ----------
    input_directory : str
        Input directory path.
    file_extension : str
        File extension to search for.
    num_processes : int
        Number of processes to use, default is 2

    Returns
    -------
    MD5SumChecker
    """
    md5_checker = MD5SumChecker(
        input_directory=input_directory, file_extension=file_extension, num_processes=num_processes
    )
    return md5_checker


def main():
    parser = argparse.ArgumentParser(description="MD5Sum Checker")
    parser.add_argument("-i", "--input_directory", required=True, help="Input directory path")
    parser.add_argument("-fe", "--file_extension", required=True, help="File extension to search for")
    parser.add_argument(
        "-p",
        "--num_processes",
        type=int,
        default=2,
        help="Number of processes to use (default: 2)",
    )
    args = parser.parse_args()

    md5_checker = MD5SumChecker(args.input_directory, args.file_extension, args.num_processes)


if __name__ == "__main__":
    pass
