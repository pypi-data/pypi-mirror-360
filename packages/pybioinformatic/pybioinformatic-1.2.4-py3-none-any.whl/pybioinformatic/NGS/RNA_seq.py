"""
File: RNA_seq.py
Description: RNA-seq analysis pipeline module.
CreateDate: 2024/7/24
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from io import TextIOWrapper
from typing import Literal, Union, Dict
from os import makedirs
from os.path import abspath, exists
from shutil import which
from tqdm import tqdm
from scipy.stats import pearsonr
from statsmodels.stats.multitest import multipletests
from pandas import DataFrame, Series, concat
from pybioinformatic.gtf import Gtf
from pybioinformatic.task_manager import TaskManager
from pybioinformatic.NGS import NGSAnalyser
from pybioinformatic.util import FuncDict


class RNASeqAnalyser(NGSAnalyser):
    def __init__(
            self,
            read1: str,
            read2: str,
            ref_genome: str,
            output_path: str,
            ref_gff: str = None,
            num_threads: int = 10,
            sample_name: str = None,
            exe_path_dict: Dict[str, str] = None
    ):
        self._exe_set.update({'stringtie'})
        super().__init__(read1, read2, ref_genome, output_path, num_threads, sample_name, exe_path_dict)
        self.ref_gff = abspath(ref_gff) if ref_gff else ref_gff
        self.assembly_path = f'{self.output_path}/03.assembly/{self.sample_name}'
        self.stringtie_gtf = f'{self.assembly_path}/{self.sample_name}.st.gtf'

    def run_stringtie(
            self,
            sorted_bam: str = None,
            out_gtf: str = None,
            **other_options
    ):
        stringtie = which(self.exe_path_dict['stringtie'])
        sorted_bam = abspath(sorted_bam) if sorted_bam else self.hisat2_raw_bam
        out_gtf = abspath(out_gtf) if out_gtf else self.stringtie_gtf
        makedirs(self.assembly_path, exist_ok=True)
        cmd = (
            f'{stringtie} '
            f'-p {self.num_threads} '
            f'-l {self.sample_name} '
            f'-o {out_gtf} '
            f'{sorted_bam}'
        )
        return self.other_options(cmd, other_options) if other_options else cmd

    def ssRNA_seq_pipeline(self):
        fastp_options = {
            '-j': f'{self.qc_path}/{self.sample_name}.fastp.json',
            '-h': f'{self.qc_path}/{self.sample_name}.fastp.html'
        }
        hisat2_options = {'--rna-strandness': 'RF'}
        stringtie_options = {'--rf': '', '-G': self.ref_gff} if self.ref_gff else {'--rf': ''}
        cmds = (
            f"{self.run_fastp(**fastp_options)}\n\n"
            f'{self.run_hisat2(**hisat2_options)}\n\n'
            f'{self.run_stringtie(**stringtie_options)}'
        )
        return cmds


class LncRNAPredictor:
    _exe_set = {'CNCI.py', 'CPC2.py', 'PLEK', 'pfam_scan.pl', 'seqkit'}

    def __init__(
            self,
            nucl_fasta_file: str,
            output_path: str,
            num_thread: int = 10,
            module: Literal['ve', 'pl'] = 'pl',
            pep_fasta_file: str = None,
            PfamDatabase: str = None,
            exe_path_dict: Dict[str, str] = None
    ):
        if exe_path_dict is None:
            exe_path_dict = {}
        self.nucl = abspath(nucl_fasta_file)
        self.pep = abspath(pep_fasta_file) if pep_fasta_file else None
        self.PfamDatabase = abspath(PfamDatabase) if PfamDatabase else None
        self.output_path = abspath(output_path)
        self.num_thread = num_thread
        self.module = module
        self.exe_path_dict = FuncDict(
            {
                k: which(v)
                for k, v in exe_path_dict.items()
                if k in self._exe_set and which(v) is not None
            }
        )
        # output
        self.CNCI_out = f'{self.output_path}/CNCI/CNCI.index'
        self.CPC2_out = f'{self.output_path}/CPC2/CPC2.txt'
        self.PLEK_out = f'{self.output_path}/PLEK/PLEK.xls'
        self.PfamScan_out = f'{self.output_path}/PfamScan/pfamscan_out.txt'

    def run_CNCI(self):
        CNCI = which(self.exe_path_dict['CNCI.py'])
        cmd = f'{CNCI} -p {self.num_thread} -m {self.module} -f {self.nucl} -o {self.output_path}/CNCI'
        return cmd

    def run_CPC2(self):
        CPC2 = which(self.exe_path_dict['CPC2.py'])
        makedirs(f'{self.output_path}/CPC2', exist_ok=True)
        cmd = f'{CPC2} -i {self.nucl} --ORF TRUE -o {self.output_path}/CPC2/CPC2'
        return cmd

    def run_PLEK(self):
        PLEK = which(self.exe_path_dict['PLEK'])
        makedirs(f'{self.output_path}/PLEK', exist_ok=True)
        cmd = f'{PLEK} -thread {self.num_thread} -fasta {self.nucl} -out {self.PLEK_out}'
        return cmd

    def run_PfamScan(self):
        PfamScan = which(self.exe_path_dict['pfam_scan.pl'])
        makedirs(f'{self.output_path}/PfamScan', exist_ok=True)
        cmd = (f'{PfamScan} '
               f'-fasta {self.pep} '
               f'-dir {self.PfamDatabase} '
               f'-outfile {self.PfamScan_out}')
        return cmd

    def merge_results(self,
                      CNCI_results: str = None,
                      CPC2_results: str = None,
                      PLEK_results: str = None,
                      PfamScan_results: str = None):
        CNCI_results = abspath(CNCI_results) if CNCI_results else self.CNCI_out
        CPC2_results = abspath(CPC2_results) if CPC2_results else self.CPC2_out
        PLEK_results = abspath(PLEK_results) if PLEK_results else self.PLEK_out
        PfamScan_results = abspath(PfamScan_results) if PfamScan_results else self.PfamScan_out

        seqkit = which(self.exe_path_dict['seqkit'])
        CNCI_results = r'''awk -F'\t' '{if($2 == "noncoding"){print $1}}' %s | awk -F' ' '{print $1}' ''' % CNCI_results
        CPC2_results = r'''awk -F'\t' '{if($9 == "noncoding"){print $1}}' %s''' % CPC2_results
        PLEK_results = r'''awk -F'\t' '{if($1 == "Non-coding"){print $3}}' %s | sed 's/>//;s/ gene.*//' ''' % PLEK_results
        awk1 = r'''awk -F' ' '{if($1 == 3){print $2}}' '''
        awk2 = r'''awk -F' ' '{print $1}' %s''' % PfamScan_results
        seqkit_cmd1 = f'{seqkit} grep -f - {self.nucl}'
        seqkit_cmd2 = f'{seqkit} seq -m 200 -'
        cmd = (f'cat <({CNCI_results}) <({CPC2_results}) <({PLEK_results}) | sort | uniq -c | {awk1} | '
               f'grep -vFwf <({awk2}) - | {seqkit_cmd1} | {seqkit_cmd2} > {self.output_path}/lncRNA.fa')
        return cmd


class LncRNATargetPredictor:
    def __init__(self,
                 lncRNA_gtf_file: Union[str, TextIOWrapper] = None,
                 mRNA_gtf_file: Union[str, TextIOWrapper] = None,
                 distance: int = 100000,
                 lncRNA_exp_file: Union[str, TextIOWrapper] = None,
                 mRNA_exp_file: Union[str, TextIOWrapper] = None,
                 lncRNA_min_exp: float = 0.5,
                 mRNA_min_exp: float = 0.5,
                 r: float = 0.85,
                 FDR: float = 0.05,
                 q_value: float = 0.05,
                 num_processing: int = 1,
                 output_path: str = '.'):
        self.lncRNA_gtf = abspath(lncRNA_gtf_file)
        self.lncRNA_exp = abspath(lncRNA_exp_file)
        self.lncRNA_min_exp = lncRNA_min_exp
        self.mRNA_gtf = abspath(mRNA_gtf_file)
        self.mRNA_exp = abspath(mRNA_exp_file)
        self.mRNA_min_exp = mRNA_min_exp
        self.distance = distance
        self.r, self.FDR, self.q_value = r, FDR, q_value
        self.num_processing = num_processing
        self.output_path = abspath(output_path)

    @staticmethod
    def intersect(row: Series, mRNA: DataFrame, distance: int):
        lncRNA_chr = row['Chromosome']
        lncRNA_start, lncRNA_end = row['Start'], row['End']
        start = lncRNA_start - distance if lncRNA_start - distance > 0 else 1
        end = lncRNA_end + distance
        lncRNA_strand = row['Strand']
        candidate_mRNA = mRNA[
            (mRNA['Chromosome'] == lncRNA_chr) &
            (start <= mRNA['Start']) &
            (end >= mRNA['End'])
            ]
        candidate_mRNA['LncRNA_id'] = row.name
        candidate_mRNA['LncRNA_start'] = lncRNA_start
        candidate_mRNA['LncRNA_end'] = lncRNA_end
        candidate_mRNA['LncRNA_strand'] = lncRNA_strand
        return candidate_mRNA

    def co_location(self):
        with Gtf(self.lncRNA_gtf) as lncRNA_gtf, Gtf(self.mRNA_gtf) as mRNA_gtf:
            lncRNA_df = lncRNA_gtf.merge_by_transcript()
            mRNA_df = mRNA_gtf.merge_by_transcript()
            lncRNA_df.to_csv(f'{self.output_path}/lncRNA.bed', sep='\t')
            mRNA_df.to_csv(f'{self.output_path}/mRNA.bed', sep='\t')
            params = ((row[1], mRNA_df, self.distance) for row in lncRNA_df.iterrows())
            tkm = TaskManager(num_processing=self.num_processing, params=params)
            with tqdm(total=len(lncRNA_df), desc='Co-location predicting') as pbar:
                rets = tkm.parallel_run_func(func=self.intersect, call_back_func=lambda _: pbar.update())
            dfs = [ret.get() for ret in rets]
            lncRNA_mRNA_df = concat(dfs)
            lncRNA_mRNA_df.to_csv(f'{self.output_path}/co_loc.xls', sep='\t')

    @staticmethod
    def sub_process(x_name, x_data, y_name, y_data):
        r, p = pearsonr(x_data, y_data)
        return [x_name, y_name, r, p]

    def co_expression(self):
        lncRNA_exp_dict = {
            line.strip().split('\t')[0]: [float(i) for i in line.strip().split('\t')[1:]]
            for line in open(self.lncRNA_exp)
            if not line.startswith('Geneid') and line.strip() and
               all([float(i) >= self.lncRNA_min_exp for i in line.strip().split('\t')[1:]])
        }

        mRNA_exp_dict = {
            line.strip().split('\t')[0]: [float(i) for i in line.strip().split('\t')[1:]]
            for line in open(self.mRNA_exp)
            if not line.startswith('Geneid') and line.strip() and
               all([float(i) >= self.mRNA_min_exp for i in line.strip().split('\t')[1:]])
        }

        with tqdm(total=len(lncRNA_exp_dict) * len(mRNA_exp_dict), desc='Co-expression predicting') as pbar:
            params = ((k1, v1, k2, v2) for k1, v1 in lncRNA_exp_dict.items() for k2, v2 in mRNA_exp_dict.items())
            tkm = TaskManager(num_processing=self.num_processing, params=params)
            rets = tkm.parallel_run_func(func=self.sub_process, call_back_func=lambda _: pbar.update())

        data = [ret.get() for ret in rets]
        raw = DataFrame(data=data, columns=['lncRNA_id', 'mRNA_id', 'pcc', 'p_value'])
        raw.sort_values(by=['lncRNA_id', 'p_value'], inplace=True, ascending=[True, True])
        raw.to_csv(f'{self.output_path}/raw_co_exp.xls', sep='\t', index=False, float_format='%.12f', na_rep='NA')

        filter_df = raw[(raw['pcc'].abs() >= self.r) & (raw['p_value'] <= self.q_value)]
        filter_df['q_value'] = multipletests(pvals=filter_df['p_value'], alpha=self.FDR, method='fdr_bh')[1]
        filter_df = filter_df[filter_df['q_value'] <= self.q_value]
        filter_df.sort_values(by=['lncRNA_id', 'q_value'], inplace=True, ascending=[True, True])
        filter_df.to_csv(f'{self.output_path}/filter_co_exp.xls', sep='\t', index=False, float_format='%.12f', na_rep='NA')


class LncRNAClassification:
    def __init__(self, mRNA_gff_file: str, lncRNA_gtf_file: str, out_dir: str):
        self.mRNA_gff_file = abspath(mRNA_gff_file)
        self.mRNA_gtf_file = '.'.join(self.mRNA_gff_file.split('.')[:-1]) + '.gtf'
        self.lncRNA_gtf_file = abspath(lncRNA_gtf_file)
        out_dir = abspath(out_dir)
        makedirs(out_dir, exist_ok=True)
        self.gene_bed = f'{out_dir}/gene.bed'
        self.exon_bed = f'{out_dir}/exon.bed'
        self.intron_bed = f'{out_dir}/intron.bed'
        self.lncRNA_bed = f'{out_dir}/lncRNA.bed'
        self.sense = f'{out_dir}/sense.bed'
        self.antisense = f'{out_dir}/antisense.bed'
        self.intronic = f'{out_dir}/intronic.bed'
        self.intergenic = f'{out_dir}/intergenic.bed'

    def classification(self):
        bedtools = which('bedtools')
        gffread = which('gffread')
        gff2gtf = f'{gffread} {self.mRNA_gff_file} -T -o {self.mRNA_gtf_file}' if not exists(self.mRNA_gtf_file) else ''

        gene_bed = (r'''awk -F'\t' '{if($3 == "gene"){print $1,$4,$5,$9,$6,$7}}' OFS='\t' %s | sort -uV > %s''' %
                    (self.mRNA_gff_file, self.gene_bed))
        exon_bed = (r'''awk -F'\t' '{if($3 == "exon"){print $1,$4,$5,$9,$6,$7}}' OFS='\t' %s | sort -uV > %s''' %
                    (self.mRNA_gtf_file, self.exon_bed))
        intron_bed = f'{bedtools} subtract -a {self.gene_bed} -b {self.exon_bed} -s | sort -uV > {self.intron_bed}'
        lncRNA_bed = (r'''awk -F'\t' '{print $1,$4,$5,$9,$6,$7}' OFS='\t' %s | sort -uV > %s''' %
                      (self.lncRNA_gtf_file, self.lncRNA_bed))

        intronic = f'{bedtools} intersect -a {self.lncRNA_bed} -b {self.intron_bed} -s > {self.intronic}'

        sense = (
                r'''%s intersect -a <(awk '{if(match($0, /transcript_id "[a-zA-Z0-9]*.*[a-zA-Z0-9]*"/)) print substr($0, RSTART, RLENGTH)}' %s | sort -uV | grep -Fwvf - %s) -b %s -s > %s''' %
                (bedtools, self.intronic, self.lncRNA_bed, self.gene_bed, self.sense)
        )

        antisense = (
                r'''%s intersect -a <(cat %s %s | awk '{if(match($0, /transcript_id "[a-zA-Z0-9]*.*[a-zA-Z0-9]*"/)) print substr($0, RSTART, RLENGTH)}' | sort -uV | grep -Fwvf - %s) -b %s -S > %s''' %
                (bedtools, self.intronic, self.sense, self.lncRNA_bed, self.gene_bed, self.antisense)
        )

        intergenic = (
                r'''%s subtract -a <(cat %s %s %s | awk '{if(match($0, /transcript_id "[a-zA-Z0-9]*.*[a-zA-Z0-9]*"/)) print substr($0, RSTART, RLENGTH)}' | sort -uV | grep -Fwvf - %s) -b %s > %s''' %
                (bedtools, self.intronic, self.sense, self.antisense, self.lncRNA_bed, self.gene_bed, self.intergenic)
        )

        return '\n'.join([gff2gtf, gene_bed, exon_bed, intron_bed, lncRNA_bed, intronic, sense, antisense, intergenic])
