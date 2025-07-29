import argparse
import importlib.metadata
import json
import shutil
from pathlib import Path

import argcomplete
from rich import print as rprint
from rich_argparse import RichHelpFormatter

from bipackage.autocomplete import _tab_autocomplete
from bipackage.pipelines import bwa_dedup, gatk_gcnv, pon, snv_indel, somatic_CNV
from bipackage.pipelines.defaults import bwa_dedup_config, cnv_config, cnv_pon_config, gatk_gcnv_config, snv_ind_config

RichHelpFormatter.styles["argparse.args"] = "bold dodger_blue1"
RichHelpFormatter.styles["argparse.groups"] = "bold deep_pink2"
RichHelpFormatter.styles["argparse.help"] = "grey82"
RichHelpFormatter.styles["argparse.metavar"] = "orange_red1"
RichHelpFormatter.styles["argparse.prog"] = "bold grey85"
RichHelpFormatter.styles["argparse.syntax"] = "bold bright_white"
RichHelpFormatter.styles["argparse.text"] = "bold grey70"
RichHelpFormatter.styles["argparse.default"] = "italic"

_tab_autocomplete()

def _dict_print(dict_obj: dict, command: str) -> None:
    rprint(f"[green]Running `bipipe {command}` with ...[/green]")
    for key, value in dict_obj.items():
        if isinstance(value, (int, float)):
            rprint(f"[grey85]{key}[/grey85] : [dark_orange]{value}[/dark_orange]")
        elif isinstance(value, str):
            rprint(f"[grey85]{key}[/grey85] : [white]{value}[/white]")
        elif isinstance(value, bool):
            rprint(f"[grey85]{key}[/grey85] : [orchid1]{value}[/orchid1]")
        elif isinstance(value, list):
            rprint(f"[grey85]{key}[/grey85] : [cyan]{', '.join(map(str, value))}[/cyan]")
        else:
            rprint(f"[grey85]{key}[/grey85] : [grey23]{value}[/grey23]")


def _print_not_found_keys(not_found_keys: list) -> None:
    msg = (
        f"\n[bold red]REQUIRED KEYS NOT FOUND IN CONFIG FILE OR COMMAND LINE ARGUMENTS...[/bold red]\n"
        f"[bold red]PLEASE PROVIDE THE FOLLOWING KEYS IN YOUR CONFIG FILE OR COMMAND LINE ARGUMENTS:[/bold red]\n"
        f"\n([cyan]{', '.join(not_found_keys)}[/cyan])\n"
    )
    rprint(msg)


def bring_config(config: str) -> None:
    entry_dir = Path(__file__).parent.parent
    config_path = entry_dir / "configs" / f"{config}.json"
    # copy config file to current directory
    if config_path.exists():
        shutil.copy(config_path, Path(".") / f"{config}.json")
    else:
        rprint(f"[bold red]Configuration file `{config}.json` not found in {entry_dir / 'configs'}[/bold red]")
        rprint("[bold green]Available configurations:[/bold green]")
        for file in (entry_dir / "configs").glob("*.json"):
            rprint(f"[grey85]{file.stem}[/grey85]")

    return


