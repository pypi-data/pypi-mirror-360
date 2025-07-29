from bipackage.util.aliaser import aliaser


def _read_genes(filename: str = "genes.tsv"):
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


def _match_genes(
    filename: str,
    genes: list[str],
    *,
    gene_column_index: int = -1,
) -> list[str]:
    """Matches genes list with genes within bedfile."""
    genes_exist = []
    with open(filename) as file:
        for line in file:
            gene_name = line.split("\t")[gene_column_index].rstrip("\n")
            if gene_name in genes:
                if gene_name not in genes_exist:
                    genes_exist.append(gene_name)

    return genes_exist


def panelgenequery(
    bedfile: str,
    genes_list_file: str,
    *,
    gene_column_index: int = -1,
) -> None:
    """
    Creates a modified version of gene_list_file the second column confirms the presence of a gene.

    bedfile: str
        Path to the intersected bedfile where the last column should be the gene name.
        If the gene name column is different, use the `gene_column_index` argument.
    genes_list_file: str
        Path to the gene list file. Each gene name must be seperated by a new line.
    gene_column_index: int
        Index of the column in the bedfile that contains the genes.
        Defaults is -1 (the last column).

    Returns
    -------
    None
    """
    genes = _read_genes(genes_list_file)
    genes_exist = _match_genes(bedfile, genes=genes, gene_column_index=gene_column_index)
    genes_exist = sorted(genes_exist)
    genes_not_exist = [gene for gene in genes if gene not in genes_exist]

    try:
        alias_present = {}
        for gene in genes_not_exist[:]:
            print(f"{gene} could not be found, checking aliases.")
            aliases = aliaser(gene_symbol=gene)
            if aliases != []:
                print(f"aliases for {gene} : {aliases} ")
                matched_aliases = _match_genes(bedfile, genes=aliases, gene_column_index=gene_column_index)
                if matched_aliases != []:
                    print(f"matched aliases : {matched_aliases}")
                    genes_not_exist.remove(gene)
                    genes_exist.append(gene)
                    alias_present[gene] = matched_aliases[0]
    except Exception as e:
        print("Error occurred while checking aliases. Skipping aliases...")
        print(f"Exception: {e}")


    genes_exist = sorted(genes_exist)


    extension = genes_list_file.split(".")[-1]
    exists_path = genes_list_file.replace(extension, f"exist.{extension}")
    with open(exists_path, "w+") as ep:
        for gene in genes_not_exist:
            ep.write(f"{gene}\tNO\n")
        for gene in genes_exist:
            if gene in alias_present:
                ep.write(f"{gene}[{alias_present.get(gene)}]\tYES\n")
            else:
                ep.write(f"{gene}\tYES\n")
    return


