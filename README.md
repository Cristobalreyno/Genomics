# 🔬 Genomes Metadata Fetcher (Version 2.0)

This Python script automates the retrieval and enrichment of genomic metadata for a bacterial genus from NCBI databases (Assembly and Datasets CLI). It features robust logging, batch retrieval, extended parsing, and parallel processing using `ThreadPoolExecutor`.

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

### Python

Install with pip:
```bash
pip install -r requirements.txt
```

### External Dependencies

The script requires the following command-line tools to be installed and available in your system path:

- `esearch` and `efetch` (part of Entrez Direct)
- `datasets` (part of the NCBI Datasets CLI)

#### Installing Entrez Direct
# Descargar edirect.tar.gz desde navegador o con curl
```bash
cd ~
https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/edirect.tar.gz
or 
curl -O https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/edirect.tar.gz
# Descomprimir
tar -xvzf edirect.tar.gz

# Agregar edirect al PATH (temporalmente)
export PATH=${HOME}/edirect:$PATH

```

#### Installing the Datasets CLI

Using Conda:
```bash
conda install -c conda-forge ncbi-datasets-cli
```

Official documentation: [NCBI Datasets CLI](https://www.ncbi.nlm.nih.gov/datasets/docs/command-line-start/)

## ▶️ Usage

```bash
python Get_NCBI_genomes_metadata_V2.py <genus_name> [--max-workers N]
```

Example:
```bash
python Get_NCBI_genomes_metadata_V2.py Pantoea --max-workers 12
```

This will generate a `genomes_metadata.csv` file (and optionally `.xlsx`) containing enriched metadata for all available assemblies of the specified genus.

## 📁 Output Files

- `genomes_metadata.csv`: main file containing the combined metadata.
- `genomes_metadata.xlsx`: Excel version (if `openpyxl` is installed).
- `error_log.txt`: internal errors logged during execution.
- `missing_metadata.log`: accessions for which extended metadata could not be retrieved.

## 👨‍🔬 Author

**Cristóbal Reyno**  
PhD(c) in Applied Cellular and Molecular Biology – Universidad de La Frontera  
Researcher in antimicrobial resistance in aquatic environments  
📍 Temuco, Chile

> This script may be freely reused for scientific or educational purposes.


## 👨‍🔬 Author

**Cristóbal Reyno**  
PhD(c) in Applied Cellular and Molecular Biology – Universidad de La Frontera  
Researcher in antimicrobial resistance in aquatic environments  
📍 Temuco, Chile

> This script was developed as part of the author's doctoral thesis entitled  
> *“Genomic characterization and virulence against Dictyostelium discoideum of multiple antibiotic-resistance (MAR) Pantoea strains isolated from the Villarrica Lake sediments (southern Chile).”*
  
> The script is freely available for scientific and educational use.
