import argparse
import json
import os
from multiprocessing import Pool


class GCNV:
    def __init__(
        self,
        input_json,
        output_dir,
        exome_loc,
        genome_fasta,
        ref_dict,
        contig_pp,
        class_coherence_length,
        cnv_coherence_length,
        min_contig_length,
        p_active,
        p_alt,
        interval_psi_scale,
        sample_psi_scale,
    ):
        self.input_json = input_json
        self.output_dir = output_dir
        self.exome_loc = exome_loc
        self.genome_fasta = genome_fasta
        self.ref_dict = ref_dict
        self.contig_pp = contig_pp
        self.class_coherence_length = class_coherence_length
        self.cnv_coherence_length = cnv_coherence_length
        self.min_contig_length = min_contig_length
        self.p_active = p_active
        self.p_alt = p_alt
        self.interval_psi_scale = interval_psi_scale
        self.sample_psi_scale = sample_psi_scale
        self.input_string = None
        self.filtered_il = None
        self.interval_list = None
        self.ann_interval_list = None
        self.bam_list = None

    def preprocess_intervals(self):
        gatkt = "PreprocessIntervals"
        imr = "OVERLAPPING_ONLY"

        self.interval_list = os.path.join(self.output_dir, "hg38_exome.preprocessed.interval_list")
        command = (
            f"gatk {gatkt} -R {self.genome_fasta} -L {self.exome_loc} --bin-length 0 -imr {imr} -O {self.interval_list}"
        )
        os.system(command)

    def annotate_intervals(self):
        gatkt = "AnnotateIntervals"
        imr = "OVERLAPPING_ONLY"

        self.ann_interval_list = os.path.join(self.output_dir, "hg38_exome.annotated.tsv")
        command = f"gatk {gatkt} -L {self.interval_list} -R {self.genome_fasta} -imr {imr} -O {self.ann_interval_list}"
        os.system(command)

    def run_gatk_collect_rc(self, args):
        bam_path, interval_list, genome_fasta = args
        bam_name = os.path.basename(bam_path)
        sample_name = os.path.splitext(bam_name)[0]
        output_name = sample_name + "_counts.tsv"
        gatkt = "CollectReadCounts"
        imr = "OVERLAPPING_ONLY"

        command = f"gatk {gatkt} -L {interval_list} -R {genome_fasta} -imr {imr} -I {bam_path} -O {os.path.join(self.output_dir, output_name)}"
        os.system(command)

    def get_bam_list(self):
        self.bam_list = []

        with open(self.input_json, "r") as f:
            data = json.load(f)

        self.bam_list = data.get("alignment_files", [])

        print(self.bam_list)

    def count_reads(self):
        arguments = [(bam_path, self.interval_list, self.genome_fasta) for bam_path in self.bam_list]

        try:
            with Pool(len(self.bam_list)) as pool:
                pool.map(self.run_gatk_collect_rc, arguments)

        except Exception as e:
            print(f"error: {e}")

    def get_input_string(self):
        input_string = ""

        self.clist = [
            os.path.join(self.output_dir, item) for item in os.listdir(self.output_dir) if item.endswith("_counts.tsv")
        ]  # 1

        for path in self.clist:
            input_string += f"-I {path} "

        self.input_string = input_string.strip()

        return self.input_string

    def filterintervals(self):
        self.filtered_il = os.path.join(self.output_dir, "cohort_filtered.interval_list")
        gatkt = "FilterIntervals"
        imr = "OVERLAPPING_ONLY"
        command = f"gatk {gatkt} -L {self.interval_list} --annotated-intervals {self.ann_interval_list} {self.input_string} -imr {imr} -O {self.filtered_il}"
        os.system(command)

    def determinecontig(self):
        gatkt = "DetermineGermlineContigPloidy"
        imr = "OVERLAPPING_ONLY"
        command = f"gatk {gatkt} -L {self.filtered_il} -imr {imr} {self.input_string} --contig-ploidy-priors {self.contig_pp} --output {self.output_dir} --output-prefix ploidy --verbosity DEBUG"
        os.system(command)

    def CNVCaller(self):
        gatkt = "GermlineCNVCaller"
        imr = "OVERLAPPING_ONLY"
        ploidy_calls = os.path.join(self.output_dir, "ploidy-calls")
        output = os.path.join(self.output_dir, "cnv-cohort")
        coherence_lengths = (
            f"--class-coherence-length {self.class_coherence_length} --cnv-coherence-length {self.cnv_coherence_length}"
        )
        p_scores = f"--p-active {self.p_active} --p-alt {self.p_alt}"
        psi_scores = f"--interval-psi-scale {self.interval_psi_scale} --sample-psi-scale {self.sample_psi_scale}"
        command = f"gatk {gatkt} --run-mode COHORT -L {self.filtered_il} -imr {imr} {self.input_string} --contig-ploidy-calls {ploidy_calls} --annotated-intervals {self.ann_interval_list} --output {output} --output-prefix cnv-cohort --verbosity DEBUG {coherence_lengths} {p_scores} {psi_scores}"
        print(command)
        os.system(command)

    def postprocess_sample(self):
        gatkt = "PostprocessGermlineCNVCalls"
        imr = "OVERLAPPING_ONLY"
        ploidy_calls = os.path.join(self.output_dir, "ploidy-calls")
        model = os.path.join(self.output_dir, "cnv-cohort", "cnv-cohort-model")
        calls = os.path.join(self.output_dir, "cnv-cohort", "cnv-cohort-calls")

        for i in range(len(self.clist)):
            with open(os.path.join(calls, f"SAMPLE_{i}", "sample_name.txt")) as file:
                name = file.read()
                name = name.strip()

            interval_output = os.path.join(self.output_dir, f"{name}_intervals.vcf.gz")
            segment_output = os.path.join(self.output_dir, f"{name}_segments.vcf.gz")
            denoised = os.path.join(self.output_dir, f"{name}_denoised_copy_ratios.tsv")

            command = f"gatk {gatkt} -imr {imr} --model-shard-path {model} --calls-shard-path {calls} --allosomal-contig chrX --allosomal-contig chrY --contig-ploidy-calls {ploidy_calls} --sample-index {i} --output-genotyped-intervals {interval_output} --output-genotyped-segments {segment_output} --output-denoised-copy-ratios {denoised} --sequence-dictionary {self.ref_dict}"
            print(command)
            os.system(command)

    def panel_of_normals(self):
        gatkt = "CreateReadCountPanelOfNormals"
        output = os.path.join(self.output_dir, "cnvpon.hdf5")
        opts = "--minimum-interval-median-percentile 5.0 --spark-master local[40]"

        command = f"gatk {gatkt} {self.input_string} {opts} -O {output}"

        os.system(command)

        return output

    def stardardize_denoise(self, pon):
        gatkt = "DenoiseReadCounts"
        counts_list = [item for item in os.listdir(self.output_dir) if item.endswith("_counts.tsv")]

        cr_list = []
        for item in counts_list:
            count_path = os.path.join(self.output_dir, item)
            item_prefix = item.split("_counts.tsv")[0]
            sdcr_output = os.path.join(self.output_dir, f"{item_prefix}_standardizedCR.tsv")
            dncr_output = os.path.join(self.output_dir, f"{item_prefix}_denoisedCR.tsv")
            cr_output = [item_prefix, sdcr_output, dncr_output]

            cpon = f"--count-panel-of-normals {pon}"
            sdcr = f"--standardized-copy-ratios {sdcr_output}"
            dncr = f"--denoised-copy-ratios {dncr_output}"

            command = f"gatk {gatkt} -I {count_path} {cpon} {sdcr} {dncr}"

            cr_list.append(cr_output)

            os.system(command)

        return cr_list

    def plot_pt1(self, copy_ratio_paths):
        gatkt = "PlotDenoisedCopyRatios"
        min_contig = f"--minimum-contig-length {self.min_contig_length}"
        output = f"--output {os.path.join(self.output_dir, 'plots')}"
        seq_dict = f"--sequence-dictionary {self.ref_dict}"

        for item in copy_ratio_paths:
            out_prefix = f"--output-prefix {item[0]}"
            sd_cr = f"--standardized-copy-ratios {item[1]}"
            dn_cr = f"--denoised-copy-ratios {item[2]}"

            command = f"gatk {gatkt} {sd_cr} {dn_cr} {seq_dict} {min_contig} {output} {out_prefix}"

            os.system(command)

    def run_gatk_collect_ac(self, args):
        bam_path, interval_list, genome_fasta = args
        bam_name = os.path.basename(bam_path)
        sample_name = os.path.splitext(bam_name)[0]
        output_name = sample_name + "_allelic_counts.tsv"
        gatkt = "CollectAllelicCounts"
        imr = "OVERLAPPING_ONLY"
        command = f"gatk {gatkt} -L {interval_list} -R {genome_fasta} -imr {imr} -I {bam_path} -O {os.path.join(self.output_dir, output_name)}"
        os.system(command)

    def allelic_counts(self):
        arguments = [(bam_path, self.filtered_il, self.genome_fasta) for bam_path in self.bam_list]

        try:
            with Pool(len(self.bam_list)) as pool:
                pool.map(self.run_gatk_collect_ac, arguments)

        except Exception as e:
            print(f"error: {e}")

    def run_gatk_model_segments(self, args):
        sample_name, sample_path, bam_dir = args
        gatkt = "ModelSegments"
        output_dir = os.path.join(bam_dir, "segmentation_results")

        output_prefix = f"--output-prefix {sample_name}"
        denoised = f"--denoised-copy-ratios {sample_path}_denoisedCR.tsv"
        ac = f"--allelic-counts {sample_path}_allelic_counts.tsv"

        command = f"gatk {gatkt} {denoised} {ac} --output {output_dir} {output_prefix}"
        os.system(command)

    def model_segments(self):
        arguments = [
            (
                os.path.splitext(os.path.basename(bam_path))[0],
                os.path.join(self.output_dir, os.path.splitext(os.path.basename(bam_path))[0]),
                self.output_dir,
            )
            for bam_path in self.bam_list
        ]

        try:
            with Pool(len(self.bam_list)) as pool:
                pool.map(self.run_gatk_model_segments, arguments)

        except Exception as e:
            print(f"error: {e}")

        return os.path.join(self.output_dir, "segmentation_results")

    def copy_ratio_segments(self, segment_folder):
        gatkt = "CallCopyRatioSegments"
        input_list = [item for item in os.listdir(segment_folder) if item.endswith(".cr.seg")]

        for item in input_list:
            input = f"--input {os.path.join(segment_folder, item)}"
            sample_name = item.split(".cr.seg")[0]
            output = f"--output {os.path.join(segment_folder, f'{sample_name}.called.seg')}"

            command = f"gatk {gatkt} {input} {output}"
            os.system(command)

    def plot_segments(self, segment_folder):
        gatkt = "PlotModeledSegments"
        output = os.path.join(self.output_dir, "plots_seg")

        for item in self.bam_list:
            sample_name = os.path.splitext(os.path.basename(item))[0]
            denoised = f"--denoised-copy-ratios {os.path.join(self.output_dir, f'{sample_name}_denoisedCR.tsv')}"
            ac = f"--allelic-counts {os.path.join(segment_folder, f'{sample_name}.hets.tsv')}"
            segments = f"--segments {os.path.join(segment_folder, f'{sample_name}.modelFinal.seg')}"
            seq_dict = f"--sequence-dictionary {self.ref_dict}"
            min_contig_l = f"--minimum-contig-length {self.min_contig_length}"
            output_folder = f"--output {output}"
            output_prefix = f"--output-prefix {sample_name}"

            command = (
                f"gatk {gatkt} {denoised} {ac} {segments} {seq_dict} {min_contig_l} {output_folder} {output_prefix}"
            )
            os.system(command)


