from pathlib import Path


def _find_undetermined_fastq(folder_path: str, *, substring: str = "Undetermined", recursive=True) -> list[Path]:
    """
    Find all FASTQ files in the specified folder that contain the substring in their filename.

    Parameters
    ----------
    folder_path:
        Path to the folder containing FASTQ files.
    substring:
        Substring to search for in filenames (default is "Undetermined").
    Return
    ------
        List of Path objects for matching FASTQ files.
    """
    folder = Path(folder_path)

    if recursive:
        return list(folder.rglob(f"*{substring}*.fastq.*"))
    else:
        return list(folder.glob(f"*{substring}*.fastq.*"))


def remove_undetermined_fastq(
    folder_path: str,
    *,
    substring: str = "Undetermined",
    recursive: bool = True
) -> None:
    """
    Remove all FASTQ files recursively in the specified folder that contain the substring in their filename.

    Parameters
    ----------
    folder_path:
        Path to the folder containing FASTQ files.
    substring:
        Substring to search for in filenames (default is "Undetermined").
    """
    undetermined_files = _find_undetermined_fastq(folder_path, substring=substring, recursive=recursive)

    total_file_size = sum(file.stat().st_size for file in undetermined_files)
    print(f"Total size of undetermined FASTQ files: {total_file_size / (1024 * 1024 * 1024):.2f} GB")
    print(f"Found {len(undetermined_files)} undetermined FASTQ files.")
    for file in undetermined_files:
        print(f"Removing: {file}")
        try:
            file.unlink()
            print(f"Removed: {file}")
        except Exception as e:
            print(f"Error removing {file}: {e}")

    return

def main():
    folder_path = "/mnt/ananas/01.FastQ_files/01.RE-BCL2fastq/204.TWIST-ExoV2-DNAPrepWithExomePlus-NovaSeq-RUN194_fastq_files"
    remove_undetermined_fastq(folder_path=folder_path)
    return

if __name__ == "__main__":
    main()