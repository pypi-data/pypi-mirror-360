import logging
import os
import subprocess

import pandas as pd

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
        self.filtered_bam_file = self.sample_id + ".bam"
        self.filtered_bam = os.path.join(self.out_path, self.filtered_bam_file)
        self.metrics_file = self.sample_id + "_dup_metrics.txt"
        self.metrics_path = os.path.join(self.out_path, self.metrics_file)
        self.sorted_bam_file = "sorted_" + self.sample_id + ".bam"
        self.sorted_bam = os.path.join(self.out_path, self.sorted_bam_file)

    def sort_bam(self):
        sort_cmd = f"samtools sort -@ {self.threads} {self.sam_path} -o {self.sorted_bam}"

        try:
            os.system(sort_cmd)
            logging.info(f"Samtools - Successfully sorted bam file for {self.sample_id} > {self.sorted_bam}")
        except Exception as e:
            logging.error(f"Samtools - An error occurred while sorting bam file for {self.sample_id}: {e}")

    def mark_duplicates(self):
        if self.use_mark_duplicates:
            logging.info(f"MarkDuplicatesSpark - Marking and removing duplicates for bam file of {self.sample_id}")
            marker_cmd = f"gatk MarkDuplicatesSpark -I {self.sorted_bam} -O {self.filtered_bam} --metrics-file {self.metrics_path} --spark-master local[{self.threads}]"

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
            marker_cmd = f"sambamba markdup -t {self.threads} {self.sorted_bam} {self.filtered_bam}"

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

        return self.filtered_bam

    def index_bam(self):
        index_cmd = f"samtools index -@ {self.threads} {self.filtered_bam}"

        try:
            os.system(index_cmd)
            logging.info(f"Samtools - Successfully indexed bam file for {self.sample_id} > {self.filtered_bam}")
        except Exception as e:
            logging.error(f"Samtools - An error occurred while indexing bam file for {self.sample_id}: {e}")

    def clean_up(self):
        try:
            os.remove(self.sam_path)
            os.remove(self.sorted_bam)
            logging.info(f"Clean up - Successfully removed intermediate files for {self.sample_id}")
        except Exception as e:
            logging.error(f"Clean up - An error occurred while removing intermediate files for {self.sample_id}: {e}")

    def convert_markdedup(self):
        self.sort_bam()
        resulting_bam = self.mark_duplicates()
        self.index_bam()
        self.clean_up()

        return resulting_bam, self.out_path