def main():
    parser = argparse.ArgumentParser(description="Run GCNV pipeline.")
    parser.add_argument("--input_json", type=str, help="Paths to input bams")
    parser.add_argument("--output_dir", type=str, help="Path to output directory")
    parser.add_argument("--exome_loc", type=str, help="Path to exome BED file")
    parser.add_argument("--genome_fasta", type=str, help="Path to genome FASTA file")
    parser.add_argument("--ref_dict", type=str, help="Path to reference dictionary file")
    parser.add_argument("--contig_pp", type=str, help="Path to contig ploidy prior file")
    parser.add_argument(
        "--class_coherence_length",
        type=str,
        default="10000",
        help="Class coherence length",
    )
    parser.add_argument("--cnv_coherence_length", type=str, default="10000", help="CNV coherence length")
    parser.add_argument(
        "--min_contig_length",
        type=str,
        default="46709983",
        help="Minimum contig length",
    )
    parser.add_argument(
        "--p_active",
        type=str,
        default="0.01",
        help="Prior probability of treating an interval as CNV-active",
    )
    parser.add_argument(
        "--p_alt",
        type=str,
        default="0.000001",
        help="Total prior probability of alternative copy-number states",
    )
    parser.add_argument(
        "--interval_psi_scale",
        type=str,
        default="0.001",
        help="Typical scale of interval-specific unexplained variance",
    )
    parser.add_argument(
        "--sample_psi_scale",
        type=str,
        default="0.0001",
        help="Typical scale of sample-specific correction to the unexplained variance",
    )

    args = parser.parse_args()

    counts = GCNV(
        args.input_json,
        args.output_dir,
        args.exome_loc,
        args.genome_fasta,
        args.ref_dict,
        args.contig_pp,
        args.class_coherence_length,
        args.cnv_coherence_length,
        args.min_contig_length,
        args.p_active,
        args.p_alt,
        args.interval_psi_scale,
        args.sample_psi_scale,
    )

    counts.preprocess_intervals()
    counts.annotate_intervals()
    counts.get_bam_list()
    counts.count_reads()
    counts.get_input_string()
    counts.filterintervals()
    counts.determinecontig()
    counts.CNVCaller()
    counts.postprocess_sample()
    # pon = counts.panel_of_normals()
    # cr_list = counts.stardardize_denoise(pon)
    # counts.plot_pt1(cr_list)
    # counts.allelic_counts()
    # seg_dir = counts.model_segments()
    # counts.copy_ratio_segments(seg_dir)
    # counts.plot_segments(seg_dir)

