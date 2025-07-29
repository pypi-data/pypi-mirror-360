import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from bipackage.util.utilities import timer


# Keep the function outside the class
def run_bedtools_command(args):
    bam_file, exome_bait, input_dir = args
    sample_name = os.path.splitext(os.path.basename(bam_file))[0]
    output_name = sample_name + "_counts.tsv"
    command = f"bedtools multicov -bed {exome_bait} -bams {bam_file} -q 20 -p > {os.path.join(input_dir, output_name)}"
    os.system(command)


class CountsFromBam:
    def __init__(self, input_dir, exome_bait, num_threads):
        self.input_dir = input_dir
        self.exome_bait = exome_bait
        self.num_threads = num_threads

    def process_bams(self):
        bam_list = []

        # Find all BAM files recursively in the input directory
        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith(".bam"):
                    bam_list.append(os.path.join(root, file))

        # Prepare arguments for the bedtools command
        arguments = [(bam_file, self.exome_bait, self.input_dir) for bam_file in bam_list]

        # Use ThreadPoolExecutor to parallelize the bedtools command execution
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [executor.submit(run_bedtools_command, arg) for arg in arguments]

            for future in as_completed(futures):
                try:
                    future.result()  # To catch exceptions raised during thread execution
                except Exception as e:
                    print(f"Error occurred: {e}")

    def create_count_matrix(self):
        counts_paths = [
            os.path.join(self.input_dir, item) for item in os.listdir(self.input_dir) if item.endswith("_counts.tsv")
        ]
        file_names = [item for item in os.listdir(self.input_dir) if item.endswith("_counts.tsv")]

        # Check if count files exist
        if not counts_paths:
            print("No count files found!")
            return

        counts_names = [name.split("_counts")[0] for name in file_names]

        # Read the first file and initialize the DataFrame
        count_mat = pd.read_csv(counts_paths[0], sep="\t", header=None)

        count_mat.columns = ["chromosome", "start", "end", counts_names[0]]

        # Append data from the remaining files
        for i in range(1, len(counts_paths)):
            df = pd.read_csv(counts_paths[i], sep="\t", header=None)
            con_df = df.iloc[:, 3]
            con_df.name = counts_names[i]
            count_mat = pd.concat([count_mat, con_df], axis=1)

        # Save the final count matrix
        count_mat.to_csv(os.path.join(self.input_dir, "Counts_matrix.txt"), sep="\t", index=False)


@timer
def bam_counts(input_dir: str, exome_bait: str, num_threads: int = 40) -> None:
    """
    Get counts from BAM file.

    Parameters
    ----------
    input_dir : str
        Input directory.
    exome_bait : str
        Exom bait.
    num_threads : int
        Number of threads to use, default is 40.

    Returns
    -------
    None
    """
    counts = CountsFromBam(input_dir, exome_bait, num_threads)
    counts.process_bams()
    # Create count matrix
    counts.create_count_matrix()
    return


if __name__ == "__main__":
    pass
