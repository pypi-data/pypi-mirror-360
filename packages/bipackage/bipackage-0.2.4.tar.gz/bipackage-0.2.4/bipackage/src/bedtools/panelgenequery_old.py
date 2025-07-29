def read_genes(filename: str = "genes.tsv"):
    """
    Reads a gene list file, where each gene name seperated by a new line and return the gene list.

    Example gene list file (genes.tsv):
    --------
    BRWD3
    POU3F4
    CHM
    GLA
    PLP1
    PRPS1
    ...
    """
    with open(filename) as f:
        content = f.read().rstrip("\n")

    genes = content.split("\n")
    return genes


def modify_bed(filename: str, genes: list[str]):
    """
    Modifies an intersected bedfile to include gene inclusion information.
    """
    genes_exist = []
    modified_bed = filename.replace(".bed", ".modified.bed")
    with open(modified_bed, "w+") as modified, open(filename) as file:
        for line in file:
            gene_name = line.split("\t")[-1].rstrip("\n")
            # cases
            if gene_name in genes:
                new_line = line.replace("\n", "\t+++\n")
                if gene_name not in genes_exist:
                    genes_exist.append(gene_name)
            else:
                new_line = line.replace("\n", "\t---\n")

            modified.write(new_line)

    not_exist = [gene for gene in genes if gene not in genes_exist]

    with (
        open("genes.present.tsv", "w+") as exist,
        open("genes.notpresent.tsv", "w+") as no_exist,
    ):
        for g in genes_exist:
            exist.write(f"{g}\n")
        for n in not_exist:
            no_exist.write(f"{n}\n")

    return


def panelgenequery(bedfile: str, genes_list_file: str):
    """
    Modifies an intersected bedfile to include gene inclusion information.

    Appends a column "+++" or "---" meaning the gene is present in gene list or not.
    Also creates and writes to 'genes.present.tsv' and 'genes.notpresent.tsv' files.
    """
    genes = read_genes(genes_list_file)
    modify_bed(bedfile, genes=genes)
    return
