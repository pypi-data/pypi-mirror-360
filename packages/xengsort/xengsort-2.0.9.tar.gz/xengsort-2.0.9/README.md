# xengsort: Fast lightweight accurate xenograft sorting

This tool, xengsort, uses 3-way bucketed Cuckoo hashing to efficiently solve the xenograft sorting problem.

For a description of the method an evaluation on several datasets, please see our
[article in "Algorithms for Molecular Biology"](https://almob.biomedcentral.com/articles/10.1186/s13015-021-00181-w), or the initial [WABI 2020 publication](https://drops.dagstuhl.de/opus/volltexte/2020/12793/).
(There was also a [preprint on bioRxiv](https://www.biorxiv.org/content/10.1101/2020.05.14.095604v2).)
BibTeX entrys for citation can be found at the end of this README file.

In case of problems,

* please read the tutorial and/or usage guide in this file carefully,
* check the troubleshooting section below if your problem is solved there,
* and file an issue in the issue tracker if this does not help or you have discovered an error in the documentation.

See CHANGELOG.md for recent changes.
Thank you!


----


# Tutorial: Classification of human-captured mouse exomes

We here provide an example showing how to run xengsort on a human-captured mouse exome (part of one of the datasets described in the paper).
This tutorial uses the workflow management system `Snakemake` to run the example.
This is, however, not necessary to use `xengsort`. 
Please refer to the Usage Guide below to learn how to run `xengsort` on your own data manually.


Our software `xengsort` is provided as a Python package.
For efficiency, it uses just-in-time compilation provided by the [numba](http://numba.pydata.org/) package. 
We here use the package manager [conda](https://docs.conda.io/en/latest/) to manage Python packages and to use a separate environment for `xengsort`.


### Install the conda package manager (miniconda)
Go to https://docs.conda.io/en/latest/miniconda.html and download the Miniconda installer:
Choose Python 3.10 (or higher), your operating system, and preferably the 64 bit version.
Follow the instructions of the installer and append the conda executable to your PATH (even if the installer does not recommend it). 
You can let the installer do it, or do it manually by editing your ``.bashrc`` or similar file under Linux or MacOS, or by editing the environment variables under Windows.
To verify that the installation works, open a new terminal and execute
```
conda --version # ideally 22.9.xx or higher
python --version # ideally 3.10.xx or higher
```


## Installation via conda
`xengsort` is available via bioconda. To create a new environment including `xengsort`, run
```
conda create --name xengsort -c bioconda xengsort
```

If you want to install xengsort into an existing environment, activate it with
```
conda activate MYEVIRONMENT
```
and execute
```
conda install -c bioconda xengsort
```

## Manual installation via gitlab
### Obtain or update xengsort
Our software can also be obtained by cloning this public git repository:
```
git clone https://gitlab.com/genomeinformatics/xengsort.git
```

If you need to update xengsort later, you can do so by just executing
```
git pull
```
within the cloned directory tree.


### Create and activate a conda environment
To run our software, a [conda](https://docs.conda.io/en/latest/) environment with the required libraries needs to be created.
A list of needed libraries is provided in the ``environment.yml`` file in the cloned repository;
it can be used to create a new environment:

```
cd xengsort  # the directory of the cloned repository
conda env create
```
which will create an environment named ``xengsort`` with the required dependencies,
using the provided ``environment.yml`` file in the same directory.

A more explicit alternative is to run 
```
conda create --name xengsort -c conda-forge -c bioconda --file requirements.txt
```
which will do the same thing using the packages mentioned in `requirements.txt`.

**Note:** While xengsort works on Linux without problems, some of the required packages may currently not exist for Windows/Mac.

Setting up the environment may take some time, as conda searches and downloads packages.
After all dependencies are resolved, you activate the environment and install the package from the repository into this environment.
Make sure that you are in the root directory of the cloned repository (where this `README.md` file or the `CHANGELOG.md` file is) and run
```
conda activate xengsort  # activate environment
pip install -e .  # install xengsort package using pip
```


## Run the Snakemake example workflow

You can in principle remove `snakemake-minimal` and `sra-toolkit` from the list of packages.
However, you will not be able to automatically run the provided example workflow or download sequence datasets from SRA.


We provide an example Snakemake workflow (for publicly available mouse exomes), which downloads all needed reference FASTA files and exome FASTQ files, generates a hash table as an index and classifies the reads.


To run this workflow,

* you will need space for the downloaded datasets and result files, so snakemake should be executed in a separate working directory with lots of space for the datset.
* you will additionally need the `snakemake-minimal` package.
  Make sure you are in the working directory, that your conda environment called `xengsort` is active, and then additionally install Snakemake:
  ```bash
  conda install -c bioconda  snakemake-minimal
  ```
* ensure that xengsort's `Snakefile` is present in the working directory.
  It can be symbolically linked, such as:
  ```bash
  cd /path/to/workdir
  ln -s /path/to/xengsort/Snakefile Snakefile
  ```

Now Snakemake can be run as follows:
```bash
snakemake -n  # dry-run: What will happen?
snakemake -j 16  --use-conda  # execute with 16 threads
```
The `-n` (or `--dry-run`) option first performs a dry run and prints out what will be done.
In the real invocation, the `-j 16` option uses up to 16 CPU cores to execute 16 separate jobs in parallel or one job that uses 16 threads, or any combination.

You can examine the (commented) Snakefile to see what happens in each step:

* Reference sequences (human and mouse genome and transcriptome) will be downloaded from Ensembl in FASTA format.
* The k-mer index (for k=25) will be built from the FASTA files (`xengsort index`).
* An example dataset (a human-captured mouse exome) will be downloaded from SRA using sra-toolkit and saved in FASTQ format (paired-end reads).
* The paired-end reads in the dataset will be classified according to species (`xengsort classify`)

This will run for quite some time (especially downloads and index creation), best leave it overnight.
The results will appear in the `results/` directory.

To run your own human/mouse xenograft analysis, you can continue to use the same index.
All reference files, including the index (`.hash` and `.info`) are in the `ref/` directory.
You can follow the structure of the Snakefile to create your own custom workflow.
Additional information on how to use `xengsort` is given in the usage guide below.


----

# Usage Guide

xengsort is a multi-command tool with several subcommands (like git), in particular
- `xengsort index` builds an index (a bucketed 3-way Cuckoo hash table)
- `xengsort classify` classifies a sequences sample (FASTQ files) using an existing index

It is a good idea to run `xengsort index --help` to see all available options.
Using `--help` works on any subcommand.


### How to build an index

To build an index for xengsort, several parameters must be provided, which are described in the following.

First, a file name and a path for the index must be chosen.
The index is stored in two files. We will use `myindex` to store the index in the current folder.

Second, two reference genomes (host and graft) must be provided (in FASTA files). 
We assume that they are given as `host.fa.gz` and `graft.fa.gz`. 
The files can be provided as an uncompressed file or compressed using `gzip`, `bzip2` or `xz`.
The corresponding options are `-H` or `--host` and `-G` or `--graft`. 
Each option can take several arguments as files. 
```
xengsort index --index myindex -H host.fa.gz -G graft.fa.gz -n 4_500_000_000  [OPTIONS]
```

We must specify the size of the hash table:

- `-n` or  `--nobjects`: number of k-mers that will be stored in the hash table. This depends on the used reference genomes and must be estimated beforehand! As a precise estimate of the number of different k-mers can be difficult, you can err on the safe side and provide a generously large estimate, examine the final (low) load factor and then rebuild the index with a smaller `-n` parameter to achieve the desired load. There are also some tools that quickly estimate the number of distinct k-mers in large files, such as [ntCard](https://github.com/bcgsc/ntCard) or [KmerEstimate](https://github.com/srbehera11/KmerEstimate). As a guide: Human and mouse genome and transcriptome together comprise around 4.5 billion 25-mers, as shown in the examples above.
**This option must be specified; there is no default!**


We may further specify additional properties of the hash table:

- `-b` or `--bucketsize` indicates how many elements can be stored in one bucket (or page). This is 4 by default.

- `--fill` between 0.0 and 1.0 describes the desired fill rate or load factor of the hash table.
Together with `-n`, the number of slots in the table is calculated as `ceil(n/fill)`. In our experiments we used 0.88. (The number of buckets is then the smallest odd integer that is at least `ceil(ceil(n/fill)/p)`.)

- `--aligned` or `--unaligned`: indicates whether each bucket should consume a number of bits that is a power of 2. Using `--aligned` ensures that each bucket stays within the same cache line, but may waste space (padding bits), yielding faster speed but possibly (much!) larger space requirements. With `--unaligned`, no bits are used for padding and buckets may cross cache line boundaries. This is slightly slower, but may save a little or a lot of space (depending on the bucket size in bits). The default is `--unaligned`, because the speed decrease is small and the memory savings can be significant.

- `--hashfunctions` defines the parameters for the hash functions used to store the key-value pairs. If the parameter is unspecified, different random functions are chosen each time. The hash functions can be specified using a colon separated list: `--hashfunctions linear945:linear9123641:linear349341847`. It is recommended to have them chosen randomly unless you need strictly reproducible behavior, in which case the example given here is recommended.

The final important parameter is about parallelization:

- `-W` or `--weakthreads` defines how many threads are used to calculate weak *k*-mers.

Most of the parameters can also be provided in a config file (`.yaml`):
- `--cfg` or `--config` defines the path the the config file.
 
### How to classify

To classify a FASTQ sample (one or several single-end or paired-end files), make sure you are in an environment where xengsort and its dependencies are installed.
Then run the `xengsort classify` command with a previously built index, such as
```
xengsort classify --index myindex --fastq single.fq.gz --prefix myresults --mode count
```
for single-end reads, or 
```
xengsort classify --index myindex --fastq paired.1.fq.gz --pairs paired.2.fq.gz --prefix myresults --mode count
```
for paired-end reads.

Out tool offers three different classification modes. The algorithm can be specified using the `--mode` parameter.
 - count: Classifies the read based on the number of $k$-mers that belong to host or graft.
 - coverage: Classifies the read based on the proportions covered by $k$-mers of each class.
 - quick: Classifies the read only based on the third and third last $k$-mer.


The parameter `--prefix` or equivalently `--out` is required and defines the prefix for all output files; this can be a combination of path and file prefix, such as `/path/to/sorted/samplename`.  Typically, there will be 5 output files for each of the first and the second read pair:
  - `{prefix}.host.1.fq.gz`: host reads
  - `{prefix}.graft.1.fq.gz`: graft reads
  - `{prefix}.both.1.fq.gz`: reads that could originate from both
  - `{prefix}.neither.1.fq.gz`: reads that originate from neither host nor graft
  - `{prefix}.ambiguous.1.fq.gz`: (few) ambiguous reads that cannot be classified,
  
  and similarly with `.2.fq.gz`. For single-end reads, there is only `.fq.gz` (no numbers).

The compression type can be specified using the `--compression` parameter.
Currently we support `gz` (default), `bzip`, `xz` and `none` (uncompressed).


Further parameters and options are:
- `-T` defines how many threads are used for classification (4 to 8 is recommended).
- `--filter`: With this flag, only the graft reads are output.
- `--count`: With this flag, only the number of reads in each category is counted, but the reads are not sorted.


Please report a [GitLab issue](https://gitlab.com/genomeinformatics/xengsort/-/issues) in case of problems.

Happy sorting!


----

# Troubleshooting

*  **Snakemake throws errors when attempting to download the example dataset from SRA**.

This may happen for several reasons:
  1. The dataset is quite large, over 20 GB. Make sure you have sufficient space (also temporary space) and sufficient disk quota (on a shared system) to store all of the files. 
  1. Another source of trouble may be that for some reason and older version of `sra-tools` gets called. We use the `fasterq-dump` tool to download the data, which did not exist in older verisons. To use a clean environment with a recent version of `sra-tools`, you can run snakemake as `snakemake -j 16 --use-conda`, which will generate a separate environment only for the download (this takes additional time, but may resolve the problem).
  1. In earlier versions, the dataset was downloaded from a different location which is no longer available. Please check that you are using at least v1.1.0 (`xengsort --version`). If not, please do a fresh clone and follow the tutorial to set up a new environment (delete the old one first) and run `pip install -e .`, as explained above in the tutorial.

*  **Indexing stops after a few seconds with a failure.**

The most likely cause of this is that you have not specified the size of the hash table (`-n` parameter). 
(From version 1.0.1, the `-n` parameter is required, and the error cannot occur anymore. Please update to the latest version!)
For the human and mouse genomes this is approximately `-n 4_500_000_000` (4.5 billion).
It is unfortunately a limitation of the implementation that the hash table size has to be specified in advance.
If uncertain, use a generous overestimate (e.g., add the sizes of the two genomes) and look in the output for the line that starts with `choice nonzero`.
This is the exact number of k-mers stored.
You can use this value to re-index everything in a second iteration.

* **The `xengsort classify` step throws an error about `NoneType` vs. `str`.**

This can happen if you do not specify the `--out` or `--prefix` parameter.
(From version 1.0.2, this parameter is required, and the error cannot occur anymore. Please update to the latest version!)



----

# Citation

If you use xengsort, please cite the article in "Algorithms for Molecular Biology".
The BibTeX entry is provided here:
```
@Article{pmid33810805,
   Author="Jens Zentgraf and Sven Rahmann",
   Title="Fast lightweight accurate xenograft sorting",
   Journal="Algorithms Mol Biol",
   Year="2021",
   Volume="16",
   Number="1",
   Pages="2",
   Month="Apr"
}
```


In addition, you may also cite the WABI 2020 proceedigs paper:
```
@InProceedings{ZentgrafRahmann2020xengsort,
  author =	{Jens Zentgraf and Sven Rahmann},
  title =	{Fast Lightweight Accurate Xenograft Sorting},
  booktitle =	{20th International Workshop on Algorithms in Bioinformatics (WABI 2020)},
  pages =	{4:1--4:16},
  series =	{Leibniz International Proceedings in Informatics (LIPIcs)},
  ISBN =	{978-3-95977-161-0},
  ISSN =	{1868-8969},
  year =	{2020},
  volume =	{172},
  editor =	{Carl Kingsford and Nadia Pisanti},
  publisher =	{Schloss Dagstuhl--Leibniz-Zentrum f{\"u}r Informatik},
  address =	{Dagstuhl, Germany},
  URL =		{https://drops.dagstuhl.de/opus/volltexte/2020/12793},
  URN =		{urn:nbn:de:0030-drops-127933},
  doi =		{10.4230/LIPIcs.WABI.2020.4},
  annote =	{Keywords: xenograft sorting, alignment-free method, Cuckoo hashing, k-mer}
}
```
