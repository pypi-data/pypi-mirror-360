import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from bipackage.util.utilities import timer


def count_reads_and_bases(fastq_file):
    try:
        read_count = int(subprocess.check_output(f"zcat {fastq_file} | wc -l", shell=True, text=True).strip()) // 4

        first_read_length = (
            int(subprocess.check_output(f"zcat {fastq_file} | sed -n '2p' | wc -c", shell=True, text=True).strip()) - 1
        )
        base_count = read_count * first_read_length

        return fastq_file, read_count, base_count
    except subprocess.CalledProcessError as e:
        print(f"Error processing {fastq_file}: {e}")
        return fastq_file, 0, 0


@timer
def fastq_read_counter(directory: str, output_path: str) -> None:
    """
    Count fastq.

    Parameters
    ----------
    directory : str
        Path to directory.
    output_path : str
        Path to save csv file.

    """
    files_to_process = [
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if filename.endswith(".fastq.gz") and not filename.startswith("Undetermined")
    ]

    results = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(count_reads_and_bases, file): file for file in files_to_process}

        for future in futures:
            filename, read_count, base_count = future.result()
            results.append(
                {
                    "file": os.path.basename(filename),
                    "reads": read_count,
                    "bases": base_count,
                }
            )

    df = pd.DataFrame(results)

    # print(df)

    df.to_csv(output_path, index=False)

    return


if __name__ == "__main__":
    pass
