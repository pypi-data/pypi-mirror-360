#!/usr/bin/env python
"""
File: base.py
Description: Next-generation sequencing (NGS) data analysis module.
CreateDate: 2025/4/18
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Dict, List
from os import makedirs
from os.path import abspath, exists
from re import sub
from shutil import which
from click import echo
from pybioinformatic.task_manager import TaskManager
from pybioinformatic.util import FuncDict


def check_cmds(cmds_list: List[str]):
    """
    Check if the required commands are available in the system's PATH.

    This function iterates through a list of command names, checking if each
    command is present in the system's PATH using the `which` function. If a
    command is found, its path is printed to standard error, and True is appended
    to the internal tracking list. If a command is not found, an error message is
    printed, and False is appended to the list. If any command is missing, the
    program will terminate.

    Parameters:
    cmds_list (List[str]): A list of command names to check for availability.

    Returns:
    None

    Raises:
    SystemExit: If any of the commands in the list are not found in the system's
                PATH, the program will terminate.
    """
    flag = []
    echo('\033[36mCheck dependency.\033[0m', err=True)
    for software in cmds_list:
        path = which(software)
        if path:
            echo(f'{software}: {path}', err=True)
            flag.append(True)
        else:
            echo(f'{software}: command not found', err=True)
            flag.append(False)
    if not all(flag):
        exit()


def check_R_packages(packages_list: List[str]):
    """
    Check if the specified R packages are installed on the system.

    This function iterates through a list of R package names and verifies their
    installation by executing an R command. If a package is not installed, an error
    message is displayed, and the program terminates if any package is missing.

    Parameters
    ----------
    packages_list : List[str]
        A list of R package names to be checked for installation.

    Returns
    -------
    None

    Raises
    ------
    SystemExit
        If any of the specified R packages are not installed, the program will exit.

    Notes
    -----
    The function uses an external TaskManager instance to execute shell commands.
    Ensure that the TaskManager class is properly configured and available in the
    environment. The R command checks for the availability of each package using
    requireNamespace with the `quietly = TRUE` option.

    Warnings
    --------
    Missing R packages will trigger an error message printed to stderr. Ensure all
    required packages are installed before running this check in critical workflows.
    """
    flag = []
    tkm = TaskManager(num_processing=1)
    for package in packages_list:
        cmd = f'''R CMD Rscript -e 'if(requireNamespace("{package}", quietly = TRUE)) {print("True")} else {print("False")}' '''
        stdout = tkm.echo_and_exec_cmd(cmd=cmd, show_cmd=False)
        if 'True' in stdout:
            flag.append(True)
        else:
            flag.append(False)
            echo(f'\033[31mR package {package} has not been installed.\033[0m', err=True)
    if not all(flag):
        exit()


def parse_sample_info(sample_info: str) -> Dict[str, list]:
    """
    Parse sample information from a file and return it as a dictionary.

    This function reads a tab-separated file containing sample information and
    constructs a dictionary where each key is a sample name, and the value is a
    list of associated data such as read paths and comparative combinations.
    The function validates the input file for common issues like missing fields
    or invalid file paths.

    Parameters
    ----------
    sample_info : str
        Path to the file containing sample information. The file should be
        tab-separated with at least three columns: sample name, read1 path,
        and read2 path.
        For RNA-seq, the fourth column is sample comparative combinations.
        For ChIP-seq, the first and second columns are read1 and read2 path
        of ChIP, the fourth column is reference genome path, and the fifth
        and sixth columns are read1 and read2 path of Input.

    Returns
    -------
    Dict[str, list]
        A dictionary where keys are sample names (str) and values are lists
        containing read paths and additional comparative combinations.

    Raises
    ------
    ValueError
        If the file contains lines with fewer than three tab-separated values.
    FileNotFoundError
        If the provided file path does not exist or cannot be opened.
    OSError
        If there are issues accessing or reading the file system.

    Notes
    -----
    - The function assumes the first column in the file corresponds to the
      sample name, the second column to the read1 path, and the third column
      to the read2 path.
    - Additional columns beyond the third are treated as part of the comparative
      combination for RNA-seq analysis.
    - Errors related to invalid paths or malformed lines are reported to the
      standard error stream with line numbers for easier debugging.
    """
    sample_info_dict: Dict[str, List[str]] = {}
    # for RNA-seq:
    # {
    #   sample_name: [read1_path, read2_path, comparative_combination, ...],
    #   ...
    # }
    # for ChIP-seq:
    # {
    #   sample_name: [read1_path_of_ChIP, read2_path_of_ChIP, ref_genome, read1_path_of_Input, read2_path_of_Input,...],
    #   ...
    # }
    with open(sample_info) as f:
        line_num = 0
        for line in f:
            line_num += 1
            split = line.strip().split('\t')
            if len(split) < 3:
                echo(f'\033[31mError: Invalid sample info at line {line_num}.\033[0m', err=True)
            elif not exists(split[1]):
                echo(f'\033[31mError: Invalid read1 path at line {line_num}.\033[0m', err=True)
            elif not exists(split[2]):
                echo(f'\033[31mError: Invalid read2 path at line {line_num}.\033[0m', err=True)
            else:
                sample_info_dict[split[0]] = split[1:]
    return sample_info_dict


def build_ref_index(
    fasta_file: str,
    bwa_exe: str = None,
    gatk_exe: str = None,
    samtools_exe: str = None,
    hisat2_build_exe: str = None,
    bowtie_build: str = None,
    bowtie2_build: str = None,
    large: bool = False
) -> str:
    software_list = [
        which(i)
        for i in [bwa_exe, gatk_exe, samtools_exe, hisat2_build_exe, bowtie_build, bowtie2_build]
        if i is not None and which(i)
    ]
    if not software_list:
        msg = '\033[33mWaring: No any valid executable file was specified, ignore building any index of fasta file.\033[0m'
        echo(msg, err=True)
        exit()
    fasta_file = abspath(fasta_file)
    cmd_dict = {
        'bwa': f' index {fasta_file} {fasta_file}',
        'gatk': f' CreateSequenceDictionary -R {fasta_file}',
        'samtools': f' faidx {fasta_file}',
        'hisat2-build': f' {fasta_file} {fasta_file}',
        'bowtie-build': f' {fasta_file} {fasta_file}',
        'bowtie2-build': f' {fasta_file} {fasta_file}',
    }
    try:
        cmd = '\n'.join(
            [
                i + cmd_dict[i.split('/')[-1]]
                for i in software_list
            ]
        )
    except KeyError as s:
        echo(f'\033[31mError: Invalid command {s}.\033[0m', err=True)
        exit()
    else:
        if large:
            cmd = sub('build ', 'build --large-index ', cmd)
    return cmd


class NGSAnalyser:
    """
    \033[32mNext-generation sequencing (NGS) data analysis pipeline.\033[0m

    \033[34m:param read1: Pair end read1 fastq file.\033[0m
    \033[34m:param read2: Pair end read2 fastq file.\033[0m
    \033[34m:param ref_genome: Reference genome fasta file.\033[0m
    \033[34m:param output_path: Output path.\033[0m
    \033[34m:param num_threads: Number of threads.\033[0m
    \033[34m:param sample_name: Sample name.\033[0m
    \033[34m:param exe_path_dict: Software executable file path dict.\033[0m
    """

    _exe_set = {'fastp', 'bwa', 'samtools', 'hisat2', 'gatk', 'bowtie', 'bowtie2'}

    def __init__(
        self,
        read1: str,
        read2: str,
        ref_genome: str,
        output_path: str,
        num_threads: int = 10,
        sample_name: str = None,
        exe_path_dict: Dict[str, str] = None
    ):
        if exe_path_dict is None:
            exe_path_dict = {}
        ## Input file
        self.read1 = abspath(read1)
        self.read2 = abspath(read2)
        self.ref_genome = abspath(ref_genome)
        self.output_path = abspath(output_path)
        self.num_threads = num_threads
        self.sample_name = self.read1.split('/')[-1].split('.')[0] if sample_name is None else sample_name
        self.exe_path_dict = FuncDict(
            {
                k: which(v)
                for k, v in exe_path_dict.items()
                if k in self._exe_set and which(v) is not None
            }
        )
        ## Key output file
        # QC results file
        self.qc_path = f'{self.output_path}/01.QC/{self.sample_name}'
        self.read1_clean = f'{self.qc_path}/{self.sample_name}_1_clean.fq.gz'
        self.read2_clean = f'{self.qc_path}/{self.sample_name}_2_clean.fq.gz'
        # bwa mem results file
        self.mapping_path = f'{self.output_path}/02.mapping/{self.sample_name}'
        self.bwa_mem_raw_bam = f'{self.mapping_path}/{self.sample_name}.bwa.mem.sort.bam'
        self.bwa_mem_map30_bam = f'{self.mapping_path}/{self.sample_name}.bwa.mem.sort.map30.bam'
        self.bwa_mem_map30_markdup_bam = f'{self.mapping_path}/{self.sample_name}.bwa.mem.sort.map30.markdup.bam'
        self.bwa_mem_map30_markdup_bam_metrics = f'{self.mapping_path}/{self.sample_name}.bwa.mem.sort.map30.markdup.bam.metrics'
        # depth file
        self.depth = f'{self.mapping_path}/{self.sample_name}.bwa.mem.sort.map30.markdup.bam.depth'
        # bowtie2 reasults file
        self.bowtie2_raw_bam = f'{self.mapping_path}/{self.sample_name}.bt2.sort.bam'
        self.bowtie2_filtered_bam = f'{self.mapping_path}/{self.sample_name}.bt2.sort.filtered.bam'
        # hisat2 results file
        self.hisat2_raw_bam = f'{self.mapping_path}/{self.sample_name}.ht2.sort.bam'

    @staticmethod
    def other_options(cmd: str, other_options: dict):
        other_options = ' '.join([f'{k} {v}' for k, v in other_options.items()])
        cmd += f' {other_options}'
        return cmd

    def run_fastp(
        self,
        read1_raw: str = None,
        read2_raw: str = None,
        read1_clean: str = None,
        read2_clean: str = None,
        **other_options
    ):
        fastp = which(self.exe_path_dict['fastp'])
        read1_raw = abspath(read1_raw) if read1_raw else self.read1
        read2_raw = abspath(read2_raw) if read2_raw else self.read2
        read1_clean = abspath(read1_clean) if read1_clean else self.read1_clean
        read2_clean = abspath(read2_clean) if read2_clean else self.read2_clean
        makedirs(self.qc_path, exist_ok=True)
        cmd = (
            f'{fastp} '
            f'-w {self.num_threads} '
            f'-i {read1_raw} '
            f'-I {read2_raw} '
            f'-o {read1_clean} '
            f'-O {read2_clean}'
        )
        return self.other_options(cmd, other_options) if other_options else cmd

    def run_hisat2(
        self,
        read1_clean: str = None,
        read2_clean: str = None,
        out_bam: str = None,
        **other_options
    ):
        hisat2 = which(self.exe_path_dict['hisat2'])
        samtools = which(self.exe_path_dict['samtools'])
        read1_clean = abspath(read1_clean) if read1_clean else self.read1_clean
        read2_clean = abspath(read2_clean) if read2_clean else self.read2_clean
        out_bam = abspath(out_bam) if out_bam else self.hisat2_raw_bam
        makedirs(self.mapping_path, exist_ok=True)
        hisat2_cmd = (
            f'{hisat2} -p {self.num_threads} '
            f'-x {self.ref_genome} '
            f'-1 {read1_clean} '
            f'-2 {read2_clean} '
            f'--summary-file {self.mapping_path}/{self.sample_name}.ht2.log'
        )
        hisat2_cmd = self.other_options(hisat2_cmd, other_options) if other_options else hisat2_cmd
        cmd = f'{hisat2_cmd} | {samtools} sort -@ {self.num_threads} -T {self.sample_name} - -o {out_bam}'
        return cmd

    def run_bwa_mem(
        self,
        read1_clean: str = None,
        read2_clean: str = None,
        out_bam: str = None,
        **other_options
    ) -> str:
        bwa = which(self.exe_path_dict['bwa'])
        samtools = which(self.exe_path_dict['samtools'])
        read1_clean = abspath(read1_clean) if read1_clean else self.read1_clean
        read2_clean = abspath(read2_clean) if read2_clean else self.read2_clean
        out_bam = abspath(out_bam) if out_bam else self.bwa_mem_raw_bam
        makedirs(self.mapping_path, exist_ok=True)
        bwa_cmd = (
            fr'{bwa} mem -t {self.num_threads} '
            fr'-R "@RG\tID:{self.sample_name}\tSM:{self.sample_name}\tPL:ILLUMINA" '
            fr'{self.ref_genome} {read1_clean} {read2_clean}'
        )
        bwa_cmd = self.other_options(bwa_cmd, other_options) if other_options else bwa_cmd
        cmd = f'{bwa_cmd} | {samtools} sort -@ {self.num_threads} -T {self.sample_name} -o {out_bam}'
        return cmd

    def filter_reads_by_mapQ(
        self,
        bam_file: str = None,
        out_bam: str = None,
        map_q: int = 30
    ) -> str:
        if map_q not in range(1, 60):
            msg = f'\033[31mError: Invalid mapping Q value: "{map_q}". It must be an integer between 0 and 60.\033[0m'
            echo(message=msg, err=True)
            exit()
        samtools = which(self.exe_path_dict['samtools'])
        makedirs(self.mapping_path, exist_ok=True)
        bam_file = abspath(bam_file) if bam_file else self.bwa_mem_raw_bam
        out_bam = abspath(out_bam) if out_bam else self.bwa_mem_map30_bam
        awk = r'''awk '{if($1~/@/){print}else{if( $7 == "=" &&  $5 >= %s ){print $0}}}' ''' % map_q
        cmd = f'{samtools} view -h {bam_file} | {awk}| samtools view -bS -T {self.ref_genome} - -o {out_bam}'
        return cmd

    def mark_duplicates(
        self,
        bam_file: str = None,
        out_bam: str = None,
        out_metrics: str = None,
        **other_options
    ) -> str:
        gatk = which(self.exe_path_dict['gatk'])
        samtools = which(self.exe_path_dict['samtools'])
        makedirs(self.mapping_path, exist_ok=True)
        bam_file = abspath(bam_file) if bam_file else self.bwa_mem_map30_bam
        out_bam = abspath(out_bam) if out_bam else self.bwa_mem_map30_markdup_bam
        out_metrics = abspath(out_metrics) if out_metrics else self.bwa_mem_map30_markdup_bam_metrics
        cmd = (
            f'{gatk} MarkDuplicates '
            f'-I {bam_file} '
            f'-M {out_metrics} '
            f'-O {out_bam}'
        )
        cmd = self.other_options(cmd, other_options) if other_options else cmd
        cmd += f'\n{samtools} index {out_bam}'
        return cmd

    def stats_depth(
        self,
        bam_file: str = None,
        out_depth: str = None,
        **other_options
    ) -> str:
        samtools = which(self.exe_path_dict['samtools'])
        makedirs(self.mapping_path, exist_ok=True)
        bam_file = abspath(bam_file) if bam_file else self.bwa_mem_map30_markdup_bam
        out_depth = abspath(out_depth) if out_depth else self.depth
        cmd = f'{samtools} depth {bam_file} -o {self.mapping_path}/{out_depth}'
        return self.other_options(cmd, other_options) if other_options else cmd

    def run_bowtie2(
        self,
        read1_clean: str = None,
        read2_clean: str = None,
        out_bam: str = None,
        **other_options
    ) -> str:
        bowtie2 = which(self.exe_path_dict['bowtie2'])
        samtools = which(self.exe_path_dict['samtools'])
        read1_clean = abspath(read1_clean) if read1_clean else self.read1_clean
        read2_clean = abspath(read2_clean) if read2_clean else self.read2_clean
        out_bam = abspath(out_bam) if out_bam else self.bowtie2_raw_bam
        makedirs(self.mapping_path, exist_ok=True)
        bowtie2_cmd = (
            f'{bowtie2} '
            f'-p {self.num_threads} '
            f'-x {self.ref_genome} '
            f'-1 {read1_clean} '
            f'-2 {read2_clean}'
        )
        bowtie2_cmd = self.other_options(bowtie2_cmd, other_options) if other_options else bowtie2_cmd
        cmd = f'{bowtie2_cmd} | {samtools} sort -@ {self.num_threads} -T {self.sample_name} -o {out_bam}'
        return cmd

    def filter_reads_by_samtools(
        self,
        bam_file: str = None,
        out_bam: str = None,
        **other_options
    ):
        samtools = which(self.exe_path_dict['samtools'])
        bam_file = abspath(bam_file) if bam_file else self.bowtie2_raw_bam
        out_bam = abspath(out_bam) if out_bam else self.bowtie2_filtered_bam
        cmd = f'{samtools} view {bam_file} -o {out_bam}'
        cmd = self.other_options(cmd, other_options) if other_options else cmd
        return cmd
