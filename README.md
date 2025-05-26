# 🧬 Genomes Metadata Fetcher (Version 2.0)

This Python script automates the retrieval and enrichment of genomic metadata for a bacterial genus from NCBI databases (Assembly and Datasets CLI).

## ⚙️ Key Features

- Queries all available genome assemblies for a specified genus from NCBI Assembly.
- Retrieves extended metadata for each accession using the NCBI Datasets CLI (`fetch_datasets_metadata`).
- Performs detailed XML parsing, including taxonomy, assembly type, sequencing methods, gene counts, GC content, ANI, CheckM, environmental source, and more.
- Automatically exports results to `.csv` and optionally to `.xlsx` (if `openpyxl` is available).
- Supports parallel processing with configurable thread count (`--max-workers`).
- Automatically checks system dependencies (`esearch`, `efetch`, `datasets`) at runtime.
- Logs errors and missing data in `error_log.txt` and `missing_metadata.log`.
- Prevents file overwriting by generating unique filenames for outputs.

## 🧪 Requirements

Python ≥ 3.8 (installed automatically with Conda), Conda (Anaconda or Miniconda), internet access, and the external tools Entrez Direct (`esearch`, `efetch`) and NCBI Datasets CLI (`datasets`).

Quick Installation and Usage:  
Place both the `Get_NCBI_genomes_metadata_V2.py` script and the `environment.yml` file in the same folder. Conda will install all the necessary libraries and tools, but you still need to run the main script to perform the metadata retrieval. Open a terminal in that folder and run:

```bash
conda env create -f environment.yml
conda activate get_ncbi_genomes_metadata
cd ~
wget https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/edirect.tar.gz
tar -xvzf edirect.tar.gz
echo 'export PATH="${HOME}/edirect:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

If you use zsh, replace `.bashrc` with `.zshrc` in the last command.  
Verify that the following commands work (each should display a help message, not an error):

```bash
esearch -h
efetch -h
datasets --help
```
With the environment activated and all dependencies installed, you can now run:

## ▶ Usage

```bash
python Get_NCBI_genomes_metadata_V2.py <genus_name> --max-workers 8
```

Example:

```bash
python Get_NCBI_genomes_metadata_V2.py Pantoea --max-workers 8
```
Replace `<genus_name>` with the genus you want to analyze. The script will produce output files in the same folder.

## 📁 Output Files
- `genomes_metadata.csv`: main file with the combined metadata  
- `genomes_metadata.xlsx`: Excel version (if `openpyxl` is available)  
- `error_log.txt` and `missing_metadata.log`: log files with errors or accessions missing metadata

Notes: Conda is only used to install the libraries and tools required by the script. You still need to run the provided Python script to actually perform the metadata retrieval. You do not need to use GitHub unless you want to share or update the files.

## 👨‍🔬 Author

**Cristóbal Reyno**  
PhD(c) in Applied Cellular and Molecular Biology – Universidad de La Frontera  
Researcher in antimicrobial resistance in aquatic environments  
📍 Temuco, Chile

This script was developed as part of the author's doctoral thesis entitled  
“Genomic characterization and virulence against Dictyostelium discoideum of multiple antibiotic-resistance (MAR) Pantoea strains isolated from the Villarrica Lake sediments (southern Chile).”*  

It is freely available for scientific and educational use.
