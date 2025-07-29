import argparse
import csv
import json
import logging
import os
import subprocess

'''Script downsamples fastqs'''

import pandas as pd

from bipackage.util.utilities import timer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Indexer:
    def __init__(self, reference_fasta: str, algotype: str):
        self.reference_fasta = reference_fasta
        self.algotype = algotype

    def index(self):
        logging.info("bwa - Indexing the reference genome")
        command = f"bwa index -a {self.algotype} {self.reference_fasta}"

        try:
            os.system(command)
            logging.info("bwa - Successfully indexed the reference genome")
        except Exception as e:
            logging.error(f"bwa - An error occurred while indexing the reference genome: {e}")


class Mapper:
    def __init__(
        self,
        reference_fasta: str,
        sample_id: str,
        r1: str,
        r2: str,
        threads: int,
        output_path: str,
        use_dragen: bool = False,
        hash_table: str = None,
    ):
        self.reference_fasta = reference_fasta
        self.sample_id = sample_id
        self.r1 = r1
        self.r2 = r2
        self.threads = threads
        self.output_path = output_path
        self.use_dragen = use_dragen
        self.hash_table = hash_table

    def map(self):
        sample_bam_path = os.path.join(self.output_path, self.sample_id)
        os.makedirs(sample_bam_path, exist_ok=True)
        sam_file = self.sample_id + ".sam"

        if self.use_dragen:
            logging.info(f"dragen - Mapping {self.r1} and {self.r2} to the reference genome")
            command = (
                f"dragen-os -r {self.hash_table} "
                f"-1 {self.r1} -2 {self.r2} "
                f"--RGSM {self.sample_id} --RGID {self.sample_id} "
                f"--num-threads {self.threads} > {os.path.join(sample_bam_path, sam_file)}"
            )

            try:
                os.system(command)
                logging.info(f"dragen - Successfully mapped {self.r1} and {self.r2} to the reference genome")
            except Exception as e:
                logging.error(f"dragen - An error occurred while mapping {self.r1} and {self.r2}: {e}")

        else:
            logging.info(f"bwa - Mapping {self.r1} and {self.r2} to the reference genome")
            command = (
                f"bwa mem -M -t {self.threads} "
                f"-R '@RG\\tID:{self.sample_id}\\tSM:{self.sample_id}\\tLB:Mylib\\tPU:Illumina' "
                f"{self.reference_fasta} {self.r1} {self.r2} > {os.path.join(sample_bam_path, sam_file)}"
            )

            try:
                os.system(command)
                logging.info(f"bwa - Successfully mapped {self.r1} and {self.r2} to the reference genome")
            except Exception as e:
                logging.error(f"bwa - An error occurred while mapping {self.r1} and {self.r2}: {e}")

            return os.path.join(sample_bam_path, sam_file)


