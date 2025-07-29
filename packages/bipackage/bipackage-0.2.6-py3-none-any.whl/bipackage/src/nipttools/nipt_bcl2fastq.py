import argparse
import ftplib
import os
import subprocess

from bipackage.util.utilities import timer


'''Gets a bcl file, demultiplex it and send relevant fastqs to a remote server'''

class NIPTBcl2Fastq:
    def __init__(
        self,
        output_folder,
        num_readers,
        num_writers,
        num_processors,
        compression_level,
        fastq_file_names,
        nipt_part,
        nipt_folders,
        source_path,
        bcl_path,
    ):
        self.output_folder = output_folder
        self.num_readers = num_readers
        self.num_writers = num_writers
        self.num_processors = num_processors
        self.compression_level = compression_level
        self.nipt_part = nipt_part
        self.fastq_file_names = fastq_file_names
        self.bclfolders = nipt_folders
        self.source_path = source_path
        self.bcl_path = bcl_path
        self.fastq_folder_paths = []
        self.fastq_file_paths = []
        self.copybclfromnas()
        self.create_folders()
        self.bcl_to_fastq()
        self.take_sample_paths()
        # self.upload_file_secure()

    def copybclfromnas(self):
        print("Copying bcl files to server")

        if self.bclfolders:
            source_paths = " ".join([f"{self.source_path}/{folder}" for folder in self.bclfolders])
            command = f"cp -r {source_paths} {self.bcl_path}"

            subprocess.run(command, shell=True)
        else:
            print("No BCL folders found to copy.")

    def create_folders(self):
        print("Creating fastq folders")
        for folder in self.bclfolders:
            fastq_folder = os.path.join(self.output_folder, folder)
            os.makedirs(fastq_folder, exist_ok=True)
            self.fastq_folder_paths.append(fastq_folder)
        print("Fastq folders created")

    def bcl_to_fastq(self):
        print("Starting bcl2fastq")

        self.fastq_folder_paths = []

        for bcl_folder in self.bclfolders:
            bcl_abs_path = os.path.join(self.bcl_path, bcl_folder)
            fastq_abs_path = os.path.join(self.output_folder, bcl_folder)
            samplesheet_path = os.path.join(bcl_abs_path, "SampleSheet.csv")

            self.fastq_folder_paths.append(fastq_abs_path)

            run_command = (
                f"bcl2fastq -R {bcl_abs_path} -o {fastq_abs_path} "
                f"--sample-sheet {samplesheet_path} -r {self.num_readers} "
                f"-w {self.num_writers} -p {self.num_processors} "
                f"--fastq-compression-level {self.compression_level} "
                "--no-lane-splitting"
            )

            subprocess.run(run_command, shell=True)

    def take_sample_paths(self):
        print("Taking sample paths")

        all_folder_paths = [os.path.join(self.output_folder, folder) for folder in self.bclfolders]
        print(all_folder_paths)
        self.fastq_file_paths = []

        for folder_path in all_folder_paths:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    for file_name in self.fastq_file_names:
                        if file.startswith(file_name):
                            self.fastq_file_paths.append(os.path.join(root, file))

        print("Took sample paths")

    def upload_file_secure(self, ftp_server, ftp_user, ftp_password):
        print("Started uploading the files")
        try:
            ftps = ftplib.FTP_TLS()
            ftps.connect(ftp_server, 21)
            ftps.login(user=ftp_user, passwd=ftp_password)
            ftps.prot_p()
            ftps.set_pasv(True)
            counter = 0
            for file_path in self.fastq_file_paths:
                folder_path = file_path.split("/")[-2]
                fastq_name = os.path.basename(file_path)
                remote_path = os.path.join(f"NIPT-Part{str(self.nipt_part)}", folder_path, fastq_name)
                with open(file_path, "rb") as file:
                    ftps.storbinary(f"STOR {remote_path}", file)
                    print(f"File uploaded successfully: {remote_path}")
                    counter += 1
            print(f"In total {counter} Fastq files uploaded to the server")
            ftps.quit()
        except ftplib.all_errors as e:
            print(f"FTP error: {e}")

        return


@timer
def nipt_bcl2fastq(
    *,
    nipt_folders: str | list[str],
    nipt_part: str,
    fastq_names: str | list[str],
    output_folder: str,
    source_path: str,
    bcl_path: str,
    num_readers: int = 10,
    num_writers: int = 10,
    num_processors: int = 40,
    compression_level: int = 8,
) -> None:
    """
    Run bcl2fastq conversion for multiple BCL folders, upload resulting fastqs to the server.

    Parameters
    ----------
    nipt_folders : str | list[str]
        Nipt folders.
    nipt_part: str
        Part number.
    fastq_names: str | list[str]
        Fastq sample names - For example 24B3043312
    output_folder: str
        Path to the output Fastq folder.
    num_readers: int = 10
        Number of readers.
    num_writers: int = 10
        Number of writers.
    num_processors: int = 40
        Number of processors.
    compression_level: int = 8
        Compression level.
    source_path: str = source_path
        Path to the source folder.
    bcl_path: str = bcl_path
        Path to the bcl folder.

    """
    nipt = NIPTBcl2Fastq(
        output_folder,
        num_readers,
        num_writers,
        num_processors,
        compression_level,
        fastq_names,
        nipt_part,
        nipt_folders,
        source_path=source_path,
        bcl_path=bcl_path,
    )
    return nipt


if __name__ == "__main__":
    pass
