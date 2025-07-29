import gzip
import logging
import os
import subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from bipackage.util.utilities import timer


class FastqMerger:
    def __init__(self, input_folder_paths, output_folder, names):
        self.input_folder_paths = input_folder_paths
        self.output_folder = output_folder
        self.names = names

    def process_samples(self, name):
        r1_paths, r2_paths = [], []

        for folder in self.input_folder_paths:
            for root, _, files in os.walk(folder):
                for filename in files:
                    if (
                        name.lower().strip() in filename.lower().strip()
                        and (filename.endswith("R1_001.fastq.gz") or filename.endswith("2.fq.gz"))
                        and "_MF_R2" not in filename
                    ):
                        r1_paths.append(os.path.join(root, filename))
                    if (
                        name.lower().strip() in filename.lower().strip()
                        and (filename.endswith("R2_001.fastq.gz") or filename.endswith("2.fq.gz"))
                        and "_MF_R2" not in filename
                    ):
                        r2_paths.append(os.path.join(root, filename))
        return r1_paths, r2_paths

    def merge_fastq_files_command(self, input_paths, output_path):
        return f"zcat {' '.join(input_paths)} | gzip > {output_path}"

    def prepare_merge_commands(self):
        commands = []
        for name in self.names:
            print(f"#################{name}###################")

            r1_paths, r2_paths = self.process_samples(name)

            fq1_output_path = os.path.join(self.output_folder, f"{name}_MF_R1_001.fastq.gz")
            fq2_output_path = os.path.join(self.output_folder, f"{name}_MF_R2_001.fastq.gz")

            if r1_paths:
                commands.append(self.merge_fastq_files_command(r1_paths, fq1_output_path))
                print("###FOR R1###")
                print(self.merge_fastq_files_command(r1_paths, fq1_output_path))
            if r2_paths:
                commands.append(self.merge_fastq_files_command(r2_paths, fq2_output_path))
                print("###FOR R2###")
                print(self.merge_fastq_files_command(r2_paths, fq2_output_path))
        return commands

    @staticmethod
    def run_merge_command(command):
        result = subprocess.run(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stderr_output = result.stderr.decode("utf-8").strip()
        stdout_output = result.stdout.decode("utf-8").strip()

        if result.returncode != 0:
            logging.error(f"Merge - An error occurred while running command: {stderr_output}")
        else:
            logging.info(f"Merge - Command completed successfully: {stdout_output}")

        return

    def execute_merge(self, commands):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.run_merge_command, command) for command in commands]
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error occurred during merging: {e}")

        return


@timer
def merge_it(*, folder_paths: list[str], sample_names: list[str], output_path: str) -> None:
    """
    Merge fastq files.

    Parameters
    ----------
    folder_paths : list[str]
        List of paths to folders.
    sample_names: list[str]
        List of name of the files.
    output_path : str
        Path to the output directory.

    Returns
    -------
    None
    """
    merger = FastqMerger(input_folder_paths=folder_paths, names=sample_names, output_folder=output_path)
    merge_commands = merger.prepare_merge_commands()
    merger.execute_merge(merge_commands)
    return


if __name__ == "__main__":
    pass