class BAMConverter:
    def __init__(
        self,
        sample_id,
        sam_path,
        threads,
        use_mark_duplicates,
        remove_all_duplicates,
        remove_sequencing_duplicates,
    ):
        self.sample_id = sample_id
        self.sam_path = sam_path
        self.threads = threads
        self.use_mark_duplicates = use_mark_duplicates
        self.remove_all_duplicates = remove_all_duplicates
        self.remove_sequencing_duplicates = remove_sequencing_duplicates
        self.out_path = os.path.dirname(self.sam_path)
        self.bam_file = self.sample_id + ".bam"
        self.output_bam = os.path.join(self.out_path, self.bam_file)
        self.filtered_bam_file = "filtered_" + self.sample_id + ".bam"
        self.filtered_bam = os.path.join(self.out_path, self.filtered_bam_file)
        self.metrics_file = self.sample_id + "_dup_metrics.txt"
        self.metrics_path = os.path.join(self.out_path, self.metrics_file)
        self.sorted_bam_file = "sorted_" + self.filtered_bam_file
        self.sorted_bam = os.path.join(self.out_path, self.sorted_bam_file)

    def create_bam_file(self):
        logging.info(f"Samtools - Creating a bam file for {self.sample_id} from sam file")
        converter_cmd = f"samtools view -@ {self.threads} -bS -o {self.output_bam} {self.sam_path}"

        try:
            os.system(converter_cmd)
            logging.info(f"Samtools - Successfully created bam file for {self.sample_id}")
        except Exception as e:
            logging.error(f"Samtools - An error occurred while creating bam file for {self.sample_id}: {e}")

    def mark_duplicates(self):
        if self.use_mark_duplicates:
            logging.info(f"MarkDuplicatesSpark - Marking and removing duplicates for bam file of {self.sample_id}")
            marker_cmd = f"gatk MarkDuplicatesSpark -I {self.output_bam} -O {self.filtered_bam} --metrics-file {self.metrics_path} --spark-master local[{self.threads}]"

            if self.remove_sequencing_duplicates:
                marker_cmd += " --remove-sequencing-duplicates"

            if self.remove_all_duplicates:
                marker_cmd += " --remove-all-duplicates"

            try:
                os.system(marker_cmd)
                logging.info(
                    f"MarkDuplicatesSpark - Successfully marked and removed duplicates for {self.sample_id} > {self.filtered_bam}"
                )
            except Exception as e:
                logging.error(
                    f"An error occurred while marking and removing duplicates for bam file of {self.sample_id}: {e}"
                )
        else:
            logging.info(f"Sambamba - Marking and removing duplicates for bam file of {self.sample_id}")
            marker_cmd = f"sambamba markdup -t {self.threads} {self.output_bam} {self.filtered_bam}"

            if self.remove_all_duplicates:
                marker_cmd += " --remove-duplicates"

            try:
                os.system(marker_cmd)
                logging.info(
                    f"Sambamba - Successfully marked and removed duplicates for {self.sample_id} > {self.filtered_bam}"
                )
            except Exception as e:
                logging.error(
                    f"An error occurred while marking and removing duplicates for bam file of {self.sample_id}: {e}"
                )

    def sort_bam(self):
        sort_cmd = f"samtools sort -@ {self.threads} {self.filtered_bam} -o {self.sorted_bam}"

        try:
            os.system(sort_cmd)
            logging.info(f"Samtools - Successfully sorted bam file for {self.sample_id} > {self.sorted_bam}")
        except Exception as e:
            logging.error(f"Samtools - An error occurred while sorting bam file for {self.sample_id}: {e}")

    def index_bam(self):
        index_cmd = f"samtools index -@ {self.threads} {self.sorted_bam}"

        try:
            os.system(index_cmd)
            logging.info(f"Samtools - Successfully indexed bam file for {self.sample_id} > {self.sorted_bam}")
        except Exception as e:
            logging.error(f"Samtools - An error occurred while indexing bam file for {self.sample_id}: {e}")

    def clean_up(self):
        try:
            os.remove(self.sam_path)
            os.remove(self.output_bam)
            os.remove(self.filtered_bam)
            logging.info(f"Clean up - Successfully removed intermediate files for {self.sample_id}")
        except Exception as e:
            logging.error(f"Clean up - An error occurred while removing intermediate files for {self.sample_id}: {e}")

    def convert_markdedup(self):
        self.create_bam_file()
        self.mark_duplicates()
        self.sort_bam()
        self.index_bam()
        self.clean_up()

        return self.sorted_bam


# class CoverageAnalysis:
#     def __init__(self, reference, bam, bed, output_dir, max_worker):
#         self.reference = reference
#         self.bam = bam
#         self.bed = bed
#         self.output_dir = output_dir
#         self.max_worker = max_worker

#     def run_mosdepth(self):

#         output_prefix = os.path.splitext(self.bam)[0]
#         output = os.path.join(self.output_dir, output_prefix)
#         command = [
#             "mosdepth", output, f"-x -Q 1 -t {self.max_worker}",
#             "--by", self.bed, f"-f {self.reference}",
#             f"-n -T 1,5,10,15,20,30,50,100,500,1500",
#             self.bam
#         ]
#         subprocess.run(" ".join(command), shell=True)

#     def calculate_coverages(self):

