import argparse
import importlib.metadata

import argcomplete
from rich_argparse import RichHelpFormatter

from bipackage.autocomplete import _tab_autocomplete
from bipackage.constants import PARSED_GTF_PATH_GRCh38, WHOLE_GENE_LOCS_PATH_GRCh38
from bipackage.src import (
    bam_counts,
    bedfilegenerator,
    check_gzip_validity,
    check_reconnect,
    compile_bam_stats,
    downsample,
    fastq_read_counter,
    fastqvalidate,
    is_mounted,
    md5sumchecker,
    merge_it,
    mount_server,
    nipt_bcl2fastq,
    panelgenequery,
    remove_undetermined_fastq,
    undetermined_demultiplexer,
)
from bipackage.util._colors import blue, bold

_tab_autocomplete()

RichHelpFormatter.styles["argparse.args"] = "bold dark_cyan"
RichHelpFormatter.styles["argparse.groups"] = "bold dark_orange"
RichHelpFormatter.styles["argparse.help"] = "bold grey82"
RichHelpFormatter.styles["argparse.metavar"] = "grey35"
RichHelpFormatter.styles["argparse.syntax"] = "bold bold"
RichHelpFormatter.styles["argparse.text"] = "bold default"
RichHelpFormatter.styles["argparse.prog"] = "bold grey50"
RichHelpFormatter.styles["argparse.default"] = "italic"