def gatk_gcnv(
    input_json: str,
    output_dir: str,
    exome_loc: str,
    genome_fasta: str,
    ref_dict: str,
    contig_pp: str,
    class_coherence_length: str="10000",
    cnv_coherence_length: str="10000",
    min_contig_length: str="46709983",
    p_active: str="0.01",
    p_alt: str="0.000001",
    interval_psi_scale: str="0.001",
    sample_psi_scale: str="0.0001",
) -> None:
    """
    GATK GCNV pipeline.
    
    Args:
        input_json (str): Path to JSON file containing input BAM files.
        output_dir (str): Directory where output files will be saved.
        exome_loc (str): Path to BED file defining the exome regions.
        genome_fasta (str): Path to the reference genome FASTA file.
        ref_dict (str): Path to the reference dictionary file.
        contig_pp (str): Path to the contig ploidy prior file.
        class_coherence_length (str, optional): Class coherence length. Defaults to "10000".
        cnv_coherence_length (str, optional): CNV coherence length. Defaults to "10000".
        min_contig_length (str, optional): Minimum contig length. Defaults to "46709983".
        p_active (str, optional): Prior probability of treating an interval as CNV-active. Defaults to "0.01".
        p_alt (str, optional): Total prior probability of alternative copy-number states. Defaults to "0.000001".
        interval_psi_scale (str, optional): Scale of interval-specific unexplained variance. Defaults to "0.001".
        sample_psi_scale (str, optional): Scale of sample-specific correction to unexplained variance. Defaults to "0.0001".
    """
    counts = GCNV(
        input_json,
        output_dir,
        exome_loc,
        genome_fasta,
        ref_dict,
        contig_pp,
        class_coherence_length,
        cnv_coherence_length,
        min_contig_length,
        p_active,
        p_alt,
        interval_psi_scale,
        sample_psi_scale,
    )

    counts.preprocess_intervals()
    counts.annotate_intervals()
    counts.get_bam_list()
    counts.count_reads()
    counts.get_input_string()
    counts.filterintervals()
    counts.determinecontig()
    counts.CNVCaller()
    counts.postprocess_sample()
    # pon = counts.panel_of_normals()
    # cr_list = counts.stardardize_denoise(pon)
    # counts.plot_pt1(cr_list)
    # counts.allelic_counts()
    # seg_dir = counts.model_segments()
    # counts.copy_ratio_segments(seg_dir)
    # counts.plot_segments(seg_dir)
    return None

if __name__ == "__main__":
    main()