#         output_prefix = os.path.splitext(self.bam)[0]
#         qc_thresholds_file = os.path.join(self.output_dir, f"{output_prefix}.thresholds.bed.gz")

#         result = []

#         df = pd.read_csv(qc_thresholds_file, compression='gzip', header=None, sep='\t')
#         columns = df.iloc[0].to_list()
#         df = df.drop(df.index[0])
#         df.columns = columns
#         df['size'] = df['end'].astype(int) - df['start'].astype(int)

#         total_size = df['size'].sum()
#         print(total_size)

#         # Coverage columns
#         coverage_columns = [col for col in df.columns if col.endswith('X')]

#         # Calculate the sum of each coverage column and then calculate coverage
#         coverage_dict = {}
#         for col in coverage_columns:
#             df[col] = pd.to_numeric(df[col], errors='coerce').astype(int)
#             coverage_sum = df[col].sum()
#             coverage = coverage_sum / total_size
#             coverage_dict[col] = coverage

#         # Display the coverage values
#         for col, cov in coverage_dict.items():
#             result.append({"key": f"PCT of QC coverage region with coverage [{col.lower()}: inf):", "value": round(cov * 100, 2)})

#         coverage_keys = list(coverage_dict.keys())
#         for i in range(len(coverage_keys) - 1):
#             diff = df[coverage_keys[i]] - df[coverage_keys[i + 1]]
#             result.append({"key": f"PCT of QC coverage region with coverage [{coverage_keys[i].lower()}:{coverage_keys[i + 1].lower()}):", "value": round((diff.sum() / total_size) * 100, 2)})

#         return result

#     def OnTargetContigs(self):

#         output_prefix = os.path.splitext(self.bam)[0]
#         depth_summary = os.path.join(self.output_dir, f"{output_prefix}.mosdepth.summary.txt")

#         df = pd.read_csv(depth_summary, sep="\t")
#         df = df.iloc[:50]
#         # Select values without _region. all chromosomes
#         df1 = df[~df['chrom'].str.endswith('_region')]
#         total_bases = df1['bases'].astype(int).sum()

#         # Select target regions only
#         df = df[df['chrom'].str.endswith('_region')]
#         df['chrom'] = df['chrom'].str.replace('_region', '')
#         target_total_bases = df['bases'].astype(int).sum()
#         target_length = df['length'].astype(int).sum()
#         mean_coverage = round(target_total_bases / target_length, 2)

#         df = df.drop(['length', 'bases', 'min', 'max'], axis=1)

#         df.columns = ['key', 'value']
#         # uniformity_2 = sum(1 for x in total if x > 0.2 * mean_coverage) / total_bases * 100
#         # uniformity_4 = sum(1 for x in total if x > 0.4 * mean_coverage) / total_bases * 100
#         final_result = [
#             {"key": "Aligned bases", "value": total_bases},
#             {"key":"Aligned bases in QC coverage region", "value":target_total_bases},
#             {"key": "Average alignment coverage over QC coverage region", "value": mean_coverage},
#             # {"key": "Uniformity of coverage (PCT > 0.2*mean)", "value": uniformity_2},
#             # {"key": "Uniformity of coverage (PCT > 0.4*mean)", "value": uniformity_4},
#             {"key": "PCT of QC coverage region with coverage [0x: inf):", "value": 100}
#         ]

#         print(df.to_dict(orient="records"), final_result)

#         return df.to_dict(orient="records"), final_result


