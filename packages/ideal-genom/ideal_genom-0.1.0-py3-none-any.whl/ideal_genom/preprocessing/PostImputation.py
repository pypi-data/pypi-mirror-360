"""Module to run the post-imputation processing tasks on VCF files.

This module provides classes for running various post-imputation tasks in parallel,
including unzipping VCF files, filtering variants based on imputation quality, normalizing VCF files,
and indexing VCF files. It uses the `ThreadPoolExecutor` for parallel execution
and `tqdm` for progress tracking. The tasks are designed to handle large genomic datasets
efficiently by leveraging multi-threading.

It also includes functionality to download and use reference genomes for normalization, and convert
VCF file into a format suitable for further analysis, that is PLINK binary files.
"""
import time
import logging
import os
import threading
import zipfile
import subprocess
import psutil

from pathlib import Path
from typing import Callable, List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from typing import Optional

from ideal_genom.get_references import AssemblyReferenceFetcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ParallelTaskRunner:
    """A base class for running parallel tasks on files.
    
    This class provides the basic infrastructure for parallel processing of files
    using ThreadPoolExecutor. It handles file collection and parallel task execution
    while providing progress monitoring and logging.
    
    Attributes
    ----------
    input_path : Path 
        Directory path where input files are located.
    output_path : Path 
        Directory path where output files will be saved.
    max_workers : int 
        Maximum number of worker threads to use. Defaults to min(8, CPU count).
    files : List[Path] 
        List of files to be processed.
   
    Raises
    ------
    TypeError
        If input_path or output_path are not Path objects.
    FileNotFoundError
        If input_path or output_path don't exist.
    NotADirectoryError 
        If input_path or output_path are not directories.
    """
    
    def __init__(self, input_path: Path, output_path: Path, max_workers: Optional[int] = None) -> None:

        if not isinstance(input_path, Path):
            raise TypeError(f"input_path should be of type Path, got {type(input_path)}")
        if not isinstance(output_path, Path):
            raise TypeError(f"output_path should be of type Path, got {type(output_path)}")
        if not input_path.exists():
            raise FileNotFoundError(f"Input path {input_path} does not exist.")
        if not output_path.exists():
            raise FileNotFoundError(f"Output path {output_path} does not exist.")
        if not input_path.is_dir():
            raise NotADirectoryError(f"Output path {input_path} is not a directory.")
        if not output_path.is_dir():
            raise NotADirectoryError(f"Output path {output_path} is not a directory.")

        self.input_path = input_path
        self.output_path = output_path

        cpu_count = os.cpu_count() or 1  # Use 1 as fallback if cpu_count returns None
        self.max_workers = max_workers or min(8, cpu_count)

        self.files = []

        pass

    def execute_task(self) -> None:
        """Execute the specific post-imputation processing task.

        This abstract method should be implemented by all subclasses to perform
        their specific post-imputation processing operations. Implementations
        should handle the execution logic for the particular task the subclass
        is designed to perform.

        Returns
        -------
        None

        Raises
        ------
        NotImplementedError
            If the subclass does not implement this method.
        """

        raise NotImplementedError("Subclasses must implement this method.")

    def _file_collector(self, filename_pattern: str) -> List[Path]:
        """
        Collect files matching a given pattern from the input directory.
        This method finds all files matching the specified glob pattern within the
        input directory, sorts them, and stores the resulting list as an instance attribute.
        
        Parameters
        ----------
        filename_pattern : str
            A glob pattern string to match files (e.g., ``*.vcf.gz``).
        
        Returns
        -------
        List[Path]
            A sorted list of Path objects for the files matching the pattern.
        
        Raises
        ------
        TypeError
            If filename_pattern is not a string.
        FileNotFoundError
            If no files match the given pattern in the input directory.
        
        Notes
        -----
        The matched files are also stored in the instance attribute `files`.
        """

        if not isinstance(filename_pattern, str):
            raise TypeError(f"filename_pattern should be of type str, got {type(filename_pattern)}")

        files = list(self.input_path.glob(filename_pattern))
        files.sort()

        self.files = files
        logger.info(f"Found {len(files)} files matching pattern {filename_pattern} in {self.input_path}")
        
        if not files:
            raise FileNotFoundError(f"No files found matching pattern {filename_pattern} in {self.input_path}")

        return files
    
    def _run_task(self, task_fn: Callable, task_args: Dict[str, Any], desc: str = "Running tasks") -> None:
        """Execute a task function across all files using parallel processing with ThreadPoolExecutor.
        
        This method applies the given task function to each file in self.files concurrently,
        managing thread allocation, progress tracking, and error handling.
        
        Parameters
        ----------
        task_fn : Callable
            The function to execute for each file. First argument should accept a file,
            and it should accept ``**kwargs`` for additional arguments.
        task_args : Dict[str, Any]
            Dictionary of keyword arguments to pass to the task function.
        desc : str, optional
            Description for the progress bar and logging, by default "Running tasks".
        
        Returns
        -------
        None
        
        Notes
        -----
        - Uses ThreadPoolExecutor with max_workers defined in class initialization
        - Provides progress tracking via tqdm
        - Logs timing information and any exceptions that occur
        - Does not raise exceptions from individual tasks but logs them instead
        """
        
        start_time = time.time()

        logger.info(f"Active threads before: {threading.active_count()}")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(task_fn, file, **task_args): file for file in self.files
            }
            logger.info(f"Active threads after submission: {threading.active_count()}")

            with tqdm(total=len(futures), desc=desc) as pbar:
                for future in as_completed(futures):
                    args = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Task failed with args {args}: {e}")
                        raise
                    pbar.update(1)

        elapsed = time.time() - start_time
        logger.info(f"{desc} finished in {elapsed:.2f} seconds.")

