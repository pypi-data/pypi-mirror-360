"""
File: vcf.py
Description: Instantiate a VCF file object.
CreateDate: 2023/10/28
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Union, Any, Generator
from io import TextIOWrapper
from os.path import abspath
from gzip import GzipFile
from pandas import read_table


class VCF:
    def __init__(self, path: Union[str, TextIOWrapper]):
        self.name = abspath(path) if isinstance(path, str) else abspath(path.name)
        if isinstance(path, str):
            if path.endswith('gz'):
                self.__open = GzipFile(path)
            else:
                self.__open = open(path)
        else:
            if path.name.endswith('gz'):
                self.__open = GzipFile(path.name)
            else:
                self.__open = path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.__open.close()
        except AttributeError:
            pass

    def __seek_zero(self):
        try:
            self.__open.seek(0)
        except AttributeError:
            pass

# Basic method==========================================================================================================
    def get_header(self):
        for line in self.__open:
            if not isinstance(line, str):
                line = str(line, 'utf8')
            if not line.startswith('##') and line.startswith('#'):
                header = line.strip().replace('#', '').split('\t')
                self.__seek_zero()
                return header

    def to_dataframe(self):
        df = read_table(
            self.__open,
            comment='#',
            header=None,
            names=self.get_header()
        )
        return df

# Format conversion method==============================================================================================
    def to_genotype(self) -> Generator[str, Any, None]:
        """Convert VCF to GenoType."""
        for line in self.__open:
            if not isinstance(line, str):
                line = str(line, 'utf8')
            if not line.startswith('#') and line.strip():
                split = line.strip().split('\t')
                chr_name, position, ID, ref, alts, = split[:5]
                alts = alts.split(',')
                alts.insert(0, ref)
                ID = f'{chr_name}_{position}'
                samples = split[9:]
                samples_gt = []
                for sample in samples:
                    gt = sample.split(':')[0]
                    if gt == './.' or gt == '.|.' or gt == '.':
                        gt = 'NA'
                    else:
                        alleles_index = [int(i) for i in gt.replace('|', '/').split('/')]
                        alt1, alt2 = alts[alleles_index[0]], alts[alleles_index[1]]
                        if len(ref) == len(alt1) == len(alt2) == 1:
                            gt = alt1 + alt2
                        elif len(ref) == len(alt1) == len(alt2) > 1:
                            if ref == alt1 == alt2:
                                gt = '-'
                            else:
                                gt = alt1[0] + alt2[0]
                        elif len(alt1) == len(alt2) > 1:
                            gt = alt1[0] + alt2[0]
                        else:
                            if ref == alt1:
                                alt1 = '-'
                            elif len(ref) == len(alt1):
                                alt1 = alt1[0]
                            elif alt1 != '*':
                                alt1 = f"ins{alt1.replace(ref, '', 1)}" \
                                    if len(ref) < len(alt1) else \
                                    f"del{ref.replace(alt1, '', 1)}"
                            if ref == alt2:
                                alt2 = '-'
                            elif len(ref) == len(alt2):
                                alt2 = alt2[0]
                            elif alt2 != '*':
                                alt2 = f"ins{alt2.replace(ref, '', 1)}" \
                                    if len(ref) < len(alt2) else \
                                    f"del{ref.replace(alt2, '', 1)}"
                            if alt1 == alt2 and ('del' in alt1 or 'ins' in alt1):
                                gt = alt1
                            else:
                                gt = f'{alt1}/{alt2}' if alt1 != alt2 else '-'
                    samples_gt.append(gt)
                samples_gt = '\t'.join(samples_gt)
                yield f'{ID}\t{chr_name}\t{position}\t{ref}\t{samples_gt}'
            elif not line.startswith('##') and line.startswith('#'):
                split = line.strip().split('\t')
                header = 'ID\tChrom\tPosition\tRef\t'
                samples = '\t'.join(split[9:])
                yield header + samples