class Downsampler:
    def __init__(self, alignment_file, keep, sample_id, strategy, refseq):
        self.alignment_file = alignment_file
        self.sample_id = sample_id
        self.keep = keep
        self.strategy = strategy
        self.refseq = refseq
        # self.exome_bait = exome_bait
        # self.quality_threshold = quality_threshold
        # self.read_length = read_length
        # self.desired_mean_coverage = desired_mean_coverage
        self.bam_dir = os.path.dirname(self.alignment_file)

    # def get_bam_counts(self):

    #     sample_name = os.path.splitext(bam_file)[0]
    #     output_name = sample_name + "_counts.tsv"
    #     command = f"bedtools multicov -bed {self.exome_bait} -bams {self.alignment_file} -q {self.quality_threshold} -p > {os.path.join(self.bam_dir, output_name)}"

    #     try:
    #         os.system(command)
    #         logging.info("multicov - Successfully get the read counts the bam")
    #     except Exception as e:
    #         logging.error(f"multicov - An error occurred getting read counts from the bam: {e}")

    #     return os.path.join(self.bam_dir, output_name)

    # def calculate_keep(self, counts_file):

    #     counts_df = pd.read_csv(counts_file, sep="\t", header=None)

    #     counts_df = counts_df.iloc[:, [0,1,2,-1]]

    #     counts_df.columns = ["chrom", "start", "end", "counts"]

    #     counts_df["bait_length"] = (counts_df["end"] - counts_df["start"]).abs()

    #     counts_df["mean_coverage"] = (self.read_length * counts_df["counts"]) / counts_df["bait_length"]

    #     overall_coverage = sum(counts_df["mean_coverage"]) / len(counts_df)

    #     keep = self.desired_mean_coverage / overall_coverage

    #     return keep

    def ds(self):
        bam_name = os.path.basename(self.alignment_file)
        downsampled_name = f"downsampled_{bam_name}"
        downsampled_path = os.path.join(self.bam_dir, downsampled_name)

        logging.info(f"Downsampling the bam: {bam_name}")

        command = f"gatk DownsampleSam -I {self.alignment_file} -O {downsampled_path} -S {self.strategy} -P {self.keep} --REFERENCE_SEQUENCE {self.refseq}"

        try:
            os.system(command)
            logging.info("DownsampleSam - Successfully downsampled the bam")
        except Exception as e:
            logging.error(f"DownsampleSam - An error occurred while downsampling bam: {e}")

        return downsampled_path

    def remove_unpaired_reads(self, downsampled_bam):  ### YOUREHERE.
        logging.info(f"Removing unpaired reads")

        final_bam_name = self.sample_id + "_final.bam"

        final_bam = os.path.join(self.bam_dir, final_bam_name)

        command = f"samtools view -f 0x2 {downsampled_bam} -b -o {final_bam}"

        try:
            os.system(command)
            logging.info("samtools - Successfully removed unpaired reads")
        except Exception as e:
            logging.error(f"samtools - An error occurred while removing unpaired reads: {e}")

        return final_bam

    def bamtofastq(self, final_bam):
        logging.info(f"Creating fastq files from bam file")

        r1 = os.path.join(self.bam_dir, f"{self.sample_id}_DS_R1_001.fastq.gz")

        r2 = os.path.join(self.bam_dir, f"{self.sample_id}_DS_R2_001.fastq.gz")

        command = f"gatk SamToFastq -I {final_bam} -F {r1} -F2 {r2}"

        try:
            os.system(command)
            logging.info("SamToFastq - Successfully created the downsampled fastq files")
        except Exception as e:
            logging.error(f"SamToFastq - An error occurred while downsampling bam: {e}")


@timer
def downsample(
    sample_id: str,
    r1: str,
    r2: str,
    out_path: str,
    reference: str,
    *,
    threads: int = 40,
    remove_all_dups: bool = False,
    remove_seq_dups: bool = False,
    use_gatk_md: bool = False,
    strategy: str = "HighAccuracy",
    keep: float = 0.5,
) -> None:
    """
    Pipeline to map, deduplicate, and downsample sequencing reads.

    Parameters
    ----------
    sample_id : str
        Sample ID.
    r1 : str
        Path to R1 fastq file.
    r2 : str
        Path to R2 fastq file.
    out_path : str
        Output path for the results.
    reference : str
        Path to the reference genome.
    threads : int
        Number of threads to use , default is 40.
    remove_all_dups : bool
        Whether to remove all duplicates, default is False.
    remove_seq_dups : bool
        Whether to remove sequencing duplicates, default is False.
    use_gatk_md : bool
        Whether to use Use GATK MarkDuplicatesSpark, default is False.
    strategy : str
        Downsampling strategy, default is 'High Accuracy'
    keep : float
        Ratio of the reads to keep [0-1], default is 0.5.
    """
    mapit = Mapper(
        reference_fasta=reference,
        sample_id=sample_id,
        r1=r1,
        r2=r2,
        output_path=out_path,
        threads=threads,
    )
    sam_file = mapit.map()

    dedup = BAMConverter(
        sam_path=sam_file,
        sample_id=sample_id,
        threads=threads,
        use_mark_duplicates=use_gatk_md,
        remove_all_duplicates=remove_all_dups,
        remove_sequencing_duplicates=remove_seq_dups,
    )
    bam_file = dedup.convert_markdedup()

    downsampler = Downsampler(
        alignment_file=bam_file,
        sample_id=sample_id,
        strategy=strategy,
        refseq=reference,
        keep=keep,
    )

    downsampled_bam = downsampler.ds()
    final_bam = downsampler.remove_unpaired_reads(downsampled_bam)
    downsampler.bamtofastq(final_bam)
    return