class UnzipVCF(ParallelTaskRunner):
    """A class for unzipping VCF (Variant Call Format) files after imputation, with support for parallel processing.
    
    This class extends ParallelTaskRunner to efficiently extract VCF files from zip archives,
    including password-protected ones. It collects all zip files in the working directory
    and extracts their contents to the output directory.
    
    Attributes
    ----------
    (See `ParallelTaskRunner` for inherited attributes.)

    Notes
    -----
    - VCF files are commonly used in genomics for storing gene sequence variations
    - The class only extracts files (not directories) from the zip archives
    - All extracted files are placed directly in the output directory without preserving paths
    - This class is designed for post-imputation processing in genetic data pipelines
    """

    def __init__(self, input_path: Path, output_path: Path, max_workers: Optional[int] = None, password: Optional[str] = None) -> None:
        super().__init__(input_path, output_path, max_workers)
        self.password = password
    
    def execute_task(self) -> None:
        """
        Execute the post-imputation unzipping task on VCF files.

        This method performs the following steps:
        1. Collects all zip files in the working directory
        2. Unzips the VCF files, using the provided password if necessary

        Parameters
        ----------
        password : Optional[str]
            Password to decrypt zip files if they are password-protected.
            Default is None.

        Returns
        -------
        None
            This method doesn't return any value.
        """

        task_args ={'password': self.password}

        self._file_collector("*.zip")

        self._run_task(
            self.unzip_files,
            task_args=task_args,
            desc="Unzipping VCF files"
        )

        return
    
    def unzip_files(self, zip_path: Path, password: Optional[str] = None, output_prefix: str = 'unzipped-') -> None:
        """
        Extract files from a password-protected zip archive.
        This method extracts all non-directory files from the specified zip archive
        to the class's output_path directory. If the zip file is password-protected,
        provide the password as a parameter.
        
        Parameters
        ----------
        zip_path : Path
            Path to the zip file to be extracted
        password : Optional[str], optional
            Password for the zip file, None if the file is not password-protected. Defaults to None.
        output_prefix : str, optional
            Prefix to add to extracted filenames. Defaults to 'unzipped-'.
        
        Returns
        -------
        None
        
        Raises
        ------
        zipfile.BadZipFile
            If the zip file is corrupted or password is incorrect
        FileNotFoundError
            If the zip file does not exist
        PermissionError
            If there are insufficient permissions to read the zip file or write to output directory
        
        Notes
        -----
        Files are extracted to the output_path directory of the class instance.
        Only files (not directories) are extracted from the archive.
        File paths are not preserved - all files are placed directly in output_path.
        The output_prefix is added to the beginning of each extracted filename.
        """
        
        # Validate input file exists
        if not zip_path.exists():
            raise FileNotFoundError(f"Zip file {zip_path} does not exist")
        
        if not zip_path.is_file():
            raise ValueError(f"Path {zip_path} is not a file")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                
                if password is not None:
                    password_bytes = bytes(password, 'utf-8')
                    zf.setpassword(password_bytes)
                
                corrupted_file = zf.testzip()
                if corrupted_file is not None:
                    logger.error(f"Corrupted file in ZIP archive {zip_path}: {corrupted_file}")
                    raise zipfile.BadZipFile(f"Corrupted file in ZIP archive {zip_path}: {corrupted_file}")
                else:
                    logger.info(f"Extracting {zip_path}...")
                
                for member in zf.namelist():
                    
                    if zf.getinfo(member).is_dir():
                        continue
                    
                    # Use the output_prefix parameter
                    filename = output_prefix + os.path.basename(member)
                    target_path = os.path.join(self.output_path, filename)
                    
                    try:
                        with zf.open(member) as source, open(target_path, 'wb') as target:
                            target.write(source.read())
                    except RuntimeError as e:
                        if "password" in str(e).lower():
                            logger.error(f"Bad password for file '{member}' in archive {zip_path}")
                            raise zipfile.BadZipFile(f"Bad password for file '{member}' in archive {zip_path}") from e
                        else:
                            raise
                    except PermissionError as e:
                        logger.error(f"Permission denied when extracting '{member}' to '{target_path}': {e}")
                        raise
                    
        except zipfile.BadZipFile as e:
            logger.error(f"Invalid or corrupted zip file {zip_path}: {e}")
            raise
        except PermissionError as e:
            logger.error(f"Permission denied accessing zip file {zip_path}: {e}")
            raise
        
        logger.info(f"Successfully extracted {zip_path}")
        pass

