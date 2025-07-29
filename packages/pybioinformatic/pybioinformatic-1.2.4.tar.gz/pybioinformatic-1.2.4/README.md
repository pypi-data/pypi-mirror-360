# This is a bioinformatic python package.

## Install
```shell
pip install pybioinformatic --upgrade
```

## Issue
### ImportError: libffi.so.7: cannot open shared object file: No such file or directory
```shell
# First use the following command to verify that the file exists in that path.
ls /usr/lib/x86_64-linux-gnu/libffi.so.7

# If libffi.so.6 is present on your system but libffi.so.7 is missing, you can try creating a soft link to an existing libffi.so.6 file.
ln -s /usr/lib/x86_64-linux-gnu/libffi.so.6 /usr/lib/x86_64-linux-gnu/libffi.so.7

# You can also install libffi7 with sudo grant.
sudo apt-get install libffi7
```

## Usage example
### RNA secondary structure prediction.
```python
from pybioinformatic import Nucleotide

# Generate random nucleic acid sequence.
random_nucl = Nucleotide.random_nucl(name='demo', length=[100, 150], bias=1.0)

# Secondary structure prediction
ss, mfe = random_nucl.predict_secondary_structure('test/structure.ps')
print(ss, mfe, sep='\n')
```
```
>demo length=135
CAAAAAAAAACCATAAGCCGCCATGTCTCACATCGCAACCGGCTCAAGTAGAGTGCCCCTAATAATATGATCTTCGCTACAGAAGTTCCCCCCCCGCTGCCGGCTAGATGCGAACTCCACGCCTGGATGGCTCAG
...............((((((((.((......(((((.(.((((...((((.................((.((((......)))).))........)))).)))).).))))).......)).))).)))))...
-27.299999237060547
```
![image](test/structure.png)

### Connect MySQL
```python
from pybioinformatic import BioMySQL

with BioMySQL(
    mysql_host='192.168.1.110',
    mysql_port=3306,
    mysql_user='60533',
    mysql_password='NJFU',
    ssh_ip=None,
    ssh_port=None,
    ssh_user=None,
    ssh_password=None,
    remote_bind_ip=None,
    remote_bind_port=None,
    local_bind_ip=None,
    local_bind_port=None
) as connect:
    cur = connect.cursor()
    sql = 'use Ptrichocarpa;'
    cur.execute(sql)
    sql = 'select protein_id,sequence from protein where protein_id = "Potri.019G097720.1.p";'
    cur.execute(sql)
    for data in cur.fetchall():
        protein_id, sequence = data
        print(f'>{protein_id}\n{sequence}')
```
```
>Potri.019G097720.1.p
MESLQHLYLSKTGIKEIPSSFKHMISLITLKLDGTPIKELPLSIKDKVCLEYLTLHGTPIKALPELPPSLRFLTTHDCASLETVISIINISSLWFRRDFTNCFKLDQKPLVAAMHLKIQSGEETPHGTIQMVLLGSEIPEWFGDKGIGSSLTIQLPSNCHLLKGIAFCLVFLLPLPSQDMPCEVDDDSYVHVYFDCHVKSKNGESDGGDEIVFGSQERRALLYLLETCDSDHMFLHYELGLVNHLRKYSGNEVTFKFYHEVYNQGRKLGHEIRKPFKLKNCGVYLHFDENLPADTDLP*
```