class CoverageAnalysis:
    def __init__(self, reference, bam, sample_id, output_dir, bed, max_worker=40):
        self.reference = reference
        self.bed = bed
        self.bam = bam
        self.output_dir = output_dir
        self.max_worker = max_worker
        self.sample_name = sample_id

    def run_mosdepth(self):
        output = os.path.join(self.output_dir, self.sample_name)

        command = [
            "mosdepth",
            output,
            f"-x -Q 1 -t {self.max_worker}",
            "--by",
            self.bed,
            f"-f {self.reference}",
            f"-n -T 1,5,10,15,20,30,50,100,500,1500",
            self.bam,
        ]
        subprocess.run(" ".join(command), shell=True)

        thresholds = os.path.join(self.output_dir, self.sample_name + ".thresholds.bed.gz")
        summary = os.path.join(self.output_dir, self.sample_name + ".mosdepth.summary.txt")

        return thresholds, summary

    def calculate_coverages(self, qc_thresholds_file):
        result = []
        df = pd.read_csv(qc_thresholds_file, compression="gzip", header=None, sep="\t")
        columns = df.iloc[0].to_list()
        df = df.drop(df.index[0])
        df.columns = columns
        df["size"] = df["end"].astype(int) - df["start"].astype(int)

        total_size = df["size"].sum()
        print(total_size)

        # Coverage columns
        coverage_columns = [col for col in df.columns if col.endswith("X")]

        # Calculate the sum of each coverage column and then calculate coverage
        coverage_dict = {}
        for col in coverage_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(int)
            coverage_sum = df[col].sum()
            coverage = coverage_sum / total_size
            coverage_dict[col] = coverage

        # Display the coverage values
        for col, cov in coverage_dict.items():
            result.append(
                {
                    "key": f"PCT of QC coverage region with coverage [{col.lower()}: inf):",
                    "value": round(cov * 100, 2),
                }
            )

        coverage_keys = list(coverage_dict.keys())
        for i in range(len(coverage_keys) - 1):
            diff = df[coverage_keys[i]] - df[coverage_keys[i + 1]]
            result.append(
                {
                    "key": f"PCT of QC coverage region with coverage [{coverage_keys[i].lower()}:{coverage_keys[i + 1].lower()}):",
                    "value": round((diff.sum() / total_size) * 100, 2),
                }
            )

        return result

    def OnTargetContigs(self, depth_summary):
        df = pd.read_csv(depth_summary, sep="\t")
        df = df.iloc[:50]
        # Select values without _region. all chromosomes
        df1 = df[~df["chrom"].str.endswith("_region")]
        total_bases = df1["bases"].astype(int).sum()

        # Select target regions only
        df = df[df["chrom"].str.endswith("_region")]
        df["chrom"] = df["chrom"].str.replace("_region", "")
        target_total_bases = df["bases"].astype(int).sum()
        target_length = df["length"].astype(int).sum()
        mean_coverage = round(target_total_bases / target_length, 2)

        df = df.drop(["length", "bases", "min", "max"], axis=1)

        df.columns = ["key", "value"]
        # uniformity_2 = sum(1 for x in total if x > 0.2 * mean_coverage) / total_bases * 100
        # uniformity_4 = sum(1 for x in total if x > 0.4 * mean_coverage) / total_bases * 100
        final_result = [
            {"key": "Aligned bases", "value": total_bases},
            {"key": "Aligned bases in QC coverage region", "value": target_total_bases},
            {
                "key": "Average alignment coverage over QC coverage region",
                "value": mean_coverage,
            },
            # {"key": "Uniformity of coverage (PCT > 0.2*mean)", "value": uniformity_2},
            # {"key": "Uniformity of coverage (PCT > 0.4*mean)", "value": uniformity_4},
            {"key": "PCT of QC coverage region with coverage [0x: inf):", "value": 100},
        ]
        return df.to_dict(orient="records"), final_result

    def process(self):
        try:
            logging.info(f"Starting process for sample: {self.sample_name}")

            qc_thresholds_file, depth_summary_file = self.run_mosdepth()
            logging.info(f"Generated Mosdepth output: thresholds: {qc_thresholds_file}, summary: {depth_summary_file}")

            if os.path.exists(qc_thresholds_file):
                logging.info(f"Found thresholds file: {qc_thresholds_file}, proceeding to calculate coverages")
                metrics = self.calculate_coverages(qc_thresholds_file)
            else:
                logging.error(f"Thresholds file not found: {qc_thresholds_file}")
                return

            if os.path.exists(depth_summary_file):
                logging.info(f"Found summary file: {depth_summary_file}, proceeding to OnTargetContigs")
                _, final_results = self.OnTargetContigs(depth_summary_file)
                metrics.extend(final_results)
            else:
                logging.error(f"Summary file not found: {depth_summary_file}")
                return

            output_metrics_file = os.path.join(self.output_dir, f"{self.sample_name}_metrics.txt")
            logging.info(f"Writing metrics to file: {output_metrics_file}")

            with open(output_metrics_file, "w") as f:
                for metric in metrics:
                    f.write(f"{metric['key']} {metric['value']}\n")
            logging.info(f"Successfully wrote metrics for {self.sample_name}")

        except Exception as e:
            logging.error(
                f"An error occurred while processing {self.sample_name}: {e}",
                exc_info=True,
            )


# TODO: MOVE
def bwa_dedup(
    ref_fasta:str,
    bed_file:str,
    out_path:str,
    r1:str,
    r2:str,
    sample_name:str,
    *,
    at:str="bwtsw",
    threads:int=40,
    remove_dups:bool=False,
    remove_seq_dups:bool=False,
    use_md=False,
) -> None:
    """
    Run BWA mapping, deduplication, and coverage analysis using Mosdepth.

    Parameters:
    - ref_fasta: Path to the reference FASTA file.
    - bed_file: Path to the BED file for coverage analysis.
    - at: Algorithm type for BWA indexing (default is 'bwtsw').
    - out_path: Output directory for results.
    - r1: Path to the first read FASTQ file.
    - r2: Path to the second read FASTQ file.
    - sample_name: Sample identifier for output files.
    - threads: Number of threads to use for processing.
    - remove_dups: Whether to remove all duplicates (default is False).
    - remove_seq_dups: Whether to remove sequencing duplicates (default is False).
    - use_md: Whether to use MarkDuplicatesSpark (default is False).
    """
    # indexit = Indexer(reference_fasta=ref_fasta, algotype=at) # use once
    # indexit.index() # use once

    mapit = Mapper(
        reference_fasta=ref_fasta,
        sample_id=sample_name,
        r1=r1,
        r2=r2,
        output_path=out_path,
        threads=threads,
    )
    sam_file = mapit.map()

    dedup = BAMConverter(
        sam_path=sam_file,
        sample_id=sample_name,
        threads=threads,
        remove_all_duplicates=remove_dups,
        remove_sequencing_duplicates=remove_seq_dups,
        use_mark_duplicates=use_md,
    )
    final_bam, out_path_metrics = dedup.convert_markdedup()

    coverage_analysis = CoverageAnalysis(
        reference=ref_fasta,
        bam=final_bam,
        sample_id=sample_name,
        output_dir=out_path_metrics,
        bed=bed_file,
        max_worker=threads,
    )
    coverage_analysis.process()

    return