class FilterVariants(ParallelTaskRunner):
    """
    A class for filtering genetic variants in VCF/BCF files based on imputation quality (R² statistic).
    This class extends ParallelTaskRunner to provide parallel processing capabilities for filtering
    variants across multiple VCF files. It identifies variants with imputation quality below a specified
    R² threshold and removes them from the output files.
    
    Attributes
    ----------
    r2_threshold : float
        The threshold value for the R² statistic. Variants with an R² value below this threshold 
        will be filtered out.
    output_prefix : str, optional
        The prefix to be added to output filenames. Default is 'filtered-'.
    (See `ParallelTaskRunner` for inherited attributes.)
    
    Notes
    -----
    The class searches for files matching the pattern ``*dose.vcf.gz`` in the input directory
    and processes them in parallel. The filtered output files will be saved in the output
    directory with the specified prefix added to their original filenames.

    Note
    ----
    bcftools must be installed and available in the system path
    """

    def __init__(self, input_path: Path, output_path: Path, max_workers: Optional[int] = None, r2_threshold: float = 0.3, output_prefix: str = 'filtered-') -> None:
        super().__init__(input_path, output_path, max_workers)
        self.r2_threshold = r2_threshold
        self.output_prefix = output_prefix
    
    def execute_task(self) -> None:
        """
        Execute the task of filtering variants based on an R² threshold.

        This method collects the necessary files with the pattern ``*dose.vcf.gz`` and runs 
        the filtering task with the specified parameters.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If r2_threshold is not a float or output_prefix is not a string.

        Notes
        -----
        The method uses internal methods _file_collector and _run_task to perform the filtering operation.
        """

        task_args = {'r2_threshold': self.r2_threshold, 'output_prefix': self.output_prefix}
        if not isinstance(self.r2_threshold, float):
            raise TypeError(f"r2_threshold should be of type float, got {type(self.r2_threshold)}")
        if not isinstance(self.output_prefix, str):
            raise TypeError(f"prefix should be of type str, got {type(self.output_prefix)}")

        self._file_collector('unzipped-*dose.vcf.gz')

        self._run_task(
            self.filter_variants,
            task_args=task_args,
            desc="Filter variants"
        )

        return
    
    def filter_variants(self, input_file: Path, r2_threshold: float, output_prefix: str = 'filtered-') -> None:
        """Filter variants from a VCF/BCF file based on R2 imputation quality threshold.
        
        This method takes an imputed VCF/BCF file and filters out variants with 
        imputation quality (R2) below the specified threshold. The filtered output 
        is saved as a compressed VCF.

        Parameters
        ----------
        input_file : Path 
            Path to the input VCF/BCF file to be filtered
        r2_threshold : float 
            Minimum R2 imputation quality threshold (variants with R2 <= threshold will be removed)
        output_prefix : str, optional 
            Prefix to add to the output filename. Defaults to 'filtered-'.
        
        Returns
        -------
        None 
            The method outputs a filtered VCF file but doesn't return a value.
        
        Raises
        ------
        FileExistsError 
            If the input file does not exist
        IsADirectoryError
            If the input path is a directory, not a file
        TypeError 
            If r2_threshold is not a float or output_prefix is not a string
        
        Notes
        -----
        - The output file will be saved in the instance's output_path directory with
        - the name constructed as: `output_prefix` + `input_file.name`

        Note
        ----
        This method requires bcftools to be installed and available in the system path.
        """

        if not input_file.exists():
            raise FileExistsError(f"Input file {input_file} does not exist")
        if not input_file.is_file():
            raise IsADirectoryError(f"Input file {input_file} is not a file")
        if not isinstance(r2_threshold, float):
            raise TypeError(f"r2_threshold should be of type float, got {type(r2_threshold)}")
        if not isinstance(output_prefix, str):
            raise TypeError(f"output_prefix should be of type str, got {type(output_prefix)}")
        
        base_name = input_file.name.split('-')[1]
        
        output_file = self.output_path / (output_prefix + base_name)

        logger.info(f"Filtering {input_file} with R2 > {r2_threshold}")
        logger.info(f"Output file: {output_file}")

        # bcftools command
        bcf_cmd = [
            "bcftools", "view", "-Oz", "-i", f"R2>{r2_threshold}",
            input_file, "-o", output_file
        ]
        file_name = input_file.name
        
        try:
            # execute bcftools command
            subprocess.run(bcf_cmd, check=True)
            logger.info(f"Chromosome {file_name}: Completed")
        except subprocess.CalledProcessError as e:
            logger.error(f"Chromosome {file_name}: Failed with error {e}")
        except FileNotFoundError:
            logger.error(f"Chromosome {file_name}: Input file not found")
        pass

class NormalizeVCF(ParallelTaskRunner):
    """A class for normalizing VCF files post-imputation in parallel.
    
    This class provides functionality to process VCF files by normalizing them using
    bcftools. It's specifically designed to handle post-imputation VCF files and
    split multiallelic variants into separate entries.
    The class inherits from ParallelTaskRunner to enable parallel processing of
    multiple VCF files, which improves performance for large-scale genomic datasets.
    
    Attributes
    ----------
        Inherits all attributes from ParallelTaskRunner
    output_prefix : str, optional
        Prefix to add to the output files. Defaults to 'uncompressed-'.

    Note
    ----
    bcftools must be installed and available in the system path
    """

    def __init__(self, input_path: Path, output_path: Path, max_workers: Optional[int] = None, output_prefix: str = 'uncompressed-') -> None:
        super().__init__(input_path, output_path, max_workers)
        self.output_prefix = output_prefix


    def execute_task(self) -> None:
        """
        Execute the post-imputation normalization task on VCF files.

        This method collects filtered dose VCF files matching the pattern ``filtered-*dose.vcf.gz``
        and runs the normalization process on them. The normalized files will be prefixed with 
        the provided output_prefix.

        Parameters
        ----------
        output_prefix : str (optional)
            Prefix to add to the output files. Defaults to 'uncompressed-'.

        Raises
        ------
        TypeError 
            If output_prefix is not a string.

        Returns
        -------
        None
        """

        task_args = {'output_prefix': self.output_prefix}
        if not isinstance(self.output_prefix, str):
            raise TypeError(f"prefix should be of type str, got {type(self.output_prefix)}")

        self._file_collector('filtered-*dose.vcf.gz')

        self._run_task(
            self.normalize_vcf,
            task_args=task_args,
            desc="Normalizing VCF files"
        )

        return
    
    def normalize_vcf(self, input_file: Path, output_prefix: str = 'uncompressed-') -> None:
        """Normalizes a VCF file using bcftools norm with the -m -any option.
        
        This method takes a VCF file, performs normalization using bcftools to split 
        multiallelic variants into separate entries, and outputs the normalized file 
        with the specified prefix.
        
        Parameters
        ----------
        input_file : Path 
            Path to the input VCF file to be normalized
        output_prefix : str, optional 
            Prefix for the output file name. Defaults to 'uncompressed-'
        
        Returns
        -------
        None

        Raises
        ------
        FileExistsError 
            If the input file does not exist
        IsADirectoryError 
            If the input file path points to a directory
        TypeError 
            If output_prefix is not a string
        
        Notes
        -----
        The output file will be saved in the output_path directory with the naming 
        convention: `output_prefix` + `base_name`, where base_name is derived from the input file.
        """

        if not input_file.exists():
            raise FileExistsError(f"Input file {input_file} does not exist")
        if not input_file.is_file():
            raise IsADirectoryError(f"Input file {input_file} is not a file")
        if not isinstance(output_prefix, str):
            raise TypeError(f"output_prefix should be of type str, got {type(output_prefix)}")
        
        base_name = input_file.name.split('-')[1]

        output_file = self.output_path / (output_prefix + base_name)

        # Normalize with `bcftools norm -Ou -m -any`
        bcf_cmd = [
            "bcftools", "norm", "-Ou", "-o", output_file,"-m", "-any", input_file
        ]

        chr_number = os.path.basename(input_file)
        try:
            # execute bcftools command
            subprocess.run(bcf_cmd, check=True)
            logger.info(f"Chromosome {chr_number}: Completed")
        except subprocess.CalledProcessError as e:
            logger.error(f"Chromosome {chr_number}: Failed with error {e}")
        except FileNotFoundError:
            logger.error(f"Chromosome {chr_number}: Input file not found")
        pass

