#!/usr/bin/env python3
import argparse
import csv
import gzip
import json
import os
from concurrent.futures import ThreadPoolExecutor

from Bio import SeqIO

from bipackage.util.utilities import timer


'''Script extracts reads from undetermined fastq file for given indices'''

def create_target_indices(sample_sheet_file, output_json_file):
    """
    Reads the sample sheet CSV and creates a dictionary mapping Sample_ID to a list of
    four target index strings. Writes the dictionary to a JSON file.

    The sample sheet is assumed to have the following columns:
      Sample_ID, Sample_Name, Sample_Plate, Sample_Well, Index_Plate_Well,
      I7_Index_ID, index, I5_Index_ID, index2, Sample_Project, Description

    For each sample, it creates:
      - i7_variants: [original I7 index, 'N' + I7[1:]]
      - i5_variants: [original I5 index, 'N' + I5[1:]]

    And then combines them as: "i7_variant + '+' + i5_variant"
    """
    sample_to_indices = {}
    with open(sample_sheet_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sample_id = row["Sample_ID"].strip()
            i7 = row["index"].strip()  # I7 index
            i5 = row["index2"].strip()  # I5 index
            if not i7 or not i5:
                continue  # skip if either index is missing
            # Create variants: original and with first char replaced by 'N'
            i7_variants = [i7, "N" + i7[1:]] if len(i7) >= 1 else [i7]
            i5_variants = [i5, "N" + i5[1:]] if len(i5) >= 1 else [i5]
            target_indices = []
            for var7 in i7_variants:
                for var5 in i5_variants:
                    target_indices.append(f"{var7}+{var5}")
            sample_to_indices[sample_id] = target_indices

    # Write the mapping to a JSON file
    with open(output_json_file, "w") as jf:
        json.dump(sample_to_indices, jf, indent=4)
    return sample_to_indices


def filter_reads(input_file, output_file, target_indices):
    """
    Filters reads from a FASTQ file (gzip-compressed) based on whether any of the
    target index strings appear in the read header.
    """
    with gzip.open(input_file, "rt") as in_f, gzip.open(output_file, "wt") as out_f:
        for record in SeqIO.parse(in_f, "fastq"):
            header = record.description
            if any(index in header for index in target_indices):
                SeqIO.write(record, out_f, "fastq")


def process_sample(sample_id, target_indices, input_r1, input_r2, output_dir):
    """
    For a given sample, filter reads from the undetermined R1 and R2 FASTQ files
    using its target indices. Writes output files into output_dir.
    """
    output_r1 = os.path.join(output_dir, f"{sample_id}_R1.fastq.gz")
    output_r2 = os.path.join(output_dir, f"{sample_id}_R2.fastq.gz")

    # Filter R1 and R2 (sequentially in this function)
    filter_reads(input_r1, output_r1, target_indices)
    filter_reads(input_r2, output_r2, target_indices)
    print(f"Completed sample {sample_id}")


@timer
def undetermined_demultiplexer(
    sample_sheet: str, input_r1: str, input_r2: str, *, output_dir: str, json_output: str, threads: int = 4
) -> None:
    """
    Filter undetermined FASTQ files for multiple samples using index information.

    Parameters
    ----------
    sample_sheet : str
        Path to the sample sheet CSV file.
    input_r1 : str
        Path to the undetermined R1 FASTQ.gz file.
    input_r2 : str
        Path to the undetermined R2 FASTQ.gz file.
    output_dir : str
        Directory to store the filtered FASTQ files.
    json_output : str
        Path to output JSON file for sample target indices.
    threads : int
        Number of threads to use, default is 4.

    Returns
    -------
    None
    """
    # Ensure the output directory exists.
    os.makedirs(output_dir, exist_ok=True)

    # Create the sample->target indices JSON mapping.
    sample_to_indices = create_target_indices(sample_sheet, json_output)
    print(f"Created target indices JSON file: {json_output}")

    # Process each sample in parallel.
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for sample_id, target_indices in sample_to_indices.items():
            futures.append(
                executor.submit(
                    process_sample,
                    sample_id,
                    target_indices,
                    input_r1,
                    input_r2,
                    output_dir,
                )
            )
        for future in futures:
            future.result()
    print("Filtering completed for all samples.")

    return


"""
def main():
    parser = argparse.ArgumentParser(
        description="Filter undetermined FASTQ files for multiple samples using index information."
    )
    parser.add_argument("--sample_sheet", required=True, help="Path to the sample sheet CSV file.")
    parser.add_argument("--input_r1", required=True, help="Path to the undetermined R1 FASTQ.gz file.")
    parser.add_argument("--input_r2", required=True, help="Path to the undetermined R2 FASTQ.gz file.")
    parser.add_argument(
        "--output_dir",
        required=True,
        help="Directory to store the filtered FASTQ files.",
    )
    parser.add_argument(
        "--json_output",
        required=True,
        help="Path to output JSON file for sample target indices.",
    )
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use (default: 4).")
    args = parser.parse_args()

    # Ensure the output directory exists.
    os.makedirs(args.output_dir, exist_ok=True)

    # Create the sample->target indices JSON mapping.
    sample_to_indices = create_target_indices(args.sample_sheet, args.json_output)
    print(f"Created target indices JSON file: {args.json_output}")

    # Process each sample in parallel.
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for sample_id, target_indices in sample_to_indices.items():
            futures.append(
                executor.submit(
                    process_sample,
                    sample_id,
                    target_indices,
                    args.input_r1,
                    args.input_r2,
                    args.output_dir,
                )
            )
        for future in futures:
            future.result()
    print("Filtering completed for all samples.")
"""

if __name__ == "__main__":
    pass
