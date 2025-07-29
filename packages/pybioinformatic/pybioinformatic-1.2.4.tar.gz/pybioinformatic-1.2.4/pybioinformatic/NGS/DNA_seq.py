"""
File: DNA_seq.py
Description: DNA-seq analysis pipeline module.
CreateDate: 2025/4/18
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Dict
from os import makedirs
from os.path import abspath
from shutil import which
from pybioinformatic.NGS.base import NGSAnalyser
from pybioinformatic.util import FuncDict
from pybioinformatic.fasta import Fasta


class GatkSNPCalling(NGSAnalyser):
    """
    Variant calling pipeline using GATK tools.

    This class implements a complete pipeline for SNP calling using GATK's HaplotypeCaller, GenotypeGVCFs,
    and VariantFiltration tools. It handles the generation of GVCF and VCF files, applies filtering to
    variants, and integrates with other NGS analysis steps such as read alignment and quality control.

    Parameters:
        read1 (str): Path to the first paired-end FASTQ file.
        read2 (str): Path to the second paired-end FASTQ file.
        ref_genome (str): Path to the reference genome FASTA file.
        output_path (str): Directory where output files will be stored.
        num_threads (int): Number of threads to use for parallel processing. Default is 10.
        sample_name (str): Name of the sample being analyzed. If not provided, it will be inferred.
        exe_path_dict (Dict[str, str]): Dictionary mapping tool names to their executable paths.

    Returns:
        None

    Methods:
        run_HaplotypeCaller:
            Runs GATK HaplotypeCaller to generate a GVCF file from a BAM file.

            Parameters:
                bam_file (str): Path to the input BAM file. If not provided, uses the default BAM file.
                other_options: Additional options to pass to the HaplotypeCaller command.

            Returns:
                str: The constructed HaplotypeCaller command.

        run_GenotypeGVCFs:
            Runs GATK GenotypeGVCFs to generate a VCF file from a GVCF file.

            Parameters:
                gvcf_file (str): Path to the input GVCF file. If not provided, uses the default GVCF file.
                other_options: Additional options to pass to the GenotypeGVCFs command.

            Returns:
                str: The constructed GenotypeGVCFs command.

        run_VariantFiltration:
            Runs GATK VariantFiltration to filter variants in a VCF file based on specified criteria.

            Parameters:
                filter_expression (str): Expression used to filter variants. Default includes common filters.
                vcf_file (str): Path to the input VCF file. If not provided, uses the default VCF file.
                other_options: Additional options to pass to the VariantFiltration command.

            Returns:
                str: The constructed VariantFiltration command.

        pipeline:
            Executes the complete variant calling pipeline, including quality control, alignment,
            duplicate marking, and variant calling.

            Parameters:
                fastp_options (Dict[str, str]): Options for the fastp tool. Default includes JSON and HTML reports.
                bwa_mem_options (Dict[str, str]): Options for the BWA-MEM alignment tool.

            Returns:
                str: A concatenated string of all commands executed in the pipeline.
    """
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
        super().__init__(read1, read2, ref_genome, output_path, num_threads, sample_name, exe_path_dict)
        self.variant_path = f'{self.output_path}/03.variant/{self.sample_name}'
        self.gvcf = f"{self.variant_path}/{self.bwa_mem_map30_markdup_bam.split('/')[-1]}.gvcf"
        self.vcf = f"{self.variant_path}/{self.bwa_mem_map30_markdup_bam.split('/')[-1]}.vcf"
        self.filtered_vcf = f"{self.variant_path}/{self.bwa_mem_map30_markdup_bam.split('/')[-1]}.filtered.vcf"

    def run_HaplotypeCaller(
        self,
        bam_file: str = None,
        out_gvcf: str = None,
        **other_options
    ) -> str:
        gatk = which(self.exe_path_dict['gatk'])
        makedirs(self.variant_path, exist_ok=True)
        bam_file = abspath(bam_file) if bam_file else self.bwa_mem_map30_markdup_bam
        out_gvcf = abspath(out_gvcf) if out_gvcf else self.gvcf
        cmd = (f'{gatk} HaplotypeCaller '
               f'-ERC GVCF '
               f'-I {bam_file} '
               f'-R {self.ref_genome} '
               f'-O {out_gvcf}')
        return self.other_options(cmd, other_options) if other_options else cmd

    def run_GenotypeGVCFs(
        self,
        gvcf_file: str = None,
        out_vcf: str = None,
        **other_options
    ) -> str:
        gatk = which(self.exe_path_dict['gatk'])
        makedirs(self.variant_path, exist_ok=True)
        gvcf_file = abspath(gvcf_file) if gvcf_file else self.gvcf
        out_vcf = abspath(out_vcf) if out_vcf else self.vcf
        cmd = (
            f'{gatk} GenotypeGVCFs '
            f'-R {self.ref_genome} '
            f'-V {gvcf_file} '
            f'-O {out_vcf}'
        )
        return self.other_options(cmd, other_options) if other_options else cmd

    def run_VariantFiltration(
        self,
        filter_expression: str = 'QD < 2.0 || MQ < 40.0 || FS > 60.0 || SOR > 3.0',
        vcf_file: str = None,
        out_vcf: str = None,
        **other_options
    ) -> str:
        gatk = which(self.exe_path_dict['gatk'])
        makedirs(self.variant_path, exist_ok=True)
        vcf_file = abspath(vcf_file) if vcf_file else self.vcf
        out_vcf = abspath(out_vcf) if out_vcf else self.filtered_vcf
        cmd = (
            f'{gatk} VariantFiltration '
            f'--filter-name  "HARD_TO_VALIDATE" '
            f'--filter-expression "{filter_expression}" '
            f'-R {self.ref_genome} '
            f'-V {vcf_file} '
            f'-O {out_vcf}'
        )
        return self.other_options(cmd, other_options) if other_options else cmd

    def pipeline(
        self,
        fastp_options: Dict[str, str] = None,
        bwa_mem_options: Dict[str, str] = None
    ) -> str:
        if fastp_options is None:
            fastp_options = {
                    '-j': f'{self.qc_path}/{self.sample_name}.fastp.json',
                    '-h': f'{self.qc_path}/{self.sample_name}.fastp.html'
                }
        if bwa_mem_options is None:
            bwa_mem_options = {}
        cmds = (
            f'{self.run_fastp(**fastp_options)}\n\n'
            f'{self.run_bwa_mem(**bwa_mem_options)}\n\n'
            f'{self.filter_reads_by_mapQ()}\n\n'
            f'{self.mark_duplicates()}\n\n'
            f'{self.stats_depth()}\n\n'
            f'{self.run_HaplotypeCaller()}\n\n'
            f'{self.run_GenotypeGVCFs()}\n\n'
            f'{self.run_VariantFiltration()}'
        )
        return cmds


class Macs2PeakCalling:
    """
    Manages the peak calling process using MACS2 for ChIP-Seq data analysis.

    This class orchestrates the entire workflow for peak calling, starting from quality
    control of raw reads to alignment, post-processing of alignments, and finally
    peak calling using MACS2. It integrates with NGSAnalyser to handle individual steps
    such as read trimming, alignment, and filtering. The class also provides methods to
    generate commands for each step of the pipeline, which can be executed externally.

    Parameters:
        ChIP_read1 (str): Path to the first pair of ChIP-seq FASTQ file.
        ChIP_read2 (str): Path to the second pair of ChIP-seq FASTQ file.
        Input_read1 (str): Path to the first pair of input control FASTQ file.
        Input_read2 (str): Path to the second pair of input control FASTQ file.
        ref_genome (str): Path to the reference genome FASTA file.
        output_path (str): Directory where all output files will be stored.
        num_threads (int): Number of threads to use for parallel processing. Defaults to 10.
        sample_name (str): Name of the sample used for naming output files. Defaults to None.
        exe_path_dict (Dict[str, str]): Dictionary mapping executable names to their paths.
                                        Defaults to None.

    Returns:
        None

    Methods:
        other_options: Constructs additional command-line options from a dictionary.
        run_fastp: Generates commands for running fastp on ChIP and input reads.
        run_bowtie2: Generates commands for aligning reads using Bowtie2.
        mark_duplicates: Generates commands for marking duplicate reads in BAM files.
        filter_reads: Generates commands for filtering reads using Samtools.
        run_macs2: Generates commands for performing peak calling using MACS2.
    """
    _exe_set = {'macs2'}

    def __init__(
        self,
        ChIP_read1: str,
        ChIP_read2: str,
        Input_read1: str,
        Input_read2: str,
        ref_genome: str,
        output_path: str,
        num_threads: int = 10,
        sample_name: str = None,
        exe_path_dict: Dict[str, str] = None
    ):
        self.ref_genome = abspath(ref_genome)
        self.sample_name = sample_name
        self.output_path = abspath(output_path)
        self.num_threads = num_threads
        if exe_path_dict is None:
            exe_path_dict = {}
        self.exe_path_dict = FuncDict(
            {
                k: which(v)
                for k, v in exe_path_dict.items()
                if k in self._exe_set and which(v) is not None
            }
        )

        self.ChIP_NGSAnalyser = NGSAnalyser(
            read1=abspath(ChIP_read1),
            read2=abspath(ChIP_read2),
            ref_genome=abspath(ref_genome),
            output_path=output_path,
            num_threads=num_threads,
            sample_name=sample_name,
            exe_path_dict=exe_path_dict
        )

        self.Input_NGSAnalyser = NGSAnalyser(
            read1=abspath(Input_read1),
            read2=abspath(Input_read2),
            ref_genome=abspath(ref_genome),
            output_path=output_path,
            num_threads=num_threads,
            sample_name=sample_name,
            exe_path_dict=exe_path_dict
        )

        self.qc_path = f'{self.output_path}/01.QC/{self.sample_name}'
        self.mapping_path = f'{self.output_path}/02.mapping/{self.sample_name}'
        self.peaks_path = f'{self.output_path}/03.peaks/{self.sample_name}'

        self.ChIP_read1_clean = f'{self.qc_path}/{self.sample_name}_ChIP_1_clean.fq.gz'
        self.ChIP_read2_clean = f'{self.qc_path}/{self.sample_name}_ChIP_2_clean.fq.gz'
        self.ChIP_fastp_json = f'{self.qc_path}/{self.sample_name}_ChIP.fastp.json'
        self.ChIP_fastp_html = f'{self.qc_path}/{self.sample_name}_ChIP.fastp.html'

        self.Input_read1_clean = f'{self.qc_path}/{self.sample_name}_Input_1_clean.fq.gz'
        self.Input_read2_clean = f'{self.qc_path}/{self.sample_name}_Input_2_clean.fq.gz'
        self.Input_fastp_json = f'{self.qc_path}/{self.sample_name}_Input.fastp.json'
        self.Input_fastp_html = f'{self.qc_path}/{self.sample_name}_Input.fastp.html'

        self.ChIP_bowtie2_raw_bam = f'{self.mapping_path}/{self.sample_name}_ChIP.bt2.sort.bam'
        self.ChIP_bowtie2_markdup_bam = f'{self.mapping_path}/{self.sample_name}_ChIP.bt2.sort.markdup.bam'
        self.ChIP_bowtie2_markdup_bam_metrics = f'{self.mapping_path}/{self.sample_name}_ChIP.bt2.sort.markdup.bam.metrics'
        self.ChIP_bowtie2_markdup_filtered_bam = f'{self.mapping_path}/{self.sample_name}_ChIP.bt2.sort.markdup.filtered.bam'

        self.Input_bowtie2_raw_bam = f'{self.mapping_path}/{self.sample_name}_Input.bt2.sort.bam'
        self.Input_bowtie2_markdup_bam = f'{self.mapping_path}/{self.sample_name}_Input.bt2.sort.markdup.bam'
        self.Input_bowtie2_markdup_bam_metrics = f'{self.mapping_path}/{self.sample_name}_Input.bt2.sort.markdup.bam.metrics'
        self.Input_bowtie2_markdup_filtered_bam = f'{self.mapping_path}/{self.sample_name}_Input.bt2.sort.markdup.filtered.bam'

    @staticmethod
    def other_options(cmd: str, other_options: dict):
        other_options = ' '.join([f'{k} {v}' for k, v in other_options.items()])
        cmd += f' {other_options}'
        return cmd

    def run_fastp(self, **other_options) -> str:
        ChIP_qc_other_options = {
                '-j': self.ChIP_fastp_json,
                '-h': self.ChIP_fastp_html
            }
        if other_options:
            ChIP_qc_other_options.update(other_options)
        ChIP_qc_cmd = self.ChIP_NGSAnalyser.run_fastp(
            read1_clean=self.ChIP_read1_clean,
            read2_clean=self.ChIP_read2_clean,
            **ChIP_qc_other_options
        )

        Input_qc_other_options = {
                '-j': self.Input_fastp_json,
                '-h': self.Input_fastp_html
            }
        if other_options:
            Input_qc_other_options.update(other_options)
        Input_qc_cmd = self.Input_NGSAnalyser.run_fastp(
            read1_clean=self.Input_read1_clean,
            read2_clean=self.Input_read2_clean,
            **Input_qc_other_options
        )

        cmd = f'{ChIP_qc_cmd}\n{Input_qc_cmd}'
        return cmd

    def run_bowtie2(self, **other_options) -> str:
        ChIP_mapping_cmd = self.ChIP_NGSAnalyser.run_bowtie2(
            read1_clean=self.ChIP_read1_clean,
            read2_clean=self.ChIP_read2_clean,
            out_bam=self.ChIP_bowtie2_raw_bam,
            **other_options
        )
        Input_mapping_cmd = self.Input_NGSAnalyser.run_bowtie2(
            read1_clean=self.Input_read1_clean,
            read2_clean=self.Input_read2_clean,
            out_bam=self.Input_bowtie2_raw_bam,
            **other_options
        )
        cmd = f'{ChIP_mapping_cmd}\n{Input_mapping_cmd}'
        return cmd

    def mark_duplicates(self, **other_options) -> str:
        ChIP_markdup_cmd = self.ChIP_NGSAnalyser.mark_duplicates(
            bam_file=self.ChIP_bowtie2_raw_bam,
            out_bam=self.ChIP_bowtie2_markdup_bam,
            out_metrics=self.ChIP_bowtie2_markdup_bam_metrics,
            **other_options
        )
        Input_markdup_cmd = self.Input_NGSAnalyser.mark_duplicates(
            bam_file=self.Input_bowtie2_raw_bam,
            out_bam=self.Input_bowtie2_markdup_bam,
            out_metrics=self.Input_bowtie2_markdup_bam_metrics,
            **other_options
        )
        cmd = f'{ChIP_markdup_cmd}\n{Input_markdup_cmd}'
        return cmd

    def filter_reads(self, **other_options) -> str:
        ChIP_filter_cmd = self.ChIP_NGSAnalyser.filter_reads_by_samtools(
            bam_file=self.ChIP_bowtie2_markdup_bam,
            out_bam=self.ChIP_bowtie2_markdup_filtered_bam,
            **other_options
        )
        Input_filter_cmd = self.Input_NGSAnalyser.filter_reads_by_samtools(
            bam_file=self.Input_bowtie2_markdup_bam,
            out_bam=self.Input_bowtie2_markdup_filtered_bam,
            **other_options
        )
        cmd = f'{ChIP_filter_cmd}\n{Input_filter_cmd}'
        return cmd

    def run_macs2(
        self,
        genome_size: int = None,
        ChIP_bam: str = None,
        Input_bam: str = None,
        **other_options
    ) -> str:
        macs2 = which(self.exe_path_dict['macs2'])
        makedirs(self.peaks_path, exist_ok=True)
        ChIP_bam = abspath(ChIP_bam) if ChIP_bam else self.ChIP_bowtie2_markdup_filtered_bam
        Input_bam = abspath(Input_bam) if Input_bam else self.Input_bowtie2_markdup_filtered_bam
        if genome_size is None:
            with Fasta(self.ref_genome) as fa:
                genome_size = fa.get_size()
        cmd = (
            f'{macs2} callpeak '
            f'-t {ChIP_bam} '
            f'-c {Input_bam} '
            f'-g {genome_size} '
            f'-n {self.sample_name} '
            f'--outdir {self.peaks_path}'
        )
        return self.other_options(cmd, other_options) if other_options else cmd

    def pipeline(
        self,
        fastp_options: Dict[str, str] = None,
        bowtie2_options: Dict[str, str] = None,
        gatk_markduplicates_options: Dict[str, str] = None,
        samtools_filter_reads_options: Dict[str, str] = None,
        macs2_callpeak_options: Dict[str, str] = None
    ) -> str:
        """
        Executes a bioinformatics pipeline by chaining multiple commands together. This function
        allows customization of each step through optional parameters, providing default values
        for commonly used options if none are specified.

        The pipeline includes the following steps:
        1. Quality control using `fastp`.
        2. Alignment using `bowtie2` with default sensitive settings.
        3. Duplicate marking using `gatk MarkDuplicates`.
        4. Read filtering using `samtools`.
        5. Peak calling using `macs2`.

        Parameters
        ----------
        fastp_options : Dict[str, str]
            A dictionary of options to pass to the `fastp` command. If not provided,
            the default options of `run_fastp` will be used.
        bowtie2_options : Dict[str, str]
            A dictionary of options to pass to the `bowtie2` command. If not provided,
            the following defaults will be used:
            --very-sensitive, --no-mixed, --no-discordant, -k 10, -tq, -X 1000, -L 25.
        gatk_markduplicates_options : Dict[str, str]
            A dictionary of options to pass to the `gatk MarkDuplicates` command. If not
            provided, the default options of `mark_duplicates` will be used.
        samtools_filter_reads_options : Dict[str, str]
            A dictionary of options to pass to the `samtools filter reads` command. If not
            provided, the following defaults will be used:
            -bF 1804, -f 2, -q 20, -e '[NM] <= 2'.
        macs2_callpeak_options : Dict[str, str]
            A dictionary of options to pass to the `macs2 callpeak` command. If not provided,
            the default options of `run_macs2` will be used.

        Returns
        -------
        str
            A string containing the concatenated commands for the entire pipeline, separated
            by newline characters.

        Notes
        -----
        This function relies on other methods (`run_fastp`, `run_bowtie2`, `mark_duplicates`,
        `filter_reads`, `run_macs2`) to generate individual commands. Ensure these methods
        are implemented and functional before using this pipeline.
        """
        if fastp_options is None:
            fastp_options = {}

        if bowtie2_options is None:
            bowtie2_options = {
                '--very-sensitive': '',
                '--no-mixed': '',
                '--no-discordant': '',
                '-k': '10',
                '-tq': '',
                '-X': '1000',
                '-L': '25'
            }

        if gatk_markduplicates_options is None:
            gatk_markduplicates_options = {}

        if samtools_filter_reads_options is None:
            samtools_filter_reads_options = {
                '-bF': '1804',
                '-f': '2',
                '-q': '20',
                '-e': "'[NM] <= 2'"
            }

        if macs2_callpeak_options is None:
            macs2_callpeak_options = {}

        cmds = (
            f'{self.run_fastp(**fastp_options)}\n\n'
            f'{self.run_bowtie2(**bowtie2_options)}\n\n'
            f'{self.mark_duplicates(**gatk_markduplicates_options)}\n\n'
            f'{self.filter_reads(**samtools_filter_reads_options)}\n\n'
            f'{self.run_macs2(**macs2_callpeak_options)}'
        )

        return cmds