class ReferenceNormalizeVCF(ParallelTaskRunner):
    """A class for normalizing VCF files using a reference genome in parallel.
    
    This class extends ParallelTaskRunner to process multiple VCF files concurrently,
    normalizing them against a reference genome using bcftools. If a reference file
    is not provided, it will automatically download the appropriate reference genome
    based on the specified build.
    
    Attributes
    ----------
    build : str
        Genome build version, either '37' or '38'. Defaults to '38'.
    output_prefix : str
        Prefix to add to the output files. Defaults to 'normalized-'.
    reference_file : Path, optional
        Path to the reference genome file used for normalization. Defaults to None.
        If None or the file does not exist, it will be downloaded automatically based on the build.
    (See `ParallelTaskRunner` for inherited attributes.)
    
    Note
    ----
    bcftools must be installed and available in the system path
    """

    def __init__(self, input_path: Path, output_path: Path, max_workers: Optional[int] = None, build: str = '38', output_prefix: str = 'normalized-', reference_file: Optional[Path] = None) -> None:
        super().__init__(input_path, output_path, max_workers)
        self.build = build
        self.output_prefix = output_prefix
        self.reference_file = reference_file

    def execute_task(self) -> None:
        """Execute the post-imputation normalization task with reference genome.
        
        This method normalizes VCF files using a reference genome. If no reference file is provided,
        it automatically downloads the appropriate reference genome based on the build parameter.

        
        Returns
        -------
        None

        Raises
        ------
        TypeError 
            If output_prefix is not a string.
        
        Notes
        -----
        This method collects uncompressed dose VCF files using a pattern match and normalizes them against the reference genome. The downloaded reference genomes come from the 1000 Genomes Project.
        """

        if not isinstance(self.output_prefix, str):
            raise TypeError(f"prefix should be of type str, got {type(self.output_prefix)}")
        
        if not self.reference_file or not self.reference_file.exists():
            if self.build == '37':

                assemb37 = AssemblyReferenceFetcher(
                        base_url='https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/phase2_reference_assembly_sequence/',
                        build='37',
                        extension='.fa.gz'
                )
                assemb37.get_reference_url()
                assemb37.download_reference_file()
                assemb37.unzip_reference_file()
                self.reference_file = assemb37.file_path

            elif self.build == '38':

                assemb38 = AssemblyReferenceFetcher(
                        base_url='https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/GRCh38_reference_genome/',
                        build='38',
                        extension='.fa'
                )
                assemb38.get_reference_url()
                assemb38.download_reference_file()
                assemb38.unzip_reference_file()
                self.reference_file = assemb38.file_path

        self._file_collector('uncompressed-*dose.vcf.gz')

        task_args = {'output_prefix': self.output_prefix}

        self._run_task(
            self.normalize_with_reference,
            task_args=task_args,
            desc="Normalizing VCF files with Reference"
        )

        return
    
    def normalize_with_reference(self, input_file: Path, output_prefix: str = 'normalized-') -> None:
        """Normalize a VCF file with a reference genome using bcftools.
        
        This method takes an input VCF file and normalizes it against a reference genome
        using bcftools norm. The normalized output is compressed with gzip (-Oz).
        
        Parameters
        ----------
        input_file : Path
            Path to the input VCF file to be normalized.
        output_prefix : str, default='normalized-'
            Prefix to add to the output filename.
        
        Returns
        -------
        None
            The method doesn't return a value but creates a normalized VCF file
            at the output_path location.
        
        Raises
        ------
        TypeError
            If output_prefix is not a string.
        subprocess.CalledProcessError
            If the bcftools command fails.
        FileNotFoundError
            If the input file cannot be found.
        
        Notes
        -----
        The output filename is constructed from the output_prefix and the
        base name extracted from the input filename (after the first hyphen).
        """

        if not isinstance(output_prefix, str):
            raise TypeError(f"output_prefix should be of type str, got {type(output_prefix)}")
        
        base_name = input_file.name.split('-')[1]

        output_file = self.output_path / (output_prefix + base_name)

        # Normalize with `bcftools norm -Ou -m -any`
        bcf_cmd = [
            "bcftools", "norm", "-Oz", "-f", self.reference_file, "-o", output_file, input_file
        ]

        chr_number = os.path.basename(input_file)
        try:
            # execute bcftools command
            subprocess.run(bcf_cmd, check=True)
            logger.info(f"Chromosome {chr_number}: Completed")
        except subprocess.CalledProcessError as e:
            logger.error(f"Chromosome {chr_number}: Failed with error {e}")
        except FileNotFoundError:
            logger.error(f"Chromosome {chr_number}: Input file not found")
        pass