""" def _old_downsample():
    parser = argparse.ArgumentParser(description="Pipeline to map, deduplicate, and downsample sequencing reads.")
    parser.add_argument("--sample_id", type=str, required=True, help="Sample ID")
    parser.add_argument("--r1", required=True, help="Path to R1 fastq file")
    parser.add_argument("--r2", required=True, help="Path to R2 fastq file")
    parser.add_argument("--out_path", required=True, help="Output path for the results")
    parser.add_argument("--threads", type=int, default=40, help="Number of threads to use")
    parser.add_argument("--remove_all_dups", action="store_true", help="Remove all duplicates")
    parser.add_argument("--remove_seq_dups", action="store_true", help="Remove sequencing duplicates")
    parser.add_argument("--use_gatk_md", action="store_true", help="Use GATK MarkDuplicatesSpark")
    parser.add_argument("--strategy", default="HighAccuracy", help="Downsampling strategy")
    parser.add_argument("--keep", type=float, default=0.5, help="How much read to keep? Give a ratio")
    parser.add_argument("--reference", required=True, help="Path to the reference genome")
    # parser.add_argument('--bed', required=True, help='Path to the exome bait BED file')
    # parser.add_argument('--qc_threshold', type=int, default=20, help='Quality threshold for read counting')
    # parser.add_argument('--read_length', type=int, default=150, help='Read length')
    # parser.add_argument('--desired_mean_coverage', type=int, default=100, help='Desired mean coverage after downsampling')

    args = parser.parse_args()

    mapit = Mapper(
        reference_fasta=args.reference,
        sample_id=args.sample_id,
        r1=args.r1,
        r2=args.r2,
        output_path=args.out_path,
        threads=args.threads,
    )
    sam_file = mapit.map()

    dedup = BAMConverter(
        sam_path=sam_file,
        sample_id=args.sample_id,
        threads=args.threads,
        use_mark_duplicates=args.use_gatk_md,
        remove_all_duplicates=args.remove_all_dups,
        remove_sequencing_duplicates=args.remove_seq_dups,
    )
    bam_file = dedup.convert_markdedup()

    # coverage = CoverageAnalysis(
    #     reference=args.reference,
    #     bam = bam_file,
    #     bed = args.bed,
    #     output_dir=args.out_path,
    #     max_worker= args.threads
    # )
    # coverage.run_mosdepth()
    # coverage.calculate_coverages()
    # coverage.OnTargetContigs()

    downsampler = Downsampler(
        alignment_file=bam_file,
        sample_id=args.sample_id,
        strategy=args.strategy,
        refseq=args.reference,
        keep=args.keep,
        # exome_bait=args.bed,
        # quality_threshold=args.qc_threshold,
        # read_length=args.read_length,
        # desired_mean_coverage=args.desired_mean_coverage
    )
    # counts_file = downsampler.get_bam_counts()
    # keep = downsampler.calculate_keep(counts_file)
    downsampled_bam = downsampler.ds()
    final_bam = downsampler.remove_unpaired_reads(downsampled_bam)
    downsampler.bamtofastq(final_bam)
    return """

if __name__ == "__main__":
    pass