def main():
    parser = argparse.ArgumentParser(
        description="BIPackage Pipelines Entry Point",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"bipipe {importlib.metadata.version('bipackage')}",
    )

    subparsers = parser.add_subparsers(dest="command")

    # ------------------------------------BWA DEDUP SUBPARSER ------------------------------------
    bwadedup_subparser = subparsers.add_parser(
        "bwa_dedup",
        help="Run the bwa_dedup_sp_qc_mosdepth pipeline.",
        formatter_class=RichHelpFormatter,
    )
    bwadedup_subparser.add_argument(
        "--config",
        type=str,
        # required=True,
        help="Path to the configuration file for the bwa_dedup_sp_qc_mosdepth pipeline.",
    )
    bwadedup_subparser.add_argument(
        "--ref_fasta",
        type=str,
        help="Path to the reference FASTA file.",
    )
    bwadedup_subparser.add_argument(
        "--bed_file",
        type=str,
        help="Path to the BED file for coverage analysis.",
    )
    bwadedup_subparser.add_argument(
        "--at",
        type=str,
        default="bwtsw",
        help="Algorithm type for BWA indexing (default is 'bwtsw').",
    )
    bwadedup_subparser.add_argument(
        "--out_path",
        type=str,
        help="Output directory for results.",
    )
    bwadedup_subparser.add_argument(
        "--r1",
        type=str,
        help="Path to the first read FASTQ file.",
    )
    bwadedup_subparser.add_argument(
        "--r2",
        type=str,
        help="Path to the second read FASTQ file.",
    )
    bwadedup_subparser.add_argument(
        "--sample_name",
        type=str,
        help="Sample identifier for output files.",
    )
    bwadedup_subparser.add_argument(
        "--threads",
        type=int,
        help="Number of threads to use for processing.",
    )
    bwadedup_subparser.add_argument(
        "--remove_dups",
        action="store_true",
        help="Whether to remove all duplicates (default is False).",
    )
    bwadedup_subparser.add_argument(
        "--remove_seq_dups",
        action="store_true",
        help="Whether to remove sequencing duplicates (default is False).",
    )
    bwadedup_subparser.add_argument(
        "--use_md",
        action="store_true",
        help="Whether to use MarkDuplicatesSpark (default is False).",
    )
    # ------------------------------------ GATK GCNV SUBPARSER ------------------------------------
    gatk_gcnv_subparser = subparsers.add_parser(
        "gatk_gcnv",
        help="Run the GATK GCNV pipeline.",
        formatter_class=RichHelpFormatter,
    )
    gatk_gcnv_subparser.add_argument(
        "--config",
        type=str,
        # required=True,
        help="Path to the configuration file for the GATK GCNV pipeline.",
    )
    gatk_gcnv_subparser.add_argument(
        "--input_json",
        type=str,
        help="Paths to input bams (JSON file)",
    )
    gatk_gcnv_subparser.add_argument(
        "--output_dir",
        type=str,
        help="Path to output directory",
    )
    gatk_gcnv_subparser.add_argument(
        "--exome_loc",
        type=str,
        help="Path to exome BED file",
    )
    gatk_gcnv_subparser.add_argument(
        "--genome_fasta",
        type=str,
        help="Path to genome FASTA file",
    )
    gatk_gcnv_subparser.add_argument(
        "--ref_dict",
        type=str,
        help="Path to reference dictionary file",
    )
    gatk_gcnv_subparser.add_argument(
        "--contig_pp",
        type=str,
        help="Path to contig ploidy prior file",
    )
    gatk_gcnv_subparser.add_argument(
        "--class_coherence_length",
        type=str,
        help="Class coherence length",
    )
    gatk_gcnv_subparser.add_argument(
        "--cnv_coherence_length",
        type=str,
        help="CNV coherence length",
    )
    gatk_gcnv_subparser.add_argument(
        "--min_contig_length",
        type=str,
        help="Minimum contig length",
    )
    gatk_gcnv_subparser.add_argument(
        "--p_active",
        type=str,
        help="Prior probability of treating an interval as CNV-active",
    )
    gatk_gcnv_subparser.add_argument(
        "--p_alt",
        type=str,
        help="Total prior probability of alternative copy-number states",
    )
    gatk_gcnv_subparser.add_argument(
        "--interval_psi_scale",
        type=str,
        help="Typical scale of interval-specific unexplained variance",
    )
    gatk_gcnv_subparser.add_argument(
        "--sample_psi_scale",
        type=str,
        help="Typical scale of sample-specific correction to the unexplained variance",
    )
    # ------------------------------------ PON SUBPARSER ------------------------------------
    pon_subparser = subparsers.add_parser(
        "cnv_pon",
        help="Run the Panel of Normals (PON) pipeline.",
        formatter_class=RichHelpFormatter,
    )
    pon_subparser.add_argument(
        "--config",
        type=str,
        # required=True,
        help="Path to the configuration file for the PON pipeline.",
    )
    pon_subparser.add_argument(
        "--output_folder",
        type=str,
        help="Output folder for results.",
    )
    pon_subparser.add_argument(
        "--ref_fasta",
        type=str,
        help="Path to the reference FASTA file.",
    )
    pon_subparser.add_argument(
        "--ref_dict",
        type=str,
        help="Path to the reference dictionary file.",
    )
    pon_subparser.add_argument(
        "--interval_list",
        type=str,
        help="Path to the interval list file.",
    )
    pon_subparser.add_argument(
        "--pon_id",
        type=str,
        help="Panel of Normals ID.",
    )
    pon_subparser.add_argument(
        "--normal_bams",
        nargs="+",
        type=str,
        help="List of normal BAM files.",
    )
    pon_subparser.add_argument(
        "--gc_correction",
        action="store_true",
        help="Enable GC correction.",
    )
    pon_subparser.add_argument(
        "--bin_length",
        type=int,
        help="Bin length.",
    )
    pon_subparser.add_argument(
        "--blacklist_intervals",
        type=str,
        help="Path to blacklist intervals file.",
    )
    pon_subparser.add_argument(
        "--padding",
        type=int,
        help="Padding value.",
    )
    pon_subparser.add_argument(
        "--do_impute_zeros",
        action="store_true",
        help="Impute zeros.",
    )
    pon_subparser.add_argument(
        "--number_of_eigensamples",
        type=int,
        help="Number of eigensamples.",
    )
    pon_subparser.add_argument(
        "--feature_query_lookahead",
        type=int,
        help="Feature query lookahead.",
    )
    pon_subparser.add_argument(
        "--minimum_interval_median_percentile",
        type=float,
        help="Minimum interval median percentile.",
    )
    pon_subparser.add_argument(
        "--maximum_zeros_in_sample_percentage",
        type=float,
        help="Maximum zeros in sample percentage.",
    )
    pon_subparser.add_argument(
        "--maximum_zeros_in_interval_percentage",
        type=float,
        help="Maximum zeros in interval percentage.",
    )
    pon_subparser.add_argument(
        "--extreme_sample_median_percentile",
        type=float,
        help="Extreme sample median percentile.",
    )
    pon_subparser.add_argument(
        "--extreme_outlier_truncation_percentile",
        type=float,
        help="Extreme outlier truncation percentile.",
    )
    pon_subparser.add_argument(
        "--maximum_chunk_size",
        type=int,
        help="Maximum chunk size.",
    )
    # ------------------------------------ SNV/INDEL SUBPARSER ------------------------------------
    snv_ind_subparser = subparsers.add_parser(
        "snv_indel",
        help="Run the SNV/Indel pipeline.",
        formatter_class=RichHelpFormatter,
    )
    snv_ind_subparser.add_argument(
        "--config",
        type=str,
        # required=True,
        help="Path to the configuration file for the SNV/Indel pipeline.",
    )
    snv_ind_subparser.add_argument(
        "--algotype",
        type=str,
        help="Algorithm type for BWA indexing.",
    )
    snv_ind_subparser.add_argument(
        "--index_fasta",
        action="store_true",
        help="Whether to index the FASTA file.",
    )
    snv_ind_subparser.add_argument(
        "--aligner_threads",
        type=int,
        help="Number of threads for the aligner.",
    )
    snv_ind_subparser.add_argument(
        "--remove_all_duplicates",
        action="store_true",
        help="Remove all duplicates.",
    )
    snv_ind_subparser.add_argument(
        "--remove_sequencing_duplicates",
        action="store_true",
        help="Remove sequencing duplicates.",
    )
    snv_ind_subparser.add_argument(
        "--use_gatk_mark_duplicates",
        action="store_true",
        help="Use GATK MarkDuplicates.",
    )
    snv_ind_subparser.add_argument(
        "--use_dragen",
        action="store_true",
        help="Use DRAGEN.",
    )
    snv_ind_subparser.add_argument(
        "--output_folder",
        type=str,
        help="Output folder for results.",
    )
    snv_ind_subparser.add_argument(
        "--run_name",
        type=str,
        help="Run name.",
    )
    snv_ind_subparser.add_argument(
        "--ref_fasta",
        type=str,
        help="Path to the reference FASTA file.",
    )
    snv_ind_subparser.add_argument(
        "--ref_dict",
        type=str,
        help="Path to the reference dictionary file.",
    )
    snv_ind_subparser.add_argument(
        "--interval_list",
        type=str,
        help="Path to the interval list file.",
    )
    snv_ind_subparser.add_argument(
        "--scatter_count",
        type=int,
        help="Scatter count.",
    )
    snv_ind_subparser.add_argument(
        "--germline_resource",
        type=str,
        help="Path to the germline resource VCF.",
    )
    snv_ind_subparser.add_argument(
        "--index_image",
        type=str,
        help="Path to the index image.",
    )
    snv_ind_subparser.add_argument(
        "--downsampling_stride",
        type=int,
        help="Downsampling stride.",
    )
    snv_ind_subparser.add_argument(
        "--panel_of_normals",
        type=str,
        help="Panel of normals file.",
    )
    snv_ind_subparser.add_argument(
        "--variants_for_contamination",
        type=str,
        help="Variants for contamination file.",
    )
    snv_ind_subparser.add_argument(
        "--max_reads_per_alignment_start",
        type=int,
        help="Max reads per alignment start.",
    )
    snv_ind_subparser.add_argument(
        "--max_suspicious_reads_per_alignment_start",
        type=int,
        help="Max suspicious reads per alignment start.",
    )
    snv_ind_subparser.add_argument(
        "--max_population_af",
        type=float,
        help="Max population allele frequency.",
    )
    snv_ind_subparser.add_argument(
        "--lrom",
        action="store_true",
        help="Enable LROM.",
    )
    snv_ind_subparser.add_argument(
        "--interval_padding",
        type=int,
        help="Interval padding.",
    )
    snv_ind_subparser.add_argument(
        "--tumor_samples",
        type=str,
        help="JSON string or path to tumor samples list.",
    )
    snv_ind_subparser.add_argument(
        "--normal_samples",
        type=str,
        help="JSON string or path to normal samples list.",
    )
    # ------------------------------------ CNV SUBPARSER ------------------------------------
    cnv_config_subparser = subparsers.add_parser(
        "cnv",
        help="Run the CNV pipeline.",
        formatter_class=RichHelpFormatter,
    )
    cnv_config_subparser.add_argument(
        "--config",
        type=str,
        # required=True,
        help="Path to the configuration file for the CNV pipeline.",
    )
    cnv_config_subparser.add_argument(
        "--algotype",
        type=str,
        help="Algorithm type for BWA indexing.",
    )
    cnv_config_subparser.add_argument(
        "--index_fasta",
        action="store_true",
        help="Whether to index the FASTA file.",
    )
    cnv_config_subparser.add_argument(
        "--aligner_threads",
        type=int,
        help="Number of threads for the aligner.",
    )
    cnv_config_subparser.add_argument(
        "--remove_all_duplicates",
        action="store_true",
        help="Remove all duplicates.",
    )
    cnv_config_subparser.add_argument(
        "--remove_sequencing_duplicates",
        action="store_true",
        help="Remove sequencing duplicates.",
    )
    cnv_config_subparser.add_argument(
        "--use_gatk_mark_duplicates",
        action="store_true",
        help="Use GATK MarkDuplicates.",
    )
    cnv_config_subparser.add_argument(
        "--use_dragen",
        action="store_true",
        help="Use DRAGEN.",
    )
    cnv_config_subparser.add_argument(
        "--output_folder",
        type=str,
        help="Output folder for results.",
    )
    cnv_config_subparser.add_argument(
        "--run_name",
        type=str,
        help="Run name.",
    )
    cnv_config_subparser.add_argument(
        "--ref_fasta",
        type=str,
        help="Path to the reference FASTA file.",
    )
    cnv_config_subparser.add_argument(
        "--ref_dict",
        type=str,
        help="Path to the reference dictionary file.",
    )
    cnv_config_subparser.add_argument(
        "--interval_list",
        type=str,
        help="Path to the interval list file.",
    )
    cnv_config_subparser.add_argument(
        "--common_sites",
        type=str,
        help="Path to the common sites interval list.",
    )
    cnv_config_subparser.add_argument(
        "--pon",
        type=str,
        help="Panel of normals HDF5 file.",
    )
    cnv_config_subparser.add_argument(
        "--blacklist_intervals",
        type=str,
        help="Path to blacklist intervals file.",
    )
    cnv_config_subparser.add_argument(
        "--minimum_base_quality",
        type=int,
        help="Minimum base quality.",
    )
    cnv_config_subparser.add_argument(
        "--number_of_eigensamples",
        type=int,
        help="Number of eigensamples.",
    )
    cnv_config_subparser.add_argument(
        "--minimum_total_allele_count_case",
        type=int,
        help="Minimum total allele count (case).",
    )
    cnv_config_subparser.add_argument(
        "--minimum_total_allele_count_normal",
        type=int,
        help="Minimum total allele count (normal).",
    )
    cnv_config_subparser.add_argument(
        "--genotyping_homozygous_log_ratio_threshold",
        type=float,
        help="Genotyping homozygous log ratio threshold.",
    )
    cnv_config_subparser.add_argument(
        "--genotyping_base_error_rate",
        type=float,
        help="Genotyping base error rate.",
    )
    cnv_config_subparser.add_argument(
        "--maximum_number_of_segments_per_chromosome",
        type=int,
        help="Max segments per chromosome.",
    )
    cnv_config_subparser.add_argument(
        "--kernel_variance_copy_ratio",
        type=float,
        help="Kernel variance copy ratio.",
    )
    cnv_config_subparser.add_argument(
        "--kernel_variance_allele_fraction",
        type=float,
        help="Kernel variance allele fraction.",
    )
    cnv_config_subparser.add_argument(
        "--kernel_scaling_allele_fraction",
        type=float,
        help="Kernel scaling allele fraction.",
    )
    cnv_config_subparser.add_argument(
        "--kernel_approximation_dimension",
        type=int,
        help="Kernel approximation dimension.",
    )
    cnv_config_subparser.add_argument(
        "--window_size",
        nargs="+",
        type=int,
        help="Window sizes.",
    )
    cnv_config_subparser.add_argument(
        "--number_of_changepoints_penalty_factor",
        type=float,
        help="Changepoints penalty factor.",
    )
    cnv_config_subparser.add_argument(
        "--minor_allele_fraction_prior_alpha",
        type=float,
        help="Minor allele fraction prior alpha.",
    )
    cnv_config_subparser.add_argument(
        "--number_of_samples_copy_ratio",
        type=int,
        help="Number of samples (copy ratio).",
    )
    cnv_config_subparser.add_argument(
        "--number_of_burn_in_samples_copy_ratio",
        type=int,
        help="Burn-in samples (copy ratio).",
    )
    cnv_config_subparser.add_argument(
        "--number_of_samples_allele_fraction",
        type=int,
        help="Number of samples (allele fraction).",
    )
    cnv_config_subparser.add_argument(
        "--number_of_burn_in_samples_allele_fraction",
        type=int,
        help="Burn-in samples (allele fraction).",
    )
    cnv_config_subparser.add_argument(
        "--smoothing_credible_interval_threshold_copy_ratio",
        type=float,
        help="Smoothing credible interval threshold (copy ratio).",
    )
    cnv_config_subparser.add_argument(
        "--smoothing_credible_interval_threshold_allele_fraction",
        type=float,
        help="Smoothing credible interval threshold (allele fraction).",
    )
    cnv_config_subparser.add_argument(
        "--maximum_number_of_smoothing_iterations",
        type=int,
        help="Max smoothing iterations.",
    )
    cnv_config_subparser.add_argument(
        "--number_of_smoothing_iterations_per_fit",
        type=int,
        help="Smoothing iterations per fit.",
    )
    cnv_config_subparser.add_argument(
        "--neutral_segment_copy_ratio_lower_bound",
        type=float,
        help="Neutral segment copy ratio lower bound.",
    )
    cnv_config_subparser.add_argument(
        "--neutral_segment_copy_ratio_upper_bound",
        type=float,
        help="Neutral segment copy ratio upper bound.",
    )
    cnv_config_subparser.add_argument(
        "--outlier_neutral_segment_copy_ratio_z_score_threshold",
        type=float,
        help="Outlier neutral segment copy ratio z-score threshold.",
    )
    cnv_config_subparser.add_argument(
        "--calling_copy_ratio_z_score_threshold",
        type=float,
        help="Calling copy ratio z-score threshold.",
    )
    cnv_config_subparser.add_argument(
        "--minimum_contig_length",
        type=int,
        help="Minimum contig length.",
    )
    cnv_config_subparser.add_argument(
        "--maximum_copy_ratio",
        type=float,
        help="Maximum copy ratio.",
    )
    cnv_config_subparser.add_argument(
        "--point_size_copy_ratio",
        type=int,
        help="Point size (copy ratio).",
    )
    cnv_config_subparser.add_argument(
        "--point_size_allele_fraction",
        type=int,
        help="Point size (allele fraction).",
    )
    cnv_config_subparser.add_argument(
        "--tumor_samples",
        type=str,
        help="JSON string or path to tumor samples list.",
    )
    cnv_config_subparser.add_argument(
        "--normal_samples",
        type=str,
        help="JSON string or path to normal samples list.",
    )
    # ------------------------------------ GET CONFIG SUBPARSER ------------------------------------
    get_config_subparser = subparsers.add_parser(
        "get-config",
        help="Get examples pipeline configurations in json format.",
        formatter_class=RichHelpFormatter,
    )
    get_config_subparser.add_argument(
        "configs",
        nargs="*",
    )
    # PARSE ARGS
    argcomplete.autocomplete(parser, always_complete_options=True)
    args = parser.parse_args()

    # ============================ BWA DEDUP SUBPARSER ============================
    if args.command == "bwa_dedup":
        # BWA DEDUP required keys
        bwa_required_keys = [
            "ref_fasta",
            "bed_file",
            "out_path",
            "r1",
            "r2",
            "sample_name",
        ]
        # Load config if provided
        config = {}
        if args.config:
            with open(args.config) as f:
                config = json.load(f)

        # Overwrite defaults with config values only
        bwa_dedup_config.update({k: v for k, v in config.items() if v is not None})

        # Then overwrite with command line args
        for key, value in vars(args).items():
            if value is not None and key != "command":
                bwa_dedup_config[key] = value

        _dict_print(bwa_dedup_config, command=args.command)
        # Check for required keys
        not_found_keys = [key for key in bwa_required_keys if bwa_dedup_config[key] is None]
        if not_found_keys:
            _print_not_found_keys(not_found_keys)
        else:
            bwa_dedup(**bwa_dedup_config)  # acceptes kwargs as config

    # ============================ GATK GCNV SUBPARSER ============================
    elif args.command == "gatk_gcnv":
        # GATK GCNV required keys
        gatk_gcnv_required_keys = [
            "input_json",
            "output_dir",
            "exome_loc",
            "genome_fasta",
            "ref_dict",
            "contig_pp",
        ]
        # Load config if provided
        config = {}
        if args.config:
            with open(args.config) as f:
                config = json.load(f)

        # Overwrite defaults with config values only
        gatk_gcnv_config.update({k: v for k, v in config.items() if v is not None})

        # Then overwrite with command line args
        for key, value in vars(args).items():
            if value is not None and key != "command":
                gatk_gcnv_config[key] = value

        _dict_print(gatk_gcnv_config, command=args.command)
        # Check for required keys
        not_found_keys = [key for key in gatk_gcnv_required_keys if gatk_gcnv_config[key] is None]
        if not_found_keys:
            _print_not_found_keys(not_found_keys)
        else:
            gatk_gcnv(**gatk_gcnv_config)  # acceptes kwargs as config

    # ============================ PON SUBPARSER ============================
    elif args.command == "cnv_pon":
        # PON required keys
        pon_required_keys = [
            "output_folder",
            "ref_fasta",
            "ref_dict",
            "interval_list",
            "pon_id",
            "normal_bams",
            "blacklist_intervals",
        ]

        # Load config if provided
        config = {}
        if args.config:
            with open(args.config) as f:
                config = json.load(f)

        # Overwrite defaults with config values only
        cnv_pon_config.update({k: v for k, v in config.items() if v is not None})

        # Then overwrite with command line args
        for key, value in vars(args).items():
            if value is not None and key != "command":
                cnv_pon_config[key] = value

        _dict_print(cnv_pon_config, command=args.command)
        # Check for required keys
        not_found_keys = [key for key in pon_required_keys if cnv_pon_config[key] is None]
        if not_found_keys:
            _print_not_found_keys(not_found_keys)
        else:
            pon(**cnv_pon_config)  # acceptes kwargs as config

    # ============================ SNV/INDEL SUBPARSER ============================
    elif args.command == "snv_indel":
        # SNV/INDEL required keys
        snv_ind_required_keys = [
            "output_folder",
            "run_name",
            "ref_fasta",
            "ref_dict",
            "interval_list",
            "germline_resource",
            "index_image",
            "tumor_samples",
            "normal_samples",
        ]

        # Load config if provided
        config = {}
        if args.config:
            with open(args.config) as f:
                config = json.load(f)

        # Overwrite defaults with config values only
        snv_ind_config.update({k: v for k, v in config.items() if v is not None})

        # Then overwrite with command line args
        for key, value in vars(args).items():
            if value is not None and key != "command":
                snv_ind_config[key] = value

        _dict_print(snv_ind_config, command=args.command)
        # Check for required keys
        not_found_keys = [key for key in snv_ind_required_keys if snv_ind_config[key] is None]
        if not_found_keys:
            _print_not_found_keys(not_found_keys)
        else:
            snv_indel(snv_ind_config)  # accepts dictionary as config

    # ============================ CNV SUBPARSER ============================
    elif args.command == "cnv":
        # CNV required keys
        cnv_required_keys = [
            "output_folder",
            "run_name",
            "ref_fasta",
            "ref_dict",
            "interval_list",
            "common_sites",
            "pon",
            "blacklist_intervals",
            "tumor_samples",
            "normal_samples",
        ]

        # Load config if provided
        config = {}
        if args.config:
            with open(args.config) as f:
                config = json.load(f)

        # Overwrite defaults with config values only
        cnv_config.update({k: v for k, v in config.items() if v is not None})

        # Then overwrite with command line args
        for key, value in vars(args).items():
            if value is not None and key != "command":
                cnv_config[key] = value

        # Print the configuration dictionary
        _dict_print(cnv_config, command=args.command)

        # Check for required keys
        not_found_keys = [key for key in cnv_required_keys if cnv_config[key] is None]
        if not_found_keys:
            _print_not_found_keys(not_found_keys)
        else:
            somatic_CNV(cnv_config)  # accepts dictionary as config

    elif args.command == "get-config":
        if not args.configs:
            entry_dir = Path(__file__).parent.parent
            rprint("[bold green]Available configurations:[/bold green]")
            for file in (entry_dir / "configs").glob("*.json"):
                rprint(f"[grey85]{file.stem}[/grey85]")
        else:
            for config_name in args.configs:
                bring_config(config_name)

    else:
        print(parser.format_help())


if __name__ == "__main__":
    main()