class IndexVCF(ParallelTaskRunner):
    """A class for indexing VCF (Variant Call Format) files using bcftools in parallel.
    
    This class extends ParallelTaskRunner to enable parallel processing of multiple VCF files.
    It creates index files that facilitate quick random access to compressed VCF files.
    
    Attributes
    ----------
    pattern : str, optional
        The glob pattern to match VCF files for indexing. Defaults to ``normalized-*dose.vcf.gz``.
    (See `ParallelTaskRunner` for inherited attributes.)

    Raises
    ------
    TypeError
        If pattern is not a string.
    
    Note
    ----
    bcftools must be installed and available in the system path
    """

    def __init__(self, input_path: Path, output_path: Path, max_workers: Optional[int] = None, pattern: str = 'normalized-*dose.vcf.gz') -> None:
        super().__init__(input_path, output_path, max_workers)

        if not isinstance(pattern, str):
            raise TypeError(f"pattern should be of type str, got {type(pattern)}")
        self.pattern = pattern

    def execute_task(self) -> None:
        """Execute the task of indexing VCF files.

        This method collects files based on the provided pattern and indexes
        the VCF files.

        Returns
        -------
        None
        """

        task_args = dict()

        self._file_collector(self.pattern)
        self._run_task(
            self.index_vcf,
            task_args=task_args,
            desc="Indexing VCF files"
        )
        return
    
    def index_vcf(self, input_file: Path) -> None:
        """Index a VCF file using bcftools.

        This method creates an index for the specified VCF file using bcftools,
        which is required for efficient querying and processing of VCF files.

        Parameters
        ----------
        input_file: Path
            Path to the VCF file to be indexed. Must be an existing file.

        Returns
        -------
        None

        Raises
        ------
        FileExistsError
            If the input file does not exist.
        """

        if not os.path.isfile(input_file):
            raise FileExistsError(f"Input file {input_file} does not exist")

        # Build the bcftools index command
        command = ["bcftools", "index", input_file]

        # Execute the command
        try:
            subprocess.run(command, check=True)
            print(f"Successfully indexed: {input_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error indexing {input_file}: {e}")

        pass

class AnnotateVCF(ParallelTaskRunner):
    """A parallel task runner for annotating normalized VCF files using reference annotation.
    
    This class provides functionality to annotate normalized VCF files with identifiers
    from a reference annotation file using bcftools. It processes multiple VCF files in 
    parallel, making it efficient for large genomic datasets.

    The class identifies all normalized VCF files matching a specified pattern and
    annotates them using the provided reference annotation file. It adds identifiers
    from the reference file to the VCF entries.
    
    Attributes
    ----------
    output_prefix : str, optional
        Prefix to add to the output files. Defaults to 'annotated-'.
    ref_annotation : Path
        Path to the reference annotation file used for annotating VCF files.
    (See `ParallelTaskRunner` for inherited attributes.)

    Raises
    ------
    TypeError
        If ref_annotation is not a Path object or output_prefix is not a string.
    FileNotFoundError
        If the reference annotation file does not exist.
    IsADirectoryError
        If the reference annotation file is not a file.
    
    Note
    ----
    This class requires bcftools to be installed and available in the system path.
    """

    def __init__(self, input_path: Path, output_path: Path, ref_annotation: Path, max_workers: Optional[int] = None, output_prefix: str = 'annotated-') -> None:
        super().__init__(input_path, output_path, max_workers)

        if not isinstance(ref_annotation, Path):
            raise TypeError(f"ref_annotation should be of type Path, got {type(ref_annotation)}")
        if not isinstance(output_prefix, str):
            raise TypeError(f"output_prefix should be of type str, got {type(output_prefix)}")
        if not ref_annotation.exists():
            raise FileNotFoundError(f"Reference annotation file {ref_annotation} does not exist.")
        if not ref_annotation.is_file():
            raise IsADirectoryError(f"Reference annotation file {ref_annotation} is not a file.")
        
        self.ref_annotation= ref_annotation
        self.output_prefix = output_prefix

    def execute_task(self) -> None:
        """Annotates normalized VCF files using a reference annotation file.
        
        This method collects all normalized VCF files matching the pattern ``normalized-*dose.vcf.gz`` 
        and annotates them using the provided reference annotation file. The annotated files 
        will be saved with the specified output prefix.
        
        Returns
        -------
        None
        """

        task_args = {'ref_annotation': self.ref_annotation, 'output_prefix': self.output_prefix}
        if not isinstance(self.ref_annotation, Path):
            raise TypeError(f"ref_annotation should be of type Path, got {type(self.ref_annotation)}")
        if not isinstance(self.output_prefix, str):
            raise TypeError(f"prefix should be of type str, got {type(self.output_prefix)}")
        if not self.ref_annotation.exists():
            raise FileNotFoundError(f"Reference annotation file {self.ref_annotation} does not exist.")
        
        self._file_collector('normalized-*dose.vcf.gz')
        
        self._run_task(
            self.annotate_vcf,
            task_args=task_args,
            desc="Annotating VCF files"
        )

        return
    
    def annotate_vcf(self, input_file: Path, ref_annotation: Path, output_prefix: str = 'annotated-') -> None:
        """
        Annotates a VCF file with identifiers from a reference annotation file using bcftools.
        This method takes an input VCF file and annotates it with IDs from a reference
        annotation file. The annotated VCF is saved to a new file with the specified prefix.

        Parameters
        ----------
        input_file: Path
            Path to the input VCF file to be annotated.
        ref_annotation: Path 
            Path to the reference annotation file used for annotation.
        output_prefix: str (optional)
            Prefix to add to the output filename. Defaults to 'annotated-'.
        
        Returns
        -------
        None
        
        Raises
        ------
        FileExistsError 
            If the input file does not exist.
        IsADirectoryError 
            If the input file is a directory, not a file.
        TypeError 
            If ref_annotation is not a Path object or output_prefix is not a string.
        subprocess.CalledProcessError 
            If the bcftools command fails.
        FileNotFoundError 
            If the input file is not found during execution.
        """

        if not input_file.exists():
            raise FileExistsError(f"Input file {input_file} does not exist")
        if not input_file.is_file():
            raise IsADirectoryError(f"Input file {input_file} is not a file")
        if not isinstance(ref_annotation, Path):
            raise TypeError(f"ref_annotation should be of type Path, got {type(ref_annotation)}")
        if not isinstance(output_prefix, str):
            raise TypeError(f"output_prefix should be of type str, got {type(output_prefix)}")
        
        base_name = input_file.name.split('-')[-1]

        output_file = self.output_path / (output_prefix + base_name)

        # Annotate with `bcftools annotate -a`
        bcf_cmd = [
            "bcftools", "annotate",
            "--annotations", ref_annotation,
            "--columns", "ID",
            "--output", output_file,
            input_file
        ]

        chr_number = os.path.basename(input_file)
        try:
            # execute bcftools command
            subprocess.run(bcf_cmd, check=True)
            logger.info(f"Chromosome {chr_number}: Completed")
        except subprocess.CalledProcessError as e:
            logger.error(f"Chromosome {chr_number}: Failed with error {e}")
        except FileNotFoundError:
            logger.error(f"Chromosome {chr_number}: Input file not found")
        pass

