import requests


def _get_gene_from_alias(gene_symbol: str):
    url = f"https://rest.genenames.org/search/{gene_symbol}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        current_name = response.json().get("response", {}).get("docs", [])[0].get("symbol")
    else:
        current_name = None

    return current_name


def _get_gene_aliases(gene_symbol: str):
    url = f"https://rest.genenames.org/fetch/symbol/{gene_symbol}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        if docs:
            return docs[0].get("alias_symbol", []) + docs[0].get("prev_symbol", [])
    return []


def aliaser(gene_symbol: str) -> list[str]:
    """Get the gene aliases list."""
    aliases = _get_gene_aliases(gene_symbol=gene_symbol)

    if aliases == []:
        # if it is an empty, try to get current name
        current_name = _get_gene_from_alias(gene_symbol=gene_symbol)
        if current_name is not None:  # if the symbol is an alias
            aliases = _get_gene_aliases(gene_symbol=current_name)
            aliases.append(current_name)
        # else:
        # no need for else as it is already an empty list
    else:
        aliases.append(gene_symbol)

    return aliases
