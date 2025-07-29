"""
File: sequence.py
Description: Instantiate a sequence object (including nucleotide and amino acid sequences).
CreateDate: 2021/11/26
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Tuple, Union, Generator, Any
from collections import Counter
from re import findall, finditer, sub
from natsort import natsort_key
from ViennaRNA import fold, circfold, RNA
from click import echo


class Sequence:
    def __init__(self, seq_id: str, sequence: str, strip: bool = True):
        self.id = sub(r'^[>@]', '', seq_id)
        if strip:
            self.seq = sequence.replace('\n', '')
        else:
            self.seq = sequence
        if '*' in sequence:
            self.len = len(sequence.replace('\n', '').replace('*', ''))
        else:
            self.len = len(sequence.replace('\n', ''))

    def __str__(self) -> str:
        if 'length' not in self.id:
            return f'>{self.id} length={len(self)}\n{self.seq.strip()}'
        else:
            self.id = sub(r'length=\d+', f'length={len(self)}', self.id)
            return f'>{self.id}\n{self.seq.strip()}'

    def __contains__(self, item) -> bool:
        """
        Define when implement "Sequence_obj1 in Sequence_obj2",
        if Sequence_obj1.seq in Sequence_obj2.seq, return True,
        otherwise return False.
        """
        return True if item.seq.replace('\n', '') in self.seq.replace('\n', '') else False

    def __ne__(self, other) -> bool:
        """
        Define when implement "Sequence_obj1 != Sequence_obj2",
        if Sequence_obj1.seq != Sequence_obj2.seq, return True,
        otherwise return False.
        """
        return True if self.seq.replace('\n', '') != other.seq.replace('\n', '') else False

    def __eq__(self, other) -> bool:
        """
        Define when implement "Sequence_obj1 == Sequence_obj2",
        if Sequence_obj1.seq == Sequence_obj2.seq, return True,
        otherwise return False.
        """
        return True if self.seq.replace('\n', '') == other.seq.replace('\n', '') else False

    def __hash__(self):
        return hash(self.seq)

    def __lt__(self, other) -> bool:
        """
        Define when implement "Sequence_obj1 < Sequence_obj2",
        if len(Sequence_obj1.seq) < len(Sequence_obj2.seq),
        return True, otherwise return False.
        """
        return True if len(self) < len(other) else False

    def __le__(self, other) -> bool:
        """
        Define when implement "Sequence_obj <= Sequence_obj2",
        if len(Sequence_obj1.seq) <= len(Sequence_obj2.seq),
        return True, otherwise return False.
        """
        return True if len(self) <= len(other) else False

    def __gt__(self, other) -> bool:
        """
        Define when implement "Sequence_obj > Sequence_obj2",
        if len(Sequence_obj1.seq) > len(Sequence_obj2.seq),
        return True, otherwise return False.
        """
        return True if len(self) > len(other) else False

    def __ge__(self, other) -> bool:
        """
        Define when implement "Sequence_obj >= Sequence_obj2",
        if len(Sequence_obj1.seq) >= len(Sequence_obj2.seq),
        return True, otherwise return False.
        """
        return True if len(self) >= len(other) else False

    def __iter__(self) -> Generator[str, None, None]:
        """ Implement "iter(self.seq)". """
        yield from self.seq

    def __getitem__(self, item):
        """
        Define when implement "Sequence_obj[int:int:int].seq",
        it is equal to "Sequence_obj.seq[int:int:int]",
        but the return value type is same as raw object.
        """
        if item.start is None or item.start == 0:
            start = 1
        else:
            start = item.start + 1
        if item.stop is None or item.stop > self.len:
            stop = self.len
        else:
            stop = item.stop
        if item.step is None:
            step = 1
        else:
            step = item.step
        if isinstance(self, Reads):
            return Reads(seq_id=f"{self.id} slice({start}:{stop}:{step})",
                         sequence=self.seq.replace('\n', '')[item],
                         desc=self.desc,
                         quality=self.quality[item])
        elif isinstance(self, Nucleotide):
            return Nucleotide(f"{self.id} slice({start}:{stop}:{step})", self.seq.replace('\n', '')[item])
        elif isinstance(self, Protein):
            return Protein(f"{self.id} slice({start}:{stop}:{step})", self.seq.replace('\n', '')[item])
        else:
            return Sequence(f"{self.id} slice({start}:{stop}:{step})", self.seq.replace('\n', '')[item])

    def k_mer(self, k: int):
        """Get K-mer sequence."""
        for i in range(0, len(self) - k + 1):
            yield self[i:i+k]

    def count_k_mer(self, k: int):
        """Count k-mer frequency."""
        k_mer_list = [obj.seq for obj in self.k_mer(k)]
        k_mer_count = Counter(k_mer_list)
        return k_mer_count

    def __len__(self) -> int:
        return len(self.seq.replace('*', '').replace('\n', ''))

    def get_seq_len_info(self) -> str:
        """Get sequence length information."""
        return f'{self.id}\t{self.len}'

    def locate_gap(self) -> Generator[str, None, None]:
        for match in finditer(r'N+', self.seq.replace('\n', '').upper()):
            if match:
                yield f'{self.id}\t{match.start() + 1}\t{match.end()}'

    def find_motif(self, motif: str, only_forward: bool = False) -> str:
        """Find the motif in the sequence."""
        ret = []
        raw_seq = self.seq.replace('\n', '')
        matched = findall(rf'{motif}', raw_seq)
        matched = list(set(matched))
        if matched:
            for match in matched:
                if raw_seq == match:
                    ret.append(f"{self.id}\t1\t{len(raw_seq)}\t+\t{motif}\t{match}")
                else:
                    split = raw_seq.split(match)
                    end = 0
                    for i in split:
                        if i != split[-1]:
                            start = end + len(i) + 1
                            end = start + len(match) - 1
                            ret.append(f"{self.id}\t{start}\t{end}\t+\t{motif}\t{match}")
        if only_forward:
            ret.sort(key=natsort_key)
            return '\n'.join(ret) if ret else f'{self.id} not found motif.'
        else:
            # If sequence is nucleotide, scan motif of reverse complementary strand.
            # If sequence is peptide chain, scan motif of reverse strand.
            try:
                seq = ''
                # Sequence is peptide chain
                if set(self.seq.upper()) - {'A', 'G', 'C', 'T', 'U', 'N'}:
                    seq = raw_seq
                # Sequence is nucleotide
                elif 'T' in self.seq or 't' in self.seq:
                    for n in raw_seq:
                        seq += Nucleotide.dna_complementary_dict[n]
                else:
                    for n in raw_seq:
                        seq += Nucleotide.rna_complementary_dict[n]
                seq = seq[::-1]
                matched = findall(rf'{motif}', seq)
                matched = list(set(matched))
                if matched:
                    for match in matched:
                        if seq == match:
                            ret.append(f"{self.id}\t1\t{len(seq)}\t-\t{motif}\t{match}")
                        else:
                            split = seq.split(match)
                            end = 0
                            for i in split:
                                if i != split[-1]:
                                    start = end + len(i) + 1
                                    end = start + len(match) - 1
                                    e = len(seq) - start + 1
                                    s = len(seq) - end + 1
                                    ret.append(f"{self.id}\t{s}\t{e}\t-\t{motif}\t{match}")
                    ret.sort(key=natsort_key)
            except AttributeError:
                pass
            return '\n'.join(ret) if ret else f'{self.id} not found motif.'

    def display_set(self, n: int = 60):
        raw_seq = self.seq.replace('\n', '')
        seq: list = findall(r'\w{1,%s}' % n, raw_seq)
        if '*' in raw_seq:
            if len(seq[-1]) == n:
                seq.append('*')
            else:
                seq[-1] = seq[-1] + '*'
        if isinstance(self, Nucleotide):
            return Nucleotide(self.id, '\n'.join(seq) + '\n', False)
        elif isinstance(self, Nucleotide):
            return Protein(self.id, '\n'.join(seq) + '\n', False)


class Nucleotide(Sequence):
    dna_complementary_dict = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N',
                              'a': 't', 't': 'a', 'g': 'c', 'c': 'g', 'n': 'n'}

    rna_complementary_dict = {'A': 'U', 'U': 'A', 'G': 'C', 'C': 'G', 'N': 'N',
                              'a': 'u', 'u': 'a', 'g': 'c', 'c': 'g', 'n': 'n'}

    codon_table = {'UUU': 'F', 'UUC': 'F', 'UUA': 'L', 'UUG': 'L',
                   'UCU': 'S', 'UCC': 'S', 'UCA': 'S', 'UCG': 'S',
                   'UAU': 'Y', 'UAC': 'Y', 'UAA': '*', 'UAG': '*',
                   'UGU': 'C', 'UGC': 'C', 'UGA': '*', 'UGG': 'W',
                   'CUU': 'L', 'CUC': 'L', 'CUA': 'L', 'CUG': 'L',
                   'CCU': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
                   'CAU': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
                   'CGU': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
                   'AUU': 'I', 'AUC': 'I', 'AUA': 'I', 'AUG': 'M',
                   'ACU': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
                   'AAU': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
                   'AGU': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
                   'GUU': 'V', 'GUC': 'V', 'GUA': 'V', 'GUG': 'V',
                   'GCU': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
                   'GAU': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
                   'GGU': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'}

    def __add__(self, other):
        """
        Define when implement "Nucleotide_obj1 + Nucleotide_obj2",
        it is equal to "Nucleotide_obj1.seq + Nucleotide_obj2.seq",
        but no value is returned, just the seq and len attributes of Nucleotide_obj1 are changed.
        """
        self.seq = self.seq + other.seq
        self.len = len(self)

    def __neg__(self):
        """
        Define when implement "-Nucleotide_obj", it is equal to "Nucleotide_obj.get_reverse_complementary_seq()".
        """
        return self.get_reverse_complementary_seq()

    @staticmethod
    def random_nucl(name: str = None, length: Union[int, list, tuple] = None, bias: Union[float, list, tuple] = 1.0):
        """
        Generate a random nucleotide sequence.
        :param name: Name of random nucleotide sequence. {type: str}
        :param length: Length of random nucleotide sequence. {type: int, list, or tuple; default: (100, 1000)}
        :param bias: Base preference. {type: float, 4-list, or 4-tuple; default: 1}
        :return: Nucleotide class instance.
        """
        import random
        if name is None:
            seed = list('abcdefghijklmnopqrstuvwxyz0123456789'.upper())
            name = ''.join([random.choice(seed) for _ in range(10)])
        if length is None:
            length = random.randint(100, 1000)
        elif isinstance(length, (list, tuple)):
            length = random.randint(length[0], length[1])
        if isinstance(bias, float):
            bias = [bias for _ in range(4)]
        random_nucl_seq = random.choices(population=list('AGCT'), weights=bias, k=length)
        return Nucleotide(name, ''.join(random_nucl_seq))

    def get_reverse_complementary_seq(self):
        """Get reverse complementary sequence of DNA or RNA."""
        seq = ''
        if 'T' in self.seq or 't' in self.seq:
            for n in self.seq.replace('\n', ''):
                seq += self.dna_complementary_dict[n]
        else:
            for n in self.seq.replace('\n', ''):
                seq += self.rna_complementary_dict[n]
        return Nucleotide(f"{self.id} reverse_complementary_chain", seq[::-1])

    def base_count(self) -> Union[Tuple[float, float, float, float, float, str], None]:
        """Get the percentage content of four bases."""
        A = self.seq.upper().count('A') / len(self) * 100
        G = self.seq.upper().count('G') / len(self) * 100
        C = self.seq.upper().count('C') / len(self) * 100
        T = self.seq.upper().count('T') / len(self) * 100
        U = self.seq.upper().count('U') / len(self) * 100
        N = self.seq.upper().count('N') / len(self) * 100
        a = '%.2f%s' % (A, '%')
        g = '%.2f%s' % (G, '%')
        c = '%.2f%s' % (C, '%')
        t = '%.2f%s' % (T, '%')
        u = '%.2f%s' % (U, '%')
        n = '%.2f%s' % (N, '%')
        if 'U' in self.seq.upper() and 'T' not in self.seq.upper():
            summary = f"Base content statistics of {self.id}\nA: {a}\nG: {g}\nC: {c}\nU: {u}\nN: {n}"
            return A, G, C, U, N, summary
        elif 'T' in self.seq.upper() and 'U' not in self.seq.upper():
            summary = f"Base content statistics of {self.id}\nA: {a}\nG: {g}\nC: {c}\nT: {t}\nN: {n}"
            return A, G, C, T, N, summary
        else:
            echo('\033[31mError: Unknown nucleotide sequence, both "U" and "T" in sequence.\033[0m', err=True)

    def find_SSR(self) -> str:
        """Find the simple sequence repeat (SSR) in the DNA sequence."""
        ret = []
        raw_seq = self.seq.replace('\n', '').replace('U', 'T')
        pattern = r'((\w+)\2\2+)'
        matched = findall(pattern, raw_seq)
        matched = list(set(matched))
        if matched:
            for match_tuple in matched:
                for match in match_tuple:
                    if len(match) >= 6:
                        try:
                            ssr_unit = max(findall(r'(\w+)\1{2}', match))
                            if len(set([nucl for nucl in ssr_unit])) == 1:
                                ssr_unit = list(set([nucl for nucl in ssr_unit]))[0]
                        except ValueError:
                            pass
                        else:
                            count = match.count(ssr_unit)
                            split = raw_seq.split(match)
                            end = 0
                            for i in split:
                                if i != split[-1]:
                                    start = end + len(i) + 1
                                    end = start + len(match) - 1
                                    ret.append(f"{self.id}\t{start}\t{end}\t({ssr_unit}){count}\t{match}")
                                ret.sort(key=lambda item: (int(item.split('\t')[1]), int(item.split('\t')[2])))
            return '\n'.join(ret) if ret else f'{self.id} not found SSR.'
        else:
            return f'{self.id} not found SSR.'

    def translation(self, complete: bool = True):
        """Translate nucleotide sequence to peptide chain."""
        peptide_chain = []
        append = peptide_chain.append
        for i in range(0, len(self), 3):
            codon = self.seq.upper().replace('T', 'U').replace('\n', '')[i:i + 3]
            try:
                append(self.codon_table[codon])
            except KeyError:
                append('-')
        peptide_chain = ''.join(peptide_chain)
        if complete:
            try:
                peptide_chain = (str(max(findall(r'M[A-Z]+\*', peptide_chain), key=len)))
                return Protein(f"{self.id} peptide_chain", peptide_chain)
            except ValueError:
                return Protein(f"{self.id} peptide_chain", '')
        else:
            peptide_chain = str(max(findall(r'M?[A-Z]+\*?', peptide_chain), key=len))
            return Protein(f"{self.id} peptide_chain", peptide_chain)

    def ORF_prediction(self, min_len: int = 1, complete: bool = True, only_plus: bool = False):
        """
        ORF prediction.
        :param min_len: minimal ORF length (type=int) {default=1}
        :param complete: whether consider ORF integrity (type=bool) {default=True}
        :param only_plus: whether only consider plus chain (type=bool) {default=False}
        :return: the longest ORF (type=Protein)
        """
        plus1 = self.translation(complete)
        plus2 = self[1:].translation(complete)
        plus3 = self[2:].translation(complete)
        prot_obj_list = [plus1, plus2, plus3]
        if set(self.seq.upper()) - {'A', 'G', 'C', 'T'}:
            msg = f'\033[33mWaring: "{self.id}" has degenerate bases, the peptide chain translation will stop at the degenerate base.\033[0m'
            echo(msg, err=True)
        if not only_plus:
            minus1 = (-self).translation(complete)
            minus2 = (-self)[1:].translation(complete)
            minus3 = (-self)[2:].translation(complete)
            prot_obj_list.extend([minus1, minus2, minus3])
        try:
            longest_ORF = max(prot_obj_list, key=len)
            if len(longest_ORF) >= min_len:
                longest_ORF.id = f'{self.id} ORF_prediction'
                return longest_ORF
            else:
                return f"{self.id} not found ORF."
        except ValueError:
            return f"{self.id} not found ORF."

    def circular_translation(self) -> Generator[tuple, Any, None]:
        """Translate a nucleotide sequence circularly."""
        for i in range(len(self)):
            cds = pep = ''
            j = i
            while True:
                if j + 3 <= len(self):
                    codon = self.seq[j:j + 3].upper()
                    if cds:
                        cds += codon
                        pep += self.codon_table[codon.replace('T', 'U')]
                        if self.codon_table[codon.replace('T', 'U')] == '*':
                            j += 3
                            break
                    else:
                        if codon == 'ATG':
                            cds += codon
                            pep += self.codon_table[codon.replace('T', 'U')]
                        else:
                            break
                else:
                    if j < len(self):
                        n = len(self) - j
                        codon = self.seq[-n:].upper() + self.seq[:3 - n].upper()
                        if cds:
                            cds += codon
                            pep += self.codon_table[codon.replace('T', 'U')]
                        else:
                            if codon == 'ATG':
                                cds += codon
                                pep += self.codon_table[codon.replace('T', 'U')]
                            else:
                                break
                        if self.codon_table[codon.replace('T', 'U')] == '*':
                            j += 3
                            break
                    else:
                        if (j - i) == len(self):
                            break
                        else:
                            if len(self) - j % len(self) < 3:
                                n = len(self) - j % len(self)
                                codon = self.seq[-n:].upper() + self.seq[:3 - n].upper()
                            else:
                                codon = self.seq[j % len(self):j % len(self) + 3].upper()
                            cds += codon
                            pep += self.codon_table[codon.replace('T', 'U')]
                            if self.codon_table[codon.replace('T', 'U')] == '*':
                                j += 3
                                break
                j += 3
            if cds and pep.endswith('*'):
                if j > len(self):
                    cds = Nucleotide(
                        f'{self.id} circular_translation_cds start={i + 1} end={j % len(self)} circular={j // len(self)}',
                        cds)
                    pep = Protein(
                        f'{self.id} circular_translation_pep start={i + 1} end={j % len(self)} circular={j // len(self)}',
                        pep)
                else:
                    cds = Nucleotide(f'{self.id} circular_translation_cds start={i + 1} end={j} circular=0', cds)
                    pep = Protein(
                        f'{self.id} circular_translation_pep start={i + 1} end={j} circular=0', pep)
                yield cds, pep

    def predict_secondary_structure(self, ps_file: str, circular: bool = False):
        seq = self.seq.replace('\n', '')
        ss, mfe = circfold(seq) if circular else fold(seq)
        RNA.PS_rna_plot(seq, ss, ps_file)
        if self.seq.count('\n') > 1:
            l1 = self.seq.strip().split('\n')
            n = len(l1[0])
            l2 = findall(r'[(.)]{1,%s}' % n, ss)
            s = f'>{self.id}\n'
            for i in zip(l1, l2):
                s += f'{i[0]}\n{i[1]}\n'
            return s.strip(), mfe
        else:
            return f'{self}\n{ss}', mfe


class Protein(Sequence):
    @staticmethod
    def random_prot(name: str = None, length: Union[int, list, tuple] = None, complete: bool = True):
        """
        Generate a random protein sequence.
        :param name: Name of random protein sequence. {type: str}
        :param length: Length of random protein sequence. {type: int, list or tuple; default: (100, 150)}
        :param complete: Whether random protein sequence is completed. {type: bool; default: True}
        :return: Protein class
        """
        import random
        if name is None:
            seed = list('abcdefghijklmnopqrstuvwxyz0123456789'.upper())
            name = ''.join([random.choice(seed) for _ in range(10)])
        if length is None:
            length = random.randint(100, 150)
        elif isinstance(length, (list, tuple)):
            length = random.randint(length[0], length[1])
        if complete:
            random_prot_seq = 'M' + ''.join([random.choice(list('HYRKCVQIGFTSWPMEADLN')) for _ in range(length - 1)]) + '*'
        else:
            random_prot_seq = ''.join([random.choice(list('HYRKCVQIGFTSWPMEADLN')) for _ in range(length)])
        return Protein(name, random_prot_seq)


class Reads(Nucleotide):
    def __init__(self, seq_id: str, sequence: str, desc: str, quality: str):
        super(Reads, self).__init__(seq_id, sequence)
        self.desc = desc
        self.quality = quality
        quality_dict = {}
        quality_str = '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
        for i in range(len(quality_str)):
            quality_dict[quality_str[i]] = i
        self.__quality_dict = quality_dict

    def __str__(self) -> str:
        if 'length' not in self.id:
            return f'@{self.id} length={len(self)}\n{self.seq.strip()}\n{self.desc}\n{self.quality}'
        else:
            self.id = sub(r'length=\d+', f'length={len(self)}', self.id)
            return f'@{self.id}\n{self.seq.strip()}\n{self.desc}\n{self.quality}'

    def get_quality(self) -> Tuple[int, ...]:
        t = tuple(self.__quality_dict[quality] for quality in self.quality)
        return t

    def filter_N(self, rate: float = 0.1, n: int = None) -> bool:
        if rate > 1:
            echo(f'\033[31mError: Invalid rate value "{rate}", it must be between 0 and 1.', err=True)
            exit()
        seq = self.seq.upper()
        if n is None:
            if seq.count('N') / self.len >= rate:
                return False
            else:
                return True
        else:
            if (seq.count('N') / self.len >= rate) or (seq.count('N') >= n):
                return False
            else:
                return True


# Test
if __name__ == '__main__':
    DNA = Nucleotide.random_nucl(length=1000)
    DNA = DNA.display_set()
    print(DNA)
    print(DNA.find_motif('(AAGCT){1,}'))
    print(DNA.base_count()[-1])
    print(DNA.ORF_prediction(complete=False).display_set())

    rev_com_DNA = DNA.get_reverse_complementary_seq().display_set(80)
    print(rev_com_DNA)
    print(rev_com_DNA.ORF_prediction().display_set())