class ProcessVCF:
    """ProcessVCF class for post-imputation processing of Variant Call Format (VCF) files.

    This class provides a pipeline for processing VCF files through multiple sequential steps:
    
    1. Unzipping VCF files (if compressed)
    2. Filtering variants based on imputation quality (R²)
    3. Normalizing variant representation
    4. Normalizing against a reference genome
    5. Indexing the normalized VCF files
    6. Annotating variants with additional information
    7. Concatenating multiple VCF files into a single output file

    Attributes
    ----------
    input_path : Path
        Path to the directory containing input VCF files.
    output_path : Path
        Path to the directory where processed files will be saved.

    Raises
    ------
    TypeError
        If `input_path` or `output_path` is not of type `Path`.
    FileNotFoundError
        If `input_path` or `output_path` does not exist.
    NotADirectoryError
        If `input_path` or `output_path` is not a directory.

    Notes
    -----
    - A subdirectory named `process_vcf` is created inside the `input_path` directory
      for storing intermediate files during processing.
    - This class is designed to handle multiple sequential steps in VCF file processing,
      such as unzipping, filtering, normalizing, and annotating.

    Note
    ----
    This class requires bcftools to be installed and available in the system path.
    """

    def __init__(self, input_path: Path, output_path: Path) -> None:
        
        if not isinstance(input_path, Path):
            raise TypeError(f"input_path should be of type Path, got {type(input_path)}")
        if not isinstance(output_path, Path):
            raise TypeError(f"output_path should be of type Path, got {type(output_path)}")
        if not input_path.exists():
            raise FileNotFoundError(f"Input path {input_path} does not exist.")
        if not output_path.exists():
            raise FileNotFoundError(f"Output path {output_path} does not exist.")
        if not input_path.is_dir():
            raise NotADirectoryError(f"Output path {input_path} is not a directory.")
        if not output_path.is_dir():
            raise NotADirectoryError(f"Output path {output_path} is not a directory.")
        
        self.input_path = input_path
        self.output_path= output_path

        self.process_vcf = self.output_path / 'process_vcf'
        self.process_vcf.mkdir(parents=True, exist_ok=True)

        pass

    def execute_unzip(self, password: Optional[str] = None) -> None:
        """Unzips a VCF file using the UnzipVCF utility.
        
        This method creates an instance of UnzipVCF with the input and process paths
        from the current object, then executes the unzipping task. If the VCF file
        is password-protected, a password can be provided.
        
        Parameters
        ----------
        password : str, optional 
            Password for the protected zip file. Defaults to None.
        
        Returns
        -------
        None
        """
        
        unzipper = UnzipVCF(
            input_path = self.input_path,
            output_path=self.process_vcf,
            password   =password
        )

        unzipper.execute_task()

        return

    def execute_filter(self, r2_threshold: float = 0.3) -> None:
        """Execute a filtering operation on VCF data based on R² threshold.

        This method filters variants in the processed VCF file by creating and 
        executing a FilterVariants object with the specified R² threshold.
        Both input and output are set to the same process_vcf file.

        Parameters
        ----------
        r2_threshold : float, optional
            The R² threshold value for filtering variants. Variants with R² value below this threshold will be filtered out. Default is 0.3.

        Returns
        -------
        None
        """

        filter = FilterVariants(
            input_path  =self.process_vcf,
            output_path =self.process_vcf,
            r2_threshold=r2_threshold
        )
        filter.execute_task()

        return
    
    def execute_normalize(self) -> None:
        """Normalizes the VCF file using the NormalizeVCF class.
        
        This method creates a NormalizeVCF object with the current processed VCF file
        as both input and output, then executes the normalization task. The normalization
        process updates the VCF file in place.
        
        Returns
        -------
        None
        """
        
        normalizer = NormalizeVCF(
            input_path = self.process_vcf,
            output_path=self.process_vcf
        )
        normalizer.execute_task()

        return
    
    def execute_reference_normalize(self, build: str = '38', ref_genome: Optional[Path] = None) -> None:
        """Normalize the VCF file against a reference genome.
        
        This method creates a ReferenceNormalizeVCF object and executes the normalization 
        task on the processed VCF file, using the specified genome build or reference file.
        
        Parameters
        ----------
        build : str, optional 
            Genome build version to use. Defaults to '38'.
        reference_file : Path, optional 
            Path to a custom reference file. If provided, this will be used instead of the default reference for the specified build. Defaults to None.
        
        Returns
        -------
        None
        """
        
        reference_normalizer = ReferenceNormalizeVCF(
            input_path =self.process_vcf,
            output_path=self.process_vcf,
            build      =build,
            reference_file=ref_genome
        )
        reference_normalizer.execute_task()

        return
    
    def execute_index(self, pattern: str = 'normalized-*dose.vcf.gz') -> None:
        """Index VCF files matching a specific pattern.

        This method creates an indexer for VCF files and executes the indexing task
        on files that match the given pattern in the process_vcf directory.

        Parameters
        ----------
        pattern : str, optional 
            The glob pattern to match VCF files for indexing. Defaults to ``normalized-*dose.vcf.gz``.

        Returns
        -------
        None
        """

        indexer = IndexVCF(
            input_path = self.process_vcf,
            output_path=self.process_vcf,
            pattern=pattern
        )
        indexer.execute_task()

        return
    
    def execute_annotate(self, ref_annotation: Path, output_prefix: str = 'annotated-') -> None:
        """Annotates a VCF file using a reference annotation file.
        
        This method initializes an AnnotateVCF object and executes the annotation
        process on the current VCF file.
        
        Parameters
        ----------
        ref_annotation : Path
            Path to the reference annotation file.
        output_prefix : str, optional
            Prefix to be added to the output file name. Default is 'annotated-'.
        
        Returns
        -------
        None
        """
        
        annotator = AnnotateVCF(
            input_path    =self.process_vcf,
            output_path   =self.process_vcf,
            ref_annotation=ref_annotation,
            output_prefix =output_prefix
        )
        annotator.execute_task()

        return
    
    def execute_concatenate(self, output_name: str, max_threads: Optional[int] = None) -> None:
        """Concatenates annotated VCF files using bcftools concat.
        
        This method finds all annotated VCF files in the process_vcf directory, 
        sorts them, and concatenates them into a single compressed VCF file.
        
        Parameters
        ----------
        output_name : str 
            Name of the output file.
        max_threads : int (optional) 
            Maximum number of threads to use for concatenation. If None, uses min(8, os.cpu_count()). Defaults to None.
        
        Returns
        -------
        None

        Raises
        ------
        TypeError 
            If output_name is not a string.
        FileNotFoundError 
            If no annotated VCF files are found in the process_vcf directory.
        ValueError 
            If max_threads is less than 1.
        
        Notes
        -----
        The output file will be saved in the output_path directory.
        The method uses the 'bcftools concat' command with Oz compression.
        """
        
        if not isinstance(output_name, str):
            raise TypeError(f"output_file should be of type str, got {type(output_file)}")
        
        if output_name.endswith('.vcf'):
            output_name += '.gz' 
        if not output_name.endswith('.vcf.gz'):
            output_name += '.vcf.gz'
        
        output_path = self.output_path / output_name

        input_files = list(self.process_vcf.glob('annotated*.vcf.gz'))
        input_files.sort()
        if not input_files:
            raise FileNotFoundError(f"No VCF files annotated VCF files found in {self.process_vcf}")
        
        if not max_threads:
            cpu_count = os.cpu_count() or 1  # Default to 1 if cpu_count returns None
            max_threads = min(8, cpu_count)
        if max_threads < 1:
            raise ValueError(f"max_threads should be at least 1, got {max_threads}")

        # Concatenate with `bcftools concat`
        command = [
            "bcftools", "concat",
            *input_files,  # List of input files
            "--threads", str(max_threads),
            "-Oz",
            "-o", output_path
        ]

        try:
            subprocess.run(command, check=True)
            logger.info(f"Successfully concatenated and outputted to: {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error concatenating VCF files: {e}")
        pass

