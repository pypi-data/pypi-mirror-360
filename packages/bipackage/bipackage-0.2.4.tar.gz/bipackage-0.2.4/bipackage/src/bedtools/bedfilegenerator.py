import argparse
import logging
import os
import subprocess

import pandas as pd

from bipackage.constants import PARSED_GTF_PATH_GRCh38, WHOLE_GENE_LOCS_PATH_GRCh38
from bipackage.util.utilities import timer


class BedFileGenerator:
    def __init__(
        self,
        parsed_gtf_path,
        whole_gene_locs_path,
        gene_list,
        bed_file_name,
        output_folder,
        whole_gene_list=None,
        cds=True,
    ):
        self.parsed_gtf_path = parsed_gtf_path
        self.whole_gene_locs_path = whole_gene_locs_path
        self.gene_list = gene_list
        self.cds = cds
        self.output_folder = output_folder
        self.bed_file_name = bed_file_name
        self.whole_gene_list = whole_gene_list
        self.bed_file_path = None

    def bed_creator(self):
        logging.info(f"Creating bed file: {self.bed_file_name}")

        gtf = pd.read_csv(self.parsed_gtf_path, sep="\t", low_memory=False)

        gtf_all_feats = gtf[
            [
                "seqname",
                "feature",
                "start",
                "end",
                "gene_name",
                "gene_id",
                "tag",
                "exon_number",
            ]
        ]

        if self.cds:
            gtf_feature = gtf_all_feats[gtf_all_feats["feature"] == "CDS"]
        else:
            gtf_feature = gtf_all_feats[gtf_all_feats["feature"] == "exon"]

        missing_genes = set(self.gene_list) - set(gtf_feature["gene_name"])

        if missing_genes:
            raise ValueError(f"The following gene names are not in the 'gene_name' column: {', '.join(missing_genes)}")

        genes = gtf_feature[gtf_feature["gene_name"].isin(self.gene_list)]

        canonicals = genes[genes["tag"].str.contains("MANE_Select|Ensembl_canonical", na=False)]

        canonicals["seqname"] = "chr" + canonicals["seqname"].astype(str)

        canonicals["seqname"] = canonicals["seqname"].str.strip()

        canonicals["gene_exon"] = canonicals["gene_name"] + "|" + canonicals["exon_number"].astype(str)

        canonicals_filtered = canonicals[["seqname", "start", "end", "gene_exon"]]

        if self.whole_gene_list:
            wglocs = pd.read_csv(self.whole_gene_locs_path, sep="\t", low_memory=False, header=None)
            wglocs.columns = ["seqname", "start", "end", "gene_exon"]
            wgenes = wglocs[wglocs["gene_exon"].isin(self.whole_gene_list)]
            whole_gene_count = wgenes["gene_exon"].nunique()

            missing_whole_genes = set(self.whole_gene_list) - set(wgenes["gene_exon"])

            if missing_whole_genes:
                raise ValueError(
                    f"The following whole gene names are not in the 'gene_name' column: {', '.join(missing_whole_genes)}"
                )

            final_bed = pd.concat([canonicals_filtered, wgenes], ignore_index=True)

        else:
            final_bed = canonicals_filtered
            whole_gene_count = 0

        self.bed_file_path = os.path.join(self.output_folder, f"{self.bed_file_name}.bed")

        final_bed.to_csv(self.bed_file_path, sep="\t", header=False, index=False)

        unique_gene_count = canonicals["gene_name"].nunique()

        logging.info(
            f"Created bed file: {self.bed_file_name} with {unique_gene_count} genes and with {whole_gene_count} whole genes"
        )

    def sort_bed(self):
        sorted_bed_file_path = os.path.join(self.output_folder, f"sorted_{self.bed_file_name}.bed")
        command = f"bedtools sort -i {self.bed_file_path} > {sorted_bed_file_path}"

        try:
            subprocess.run(command, shell=True, check=True)
            logging.info(f"Successfully sorted the BED file. Output saved to {sorted_bed_file_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"An error occurred while sorting the BED file: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")


@timer
def bedfilegenerator(
    *,
    gene_list: str | list[str],
    bed_file_name: str,
    output_folder: str,
    whole_gene_list: str | list[str] | None,
    ref_folder: str | None = None,
    parsed_gtf_path: str | None = None,
    whole_gene_locs_path: str | None = None,
    cds: bool = False,
):
    """
    The main command for the CLI entry point. Generate and sort BED files from a parsed GTF file.

    Parameters
    ----------
    gene_list: str | list[str]
        List of gene names to include.
    bed_file_name: str
        Name of the output BED file.
    output_folder: str
        Folder to save the output BED file.
    whole_gene_list: str | list[str]
        List of whole gene names to include.
    ref_folder : str | None
        Path to the folder for reference files. e.g "fasta" or "gtf".
        Will be concatenated with the default paths.
    parsed_gtf_path : str
        Path to Parsed GTF file. e.g "Homo_sapiens.GRCh38.112.parsed.gtf"
    whole_gene_locs_path : str
        Path to whole gene locs file. e.g "Homo_sapiens.GRCh38.112.gtf.gene_names.sorted.cleaned.bed"
    cds: bool = False,
        If True, use CDS features; otherwise use exon features.
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    if ref_folder is not None:
        if parsed_gtf_path is None:
            parsed_gtf_path = os.path.join(ref_folder, PARSED_GTF_PATH_GRCh38)
        if whole_gene_locs_path in None:
            whole_gene_locs_path = os.path.join(ref_folder, WHOLE_GENE_LOCS_PATH_GRCh38)

    # guard clauses
    if isinstance(gene_list, str):
        gene_list = list[str]
    if isinstance(whole_gene_list, str):
        whole_gene_list = list[whole_gene_list]

    # create the instance
    bed_generator = BedFileGenerator(
        parsed_gtf_path=parsed_gtf_path,
        whole_gene_locs_path=whole_gene_locs_path,
        gene_list=gene_list,
        bed_file_name=bed_file_name,
        output_folder=output_folder,
        whole_gene_list=whole_gene_list,
        cds=cds,
    )
    # perform the operations
    bed_generator.bed_creator()
    bed_generator.sort_bed()

    return


if __name__ == "__main__":
    pass
