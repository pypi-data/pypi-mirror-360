#!/usr/bin/env python
"""
File: fastq.py
Description: Instantiate a FASTA file object.
CreateDate: 2024/7/25
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from io import TextIOWrapper
from typing import Union, Any, Generator, Tuple
from os.path import abspath
import gzip
from random import randint, choice, choices
from re import sub
from tqdm import tqdm
from click import echo, open_file
from pybioinformatic.sequence import Sequence, Reads
from pybioinformatic.util import FuncDict
from pybioinformatic.task_manager import TaskManager


def _sample(fastq_file_path: str, flags):
    out_file = sub(
        pattern='.fastq$',
        repl='',
        string=sub(
            pattern='.fq$',
            repl='',
            string=sub(
                pattern='.gz$',
                repl='',
                string=fastq_file_path
            )
        )
    ) + f'_sample{len(flags)}.fastq.gz'
    i = 0
    with Fastq(fastq_file_path) as fastq_obj, gzip.open(out_file, 'wb') as o:
        for record in fastq_obj.parse():
            if i > max(flags):
                break
            if i in flags:
                o.write(str(record).encode('utf-8'))
            i += 1


class Fastq:
    def __seek_zero(self):
        try:
            self.__open.seek(0)
        except AttributeError:
            pass

    def __check_integrity(self):
        if self.line_num % 4 != 0:
            echo(f'\033[31mError: Truncated fastq file "{self.name}".\033[0m', err=True)
            exit()
        else:
            self.num_reads = int(self.line_num / 4)

    def __init__(self, path: Union[str, TextIOWrapper]):
        """
        Initialize name, __open, num_line and num_reads attributions.
        """
        if isinstance(path, str):
            self.name = abspath(path)
            if path.endswith('gz'):
                self.__open = gzip.GzipFile(path)
            else:
                self.__open = open(path)
            self.line_num = sum(1 for _ in self.__open)
            self.__open.seek(0)
            self.__check_integrity()
        elif isinstance(path, TextIOWrapper):
            self.name = abspath(path.name)
            if path.name == '<stdin>':
                self.__open = open_file('-').readlines()
                self.line_num = len(self.__open)
                self.__check_integrity()
            else:
                if path.name.endswith('gz'):
                    self.__open = gzip.GzipFile(path.name)
                else:
                    self.__open = path
                self.line_num = sum(1 for _ in self.__open)
                self.__open.seek(0)
                self.__check_integrity()
        else:
            echo(f'\033[31mInvalid type: {type(path)}.\033[0m', err=True)
            exit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.__open.close()
        except AttributeError:
            pass

# Basic method==========================================================================================================
    def parse(self):
        while 1:
            record_id = self.__open.readline().strip()
            if not record_id:
                self.__seek_zero()
                break
            record_seq = self.__open.readline().strip()
            record_desc = self.__open.readline().strip()
            record_quality = self.__open.readline().strip()
            if self.name.endswith('gz'):
                record_id = str(record_id, 'utf8')
                record_seq = str(record_seq, 'utf8')
                record_desc = str(record_desc, 'utf8')
                record_quality = str(record_quality, 'utf8')
            yield Reads(seq_id=record_id, sequence=record_seq, desc=record_desc, quality=record_quality)

# K-mer method==========================================================================================================
    def get_k_mer(self, k: int = 21):
        """Get K-mer sequence for each sequence from fastq file."""
        for nucl in self.parse():
            yield from nucl.k_mer(k)

    @staticmethod
    def _stat_k_mer(sequence_obj: Sequence, k: int):
        return sequence_obj.count_k_mer(k)

    def stat_k_mer(self, k: int = 21, num_processing: int = 4):
        """Count the frequency of each k-mer."""
        with tqdm(total=self.num_reads) as pbar:
            params = ((nucl, k) for nucl in self.parse())
            tkm = TaskManager(num_processing=num_processing, params=params)
            rets = tkm.parallel_run_func(func=self._stat_k_mer, call_back_func=lambda _: pbar.update())
            k_mer_count = FuncDict()
            for ret in rets:
                k_mer_count + ret.get()
            k_mer_count.sort_by_keys()
            return k_mer_count

# Other method==========================================================================================================
    @staticmethod
    def generate_random_fastq(
        num_records: int,
        record_length: Union[int, list, tuple] = 150,
        base_bias: Union[float, list] = 1.0
    ) -> Generator[str, Any, None]:
        """
        Generate a random FASTQ file.
        :param num_records: Number of records
        :param record_length: Length or length range of records
        :param base_bias: Base bias
        """
        seed = list('abcdefghijklmnopqrstuvwxyz0123456789'.upper())
        q_value = '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
        if isinstance(base_bias, float):
            base_bias = [base_bias for _ in range(5)]
        for _ in range(num_records):
            record_id = '@' + ''.join([choice(seed) for _ in range(10)])
            length = randint(min(record_length), max(record_length)) \
                if isinstance(record_length, (list, tuple)) else record_length
            record_seq = ''.join(choices(population="AGCTN", weights=base_bias, k=length))
            Q_value = ''.join(choices(population=q_value, k=length))
            yield f'{record_id}\n{record_seq}\n+\n{Q_value}'

    def sample(self, num_reads: int, other = None):
        rand_int_list = set(choices(range(self.num_reads), k=num_reads))
        while len(rand_int_list) < num_reads:
            rand_int_list.add(randint(0, self.num_reads))
        params = [(self.name, rand_int_list)]
        if other:
            params.append((other.name, rand_int_list))
        tkm = TaskManager(params=params, num_processing=2)
        tkm.parallel_run_func(func=_sample)