def main():
    parser = argparse.ArgumentParser(description="BIpackage CLI", formatter_class=RichHelpFormatter)
    # --version
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=bold(f"BIpackage {blue(importlib.metadata.version('bipackage'))}"),
        help="Show version",
    )

    # init subparsers
    subparsers = parser.add_subparsers(dest="command")

    # ======================================== BAMTOOLS ========================================

    # ---------------------------------------- bam_counts ----------------------------------------
    bam_counts_subparser = subparsers.add_parser(
        "bam_counts", help="Get counts from BAM file.", formatter_class=RichHelpFormatter
    )
    bam_counts_subparser.add_argument("--dir", "-d", required=True, help="Input directory.")
    bam_counts_subparser.add_argument("--exome-bait", "-e", required=True, help="Exome bait.")
    bam_counts_subparser.add_argument("--num-threads", "-n", type=int, default=40, help="Number of threads to use.")

    # ------------------------------------- compile_bam_stats -------------------------------------
    compile_bam_stats_subparser = subparsers.add_parser(
        "compile_bam_stats", aliases=["cbs"], help="Complies BAM stats to CSV.", formatter_class=RichHelpFormatter
    )
    compile_bam_stats_subparser.add_argument("--dir", "-d", required=True, help="Root directory for the operations.")
    compile_bam_stats_subparser.add_argument("--output-csv", "-o", required=True, help="Output csv file.")

    # ======================================== BEDTOOLS ========================================

    # ------------------------------------- bedfilegenerator -------------------------------------
    bedfilegenerator_subparser = subparsers.add_parser(
        "bedfilegenerator",
        aliases=["bfg"],
        help="Generate and sort BED files from a parsed GTF file.",
        formatter_class=RichHelpFormatter,
    )
    bedfilegenerator_subparser.add_argument(
        "--gene-list", "-g", nargs="+", required=True, help="Gene names to include."
    )
    bedfilegenerator_subparser.add_argument("--bed-file-name", "-b", required=True, help="Name of the output BED file.")
    bedfilegenerator_subparser.add_argument(
        "--output-folder", "-o", required=True, help="Folder to save the output BED file."
    )
    bedfilegenerator_subparser.add_argument(
        "--whole-gene-list", "-w", nargs="+", required=True, help="Whole gene names to include."
    )
    bedfilegenerator_subparser.add_argument(
        "--parsed-gtf-path", "-p", default=PARSED_GTF_PATH_GRCh38, help="Path to Parsed GTF file."
    )
    bedfilegenerator_subparser.add_argument(
        "--whole-gene-locs-path", "-wglp", default=WHOLE_GENE_LOCS_PATH_GRCh38, help="Path to whole gene locs file."
    )
    bedfilegenerator_subparser.add_argument(
        "--cds", "-c", action="store_true", help="If used, use CDS features; otherwise use exon features."
    )
    bedfilegenerator_subparser.add_argument("--ref-folder", "-rf", help="Path to the folder for reference files.")

    panelgenequery_subparser = subparsers.add_parser(
        "panelgenequery",
        aliases=["pgq"],
        help="Using an intersected bedfile, produces a file with gene presence information.",
        formatter_class=RichHelpFormatter,
    )
    panelgenequery_subparser.add_argument("--bedfile", "-b", required=True, help="Path to the intersected bedfile.")
    panelgenequery_subparser.add_argument("--genes-list-file", "-g", required=True, help="Path to the gene list file.")
    panelgenequery_subparser.add_argument(
        "--gene-column-index",
        "-i",
        type=int,
        default=-1,
        help="Index of the column in the bedfile that contains the genes.",
    )
    # ======================================== FASTQTOOLS ========================================

    # ------------------------------------- downsample -------------------------------------
    downsample_subparser = subparsers.add_parser(
        "downsample",
        help="Pipeline to map, deduplicate, and downsample sequencing reads.",
        formatter_class=RichHelpFormatter,
    )
    downsample_subparser.add_argument("--sample_id", "-s", required=True, help="Sample ID.")
    downsample_subparser.add_argument("--r1", "-r1", required=True, help="Path to R1 fastq file.")
    downsample_subparser.add_argument("--r2", "-r2", required=True, help="Path to R2 fastq file.")
    downsample_subparser.add_argument("--out-path", "-o", required=True, help="Output path for the results.")
    downsample_subparser.add_argument("--reference", "-r", required=True, help="Path to the reference genome.")
    downsample_subparser.add_argument("--threads", "-t", type=int, default=40, help="Number of threads to use.")
    downsample_subparser.add_argument("--remove-all-dups", "-ra", action="store_true", help="Remove all duplicates")
    downsample_subparser.add_argument(
        "--remove_seq_dups", "-rs", action="store_true", help="Remove sequencing duplicates"
    )
    downsample_subparser.add_argument("--use-gatk-md", "-ug", action="store_true", help="Use GATK MarkDuplicatesSpark")
    downsample_subparser.add_argument("--strategy", "-st", default="HighAccuracy", help="Downsampling strategy")
    downsample_subparser.add_argument(
        "--keep", "-k", type=float, default=0.5, help="How much read to keep? Give a ratio"
    )

    # ------------------------------------ fastq_read_counter ------------------------------------
    fastq_read_counter_subparser = subparsers.add_parser(
        "fastq_read_counter", aliases=["frc"], help="Count reads from FASTQ file.", formatter_class=RichHelpFormatter
    )
    fastq_read_counter_subparser.add_argument("--directory", "-d", required=True, help="Path to directory.")
    fastq_read_counter_subparser.add_argument("--output_path", "-o", required=True, help="Path to save csv file.")

    # ------------------------------------- fastqvalidate -------------------------------------
    fastqvalidate_subparser = subparsers.add_parser(
        "fastqvalidate",
        aliases=["fqv"],
        help="Validate fastq files in a given directory using`fastQValidator`.",
        formatter_class=RichHelpFormatter,
    )
    fastqvalidate_subparser.add_argument(
        "--dir",
        "-d",
        required=True,
        help="Directory to perform the validation of fasq files.",
    )

    # ------------------------------------- merge_it -------------------------------------
    merge_it_subparser = subparsers.add_parser(
        "merge_it", aliases=["mff"], help="Merge FASTQ files.", formatter_class=RichHelpFormatter
    )
    merge_it_subparser.add_argument("--folder-paths", "-f", nargs="+", required=True, help="List of paths to folders.")
    merge_it_subparser.add_argument("--sample-names", "-s", nargs="+", required=True, help="List of name of the files.")
    merge_it_subparser.add_argument("--output-path", "-o", required=True, help="Path to the output directory.")

    # -------------------------------- undetermined_demultiplexer --------------------------------
    undetermined_demultiplexer_subparser = subparsers.add_parser(
        "undetermined_demultiplexer",
        aliases=["ud"],
        help="Filter undetermined FASTQ files for multiple samples using index information.",
        formatter_class=RichHelpFormatter,
    )
    undetermined_demultiplexer_subparser.add_argument(
        "--sample_sheet", "-s", required=True, help="Path to the sample sheet CSV file."
    )
    undetermined_demultiplexer_subparser.add_argument(
        "--input_r1", "-r1", required=True, help="Path to the undetermined R1 FASTQ.gz file."
    )
    undetermined_demultiplexer_subparser.add_argument(
        "--input_r2", "-r2", required=True, help="Path to the undetermined R2 FASTQ.gz file."
    )
    undetermined_demultiplexer_subparser.add_argument(
        "--output_dir", "-o", required=True, help="Directory to store the filtered FASTQ files."
    )
    undetermined_demultiplexer_subparser.add_argument(
        "--json_output", "-j", required=True, help="Path to output JSON file for sample target indices."
    )
    undetermined_demultiplexer_subparser.add_argument(
        "--threads", "-t", type=int, default=4, help="Number of threads to use (default: 4)."
    )

    # ----------------------------------------- remove_undetermined_fastq -------------------------
    remove_undetermined_fastq_subparser = subparsers.add_parser(
        "remove_undetermined_fastq",
        aliases=["ruf"],
        help="Remove undetermined FASTQ files (recursively) from a directory.",
        formatter_class=RichHelpFormatter,
    )
    remove_undetermined_fastq_subparser.add_argument(
        "--folder_path", "-f", required=True, help="Path to the folder containing FASTQ files."
    )
    remove_undetermined_fastq_subparser.add_argument(
        "--substring",
        "-s",
        default="Undetermined",
        help="Substring to search for in filenames (default: 'Undetermined').",
    )
    remove_undetermined_fastq_subparser.add_argument(
        "--non-recursive",
        "-nr",
        action="store_false",
        help="If set, search for undetermined FASTQ files non-recursively.",
    )

    # ======================================== ITTOOLS ========================================

    # ------------------------------------- ismount -------------------------------------
    # subcommand 1
    ismounted_subparser = subparsers.add_parser(
        "is_mounted", help="Check if a given path is a mounted server.", formatter_class=RichHelpFormatter
    )
    ismounted_subparser.add_argument("--path", "-p", required=True, help="Path to check.")
    # subcommand 2
    mount_server_subparser = subparsers.add_parser(
        "mount_server", help="Mount a server.", formatter_class=RichHelpFormatter
    )
    mount_server_subparser.add_argument("--username", "-u", required=True, help="Username.")
    mount_server_subparser.add_argument("--server_address", "-s", required=True, help="Server address.")
    mount_server_subparser.add_argument("--mount-folder", "-m", required=True, help="Mount folder.")
    mount_server_subparser.add_argument("--password", "-p", required=True, help="Password.")
    mount_server_subparser.add_argument("--version", "-v", default=None, help="Version.")
    # subcommand 3
    check_reconnect_subparser = subparsers.add_parser(
        "check_reconnect", help="Check reconnects.", formatter_class=RichHelpFormatter
    )
    # check_reconnect_subparser.add_argument("--base-mnt", "-b", required=True, help="Base mount.")
    check_reconnect_subparser.add_argument("--config-file", "-c", required=True, help="Config file.")

    # ------------------------------------- md5sumchecker -------------------------------------
    md5sumchecker_subparser = subparsers.add_parser(
        "md5sumchecker", aliases=["md5sc"], help="Check md5sum of a file.", formatter_class=RichHelpFormatter
    )
    md5sumchecker_subparser.add_argument("--directory", "-d", required=True, help="Input directory path.")
    md5sumchecker_subparser.add_argument("--extension", "-e", required=True, help="File extension to search for.")
    md5sumchecker_subparser.add_argument(
        "--num_processes", "-n", type=int, default=2, help="Number of processes to use (default: 2)"
    )

    # -------------------------------- truncatedfchecker_single --------------------------------
    check_gzip_validity_subparser = subparsers.add_parser(
        "check_gzip_validity",
        aliases=["cgv"],
        help="Check a compressed file validity.",
        formatter_class=RichHelpFormatter,
    )
    check_gzip_validity_subparser.add_argument("file_path", help="Path to the compressed file.")

    # ======================================== NIPTTOOLS ========================================
    nipt_bcl2fastq_subparser = subparsers.add_parser(
        "nipt_bcl2fastq",
        aliases=["nb2f"],
        help="Run bcl2fastq conversion for multiple BCL folders.",
        formatter_class=RichHelpFormatter,
    )
    nipt_bcl2fastq_subparser.add_argument("--folders", "-f", nargs="+", required=True, help="NIPT folders.")
    nipt_bcl2fastq_subparser.add_argument("--part", "-p", required=True, type=int, help="NIPT Part number.")
    nipt_bcl2fastq_subparser.add_argument(
        "--names", "-n", nargs="+", required=True, help="Fastq sample names - For example 24B3043312."
    )
    nipt_bcl2fastq_subparser.add_argument(
        "--output-folder", "-o", required=True, help="Path to the output Fastq folder."
    )
    nipt_bcl2fastq_subparser.add_argument("--num-readers", "-r", type=int, default=10, help="Number of readers.")
    nipt_bcl2fastq_subparser.add_argument("--num-writers", "-w", type=int, default=10, help="Number of writers.")
    nipt_bcl2fastq_subparser.add_argument("--num-processors", "-np", type=int, default=40, help="Number of processors.")
    nipt_bcl2fastq_subparser.add_argument("--compression-level", "-cl", type=int, default=8, help="Compression level.")

    nipt_bcl2fastq_subparser.add_argument("--bcl-path", "-b", required=True, help="Path to the BCL folder.")
    nipt_bcl2fastq_subparser.add_argument("--source-path", "-s", required=True, help="Path to the source folder.")

    # PARSE ALL ARGS ------------------------------
    argcomplete.autocomplete(parser, always_complete_options=True)
    args = parser.parse_args()

    # EVALUATE ARGS ------------------------------
    # Subcommand: list
    if args.command is None:
        print(bold(f"BIpackage {blue(importlib.metadata.version('bipackage'))}"))
        parser.print_help()  # Show help if no command is provided
        return

    # Subcommand: bam_counts
    elif args.command == "bam_counts":
        bam_counts(input_dir=args.dir, exome_bait=args.exome_bait, num_threads=args.num_threads)

    # Subcommand: compile_bam_stats
    elif args.command == "compile_bam_stats":
        compile_bam_stats(root_directory=args.dir, output_csv=args.output_csv)

    # Subcommand: bedfilegenerator
    elif args.command == "bedfilegenerator":
        bedfilegenerator(
            gene_list=args.gene_list,
            bed_file_name=args.bed_file_name,
            output_folder=args.output_folder,
            whole_gene_list=args.whole_gene_list,
            parsed_gtf_path=args.parsed_gtf_path,
            whole_gene_locs_path=args.whole_gene_locs_path,
            cds=args.cds,
            ref_folder=args.ref_folder,
        )

    elif args.command == "panelgenequery":
        panelgenequery(
            bedfile=args.bedfile,
            genes_list_file=args.genes_list_file,
            gene_column_index=args.gene_column_index,
        )

    # Subcommand: downsample
    elif args.command == "downsample":
        downsample(
            sample_id=args.sample_id,
            r1=args.r1,
            r2=args.r2,
            out_path=args.out_path,
            reference=args.reference,
            threads=args.threads,
            remove_all_dups=args.remove_all_dups,
            remove_seq_dups=args.remove_seq_dups,
            use_gatk_md=args.use_gatk_md,
            strategy=args.strategy,
            keep=args.keep,
        )

    # Subcommand: fastq_read_counter
    elif args.command == "fastq_read_counter":
        fastq_read_counter(directory=args.directory, output_path=args.output_path)

    # Subcommand: fastqvalidate
    elif args.command == "fastqvalidate":
        fastqvalidate(directory=args.dir)

    # Subcommand: merge_it
    elif args.command == "merge_it":
        merge_it(folder_paths=args.folder_paths, sample_names=args.sample_names, output_path=args.output_path)

    # Subcommand: undetermined_demultiplexer
    elif args.command == "undetermined_demultiplexer":
        undetermined_demultiplexer(
            sample_sheet=args.sample_sheet,
            input_r1=args.input_r1,
            input_r2=args.input_r2,
            output_dir=args.output_dir,
            json_output=args.json_output,
            threads=args.threads,
        )

    # Subcommand: remove_undetermined_fastq
    elif args.command == "remove_undetermined_fastq":
        remove_undetermined_fastq(
            folder_path=args.folder_path,
            substring=args.substring,
            recursive=args.non_recursive,
        )

    # Subcommand: ismounted
    elif args.command == "is_mounted":
        is_mounted(folder_path=args.path)

    # Subcommand: mount_server
    elif args.command == "mount_server":
        mount_server(
            username=args.username,
            server_address=args.server_address,
            mount_folder=args.mount_folder,
            password=args.password,
            version=args.version,
        )

    # Subcommand: check_reconnect
    elif args.command == "check_reconnect":
        check_reconnect(config_file=args.config_file)

    # Subcommand: md5sumchecker
    elif args.command == "md5sumchecker":
        md5sumchecker(input_directory=args.directory, file_extension=args.extension, num_processes=args.num_processes)

    # Subcommand: check_gzip_validity
    elif args.command == "check_gzip_validity":
        check_gzip_validity(file_path=args.file_path)

    # Subcommand: nipt_bcl2fastq
    elif args.command == "nipt_bcl2fastq":
        nipt_bcl2fastq(
            nipt_folders=args.folders,
            nipt_part=args.part,
            fastq_names=args.names,
            output_folder=args.output_folder,
            num_readers=args.num_readers,
            num_writers=args.num_writers,
            num_processors=args.num_processors,
            compression_level=args.compression_level,
            source_path=args.source_path,
            bcl_path=args.bcl_path,
        )