class GetPLINK:

    """A class for converting concatenated VCF files to PLINK binary format.

    This class handles conversion of a concatenated VCF file to a PLINK binary ready for further analysis.

    Attributes
    ----------
    input_path : Path
        Directory path where the input VCF file is located.
    output_path : Path
        Directory path where the output files will be saved.
    input_name : str
        Name of the input VCF file (must end with .vcf or .vcf.gz).
    output_name : str, optional
        Name for the output file. If not provided, it will be derived from input_name.
        
    Raises
    ------
    TypeError
        If input_path or output_path is not a Path object, or if input_name or output_name is not a string.
    FileNotFoundError
        If input_path or output_path does not exist.
    NotADirectoryError
        If input_path or output_path is not a directory.
    ValueError
        If input_name is not provided or if it doesn't end with .vcf or .vcf.gz.
    """

    def __init__(self, input_path: Path, input_name: str, output_path: Path, output_name: str) -> None:
        

        if not isinstance(input_path, Path):
            raise TypeError(f"input_path should be of type Path, got {type(input_path)}")
        if not isinstance(output_path, Path):
            raise TypeError(f"output_path should be of type Path, got {type(output_path)}")
        if not input_path.exists():
            raise FileNotFoundError(f"Input path {input_path} does not exist.")
        if not output_path.exists():
            raise FileNotFoundError(f"Output path {output_path} does not exist.")
        if not input_path.is_dir():
            raise NotADirectoryError(f"Output path {input_path} is not a directory.")
        if not output_path.is_dir():
            raise NotADirectoryError(f"Output path {output_path} is not a directory.")
        
        if input_name:
            if not isinstance(input_name, str):
                raise TypeError(f"input_name should be of type str, got {type(input_name)}")
            if not (input_name.endswith('.vcf') or input_name.endswith('.vcf.gz')):
                raise ValueError(f"input_name should be a VCF file, got {input_name}")
        else:
            raise ValueError("input_name must be provided")

        if not output_name:
            output_name = input_name.split('.vcf')[0]
        else:
            if not isinstance(output_name, str):
                raise TypeError(f"output_name should be of type str, got {type(output_name)}")
        
        self.input_path = input_path
        self.output_path= output_path
        self.input_name = input_name
        self.output_name = output_name

        self.analysis_ready = self.input_path / 'analysis_ready'
        self.analysis_ready.mkdir(parents=True, exist_ok=True)
        
        pass

    def convert_vcf_to_plink(self, double_id: bool = True, threads: Optional[int] = None, memory: Optional[int] = None) -> None:
        """Convert a VCF file to PLINK binary format (.bed, .bim, .fam).
        
        This method runs the plink2 command-line tool to convert the input VCF file to PLINK
        binary format, filtering for SNPs with standard ACGT alleles only.
        
        Parameters
        ----------
        double_id : bool, optional 
            Whether to use the --double-id flag in plink2 command, which sets both FID and IID to the sample ID. Defaults to True.
        threads : int, optional 
            Number of CPU threads to use. If None, defaults to (available CPU cores - 2) or 10 if CPU count can't be determined.
        memory : int, optional
            Memory allocation in MB for plink2. If None, defaults to approximately 2/3 of available system memory.

        Returns
        -------
        None
        
        Side Effects
        ------------
        Creates PLINK binary files (.bed, .bim, .fam) in the self.analysis_ready directory with the prefix self.output_name + "-nosex".
        
        Raises
        ------
        subprocess.CalledProcessError 
            If the plink2 command execution fails.
        """

        if threads is None:
            cpu_count = os.cpu_count()
            if cpu_count is not None:
                threads = max(1, cpu_count - 2)  # Ensure at least 1 thread
            else:
                threads = 10

        if memory is None:
            # get virtual memory details
            memory_info = psutil.virtual_memory()
            available_memory_mb = memory_info.available / (1024 * 1024)
            memory = int(round(2*available_memory_mb/3,0))

        if double_id:
            # plink2 command
            plink2_cmd = [
                "plink2",
                "--vcf", (self.input_path / self.input_name).as_posix(),
                "--snps-only", "just-acgt", "--double-id",
                "--make-bed",
                "--out", (self.analysis_ready / (self.output_name + "-nosex")).as_posix(),
                "--threads", str(threads),
                "--memory", str(memory)
            ]
        else:
            # plink2 command
            plink2_cmd = [
                "plink2",
                "--vcf", (self.input_path / self.input_name).as_posix(),
                "--snps-only", "just-acgt",
                "--make-bed",
                "--out", (self.analysis_ready / (self.output_name + "-nosex")).as_posix(),
                "--threads", str(threads),
                "--memory", str(memory)
            ]

        # execute plink2 command
        try:
            subprocess.run(plink2_cmd, check=True)
            print(f"PLINK2 command executed successfully. Output files saved with prefix: {self.output_name}-nosex")
        except subprocess.CalledProcessError as e:
            print(f"Error running PLINK2: {e}")

        pass

    def update_fam(self, for_fam_update_file: Path, threads: Optional[int] = None) -> None:
        """Add family information to the PLINK .fam file.

        This method reads a family information file and updates the PLINK .fam file
        using the provided family information, via PLINK2.

        Parameters
        ----------
        for_fam_update_file : Path
            Path to the family information file (.fam or without suffix).
        threads : int, optional
            Number of threads to use for PLINK2 (defaults to available CPUs - 2).

        Returns
        -------
        None
        """
        if not for_fam_update_file:
            raise ValueError("for_fam_update_file must be provided")

        if not isinstance(for_fam_update_file, Path):
            raise TypeError(f"for_fam_update_file should be of type Path, got {type(for_fam_update_file)}")

        fam_file = for_fam_update_file

        # Ensure the path points to a .fam file
        if not fam_file.as_posix().endswith('.fam'):
            fam_file = Path(str(fam_file) + '.fam')

        # Check existence and type
        if not fam_file.exists():
            raise FileNotFoundError(f"Family information file {fam_file} does not exist.")
        if not fam_file.is_file():
            raise IsADirectoryError(f"Family information file {fam_file} is not a file.")

        logger.info(f"Updating family information in {self.output_name}-nosex.fam with {for_fam_update_file}")
   
        if threads is None:
            cpu_count = os.cpu_count()
            if cpu_count is not None:
                threads = max(1, cpu_count - 2)  # Ensure at least 1 thread
            else:
                threads = 10
        
        # PLINK2 command
        plink2_cmd = [
            "plink2",
            "--bfile", (self.analysis_ready / (self.output_name + "-nosex")).as_posix(),
            "--make-bed",
            "--out", (self.analysis_ready / self.output_name).as_posix(),
            "--fam", fam_file.as_posix(),
            "--threads", str(threads)
        ]

        # execute plink2 command
        try:
            subprocess.run(plink2_cmd, check=True)
            print(f"PLINK2 command executed successfully. Output files saved with prefix: {self.output_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error running PLINK2: {e}")

        pass
    