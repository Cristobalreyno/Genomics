#!/usr/bin/env python3
import subprocess
import xmltodict
import pandas as pd
import json
import logging
import concurrent.futures
import os
import sys
import shutil

# Configuración del logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
file_handler = logging.FileHandler("error_log.txt")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(console_formatter)
logger.addHandler(file_handler)

def check_dependencies():
    for tool in ['esearch', 'efetch', 'datasets']:
        if shutil.which(tool) is None:
            logger.error(f"La herramienta '{tool}' no está instalada o no está en el PATH.")
            sys.exit(1)

def get_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(new_filename):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    return new_filename

def fetch_ncbi_data(genus):
    cmd = f'esearch -db assembly -query "{genus}[Organism]" | efetch -format docsum'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error("Error al ejecutar esearch/efetch: %s", e)
        return None

def parse_genomes(xml_data):
    try:
        data = xmltodict.parse(xml_data)
        genomes = data['DocumentSummarySet']['DocumentSummary']
        if isinstance(genomes, dict):
            genomes = [genomes]
    except Exception as e:
        logger.error("Error al parsear XML: %s", e)
        return None

    genomes_data = []
    for genome in genomes:
        info = {
            'ID': genome.get('Id', ''),
            'AssemblyAccession': genome.get('AssemblyAccession', ''),
            'AssemblyName': genome.get('AssemblyName', ''),
            'Organism': genome.get('Organism', ''),
            'SpeciesName': genome.get('SpeciesName', ''),
            'SpeciesTaxid': genome.get('SpeciesTaxid', ''),
            'AssemblyType': genome.get('AssemblyType', ''),
            'AssemblyStatus': genome.get('AssemblyStatus', ''),
            'Coverage': genome.get('Coverage', ''),
            'ReleaseLevel': genome.get('ReleaseLevel', ''),
            'ReleaseType': genome.get('ReleaseType', ''),
            'SeqReleaseDate': genome.get('SeqReleaseDate', ''),
            'AsmReleaseDate_GenBank': genome.get('AsmReleaseDate_GenBank', ''),
            'AsmReleaseDate_RefSeq': genome.get('AsmReleaseDate_RefSeq', ''),
            'SubmitterOrganization': genome.get('SubmitterOrganization', ''),
            'FtpPath_GenBank': genome.get('FtpPath_GenBank', ''),
            'FtpPath_RefSeq': genome.get('FtpPath_RefSeq', ''),
            'ContigN50': genome.get('ContigN50', ''),
            'ScaffoldN50': genome.get('ScaffoldN50', ''),
            'Synonym_Genbank': genome.get('Synonym', {}).get('Genbank', ''),
            'Synonym_RefSeq': genome.get('Synonym', {}).get('RefSeq', ''),
            'BioProject_Accn': genome.get('GB_BioProjects', {}).get('Bioproj', {}).get('BioprojectAccn', ''),
            'BioSampleAccn': genome.get('BioSampleAccn', ''),
            'AssemblyLevel': genome.get('Meta', {}).get('assembly-level', ''),
            'BuscoTotalCount': genome.get('Busco', {}).get('TotalCount', ''),
            'TaxonomyCheckStatus': genome.get('Meta', {}).get('taxonomy-check-status', ''),
            'LastMajorReleaseAccession': genome.get('LastMajorReleaseAccession', ''),
            'ChainId': genome.get('ChainId', ''),
            'RsUid': genome.get('RsUid', ''),
            'GbUid': genome.get('GbUid', ''),
            'Primary': genome.get('Primary', ''),
            'PartialGenomeRepresentation': genome.get('PartialGenomeRepresentation', ''),
            'PropertyList': genome.get('PropertyList', ''),
            'FtpPath_Assembly_rpt': genome.get('FtpPath_Assembly_rpt', ''),
            'FtpPath_Stats_rpt': genome.get('FtpPath_Stats_rpt', ''),
            'RefSeq_category': genome.get('RefSeq_category', ''),
            'AssemblyStatusSort': genome.get('AssemblyStatusSort', ''),
            'RepresentativeStatus': genome.get('Meta', {}).get('representative-status', ''),
        }

        stats = genome.get('Meta', {}).get('Stats', {}).get('Stat', [])
        if isinstance(stats, dict):
            stats = [stats]

        for stat in stats:
            cat = stat.get('@category', '')
            val = stat.get('#text', '')
            if cat and val.lower() not in ['all', 'unplaced']:
                info[cat] = val

        genomes_data.append(info)
    return genomes_data

def fetch_datasets_metadata(accession):
    cmd = f"datasets summary genome accession {accession}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        json_data = json.loads(result.stdout)

        if "reports" not in json_data or not json_data["reports"]:
            logger.error("No se encontró 'reports' en el JSON para %s", accession)
            return None

        report = json_data["reports"][0]
        limited = {
            "accession": accession,
            "annotation_method": report.get("annotation_info", {}).get("method"),
            "pipeline": report.get("annotation_info", {}).get("pipeline"),
            "non_coding": report.get("annotation_info", {}).get("stats", {}).get("gene_counts", {}).get("non_coding"),
            "protein_coding": report.get("annotation_info", {}).get("stats", {}).get("gene_counts", {}).get("protein_coding"),
            "pseudogene": report.get("annotation_info", {}).get("stats", {}).get("gene_counts", {}).get("pseudogene"),
            "total_genes": report.get("annotation_info", {}).get("stats", {}).get("gene_counts", {}).get("total"),
            "assembly_method": report.get("assembly_info", {}).get("assembly_method"),
            "sequencing_tech": report.get("assembly_info", {}).get("sequencing_tech"),
            "gc_percent": report.get("assembly_stats", {}).get("gc_percent"),
            "completeness": report.get("checkm_info", {}).get("completeness"),
            "isolation_source": None
        }

        for attr in report.get("assembly_info", {}).get("biosample", {}).get("attributes", []):
            if attr.get("name") == "isolation_source":
                limited["isolation_source"] = attr.get("value")
                break

        return limited
    except Exception as e:
        logger.error("Error procesando JSON para %s: %s", accession, e)
        return None

def main():
    if len(sys.argv) < 2:
        logger.error("Uso: python script.py <nombre_del_género>")
        sys.exit(1)

    genus = sys.argv[1]
    check_dependencies()

    logger.info(f"Buscando genomas para el género: {genus}")
    xml_data = fetch_ncbi_data(genus)
    if not xml_data:
        logger.error("No se pudo obtener datos desde NCBI.")
        return

    genomes_data = parse_genomes(xml_data)
    if genomes_data is None:
        logger.error("Error en el parseo de los datos.")
        return

    df_full = pd.DataFrame(genomes_data)
    logger.info("Genomas procesados: %d", len(df_full))

    extra_metadata = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_datasets_metadata, row["AssemblyAccession"]): row["AssemblyAccession"]
            for _, row in df_full.iterrows()
        }
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            acc = futures[future]
            try:
                result = future.result()
                if result:
                    extra_metadata.append(result)
                logger.info("%d/%d: %s procesado", i, len(futures), acc)
            except Exception as e:
                logger.error("Error procesando %s: %s", acc, e)

    df_extra = pd.DataFrame(extra_metadata)
    df_merged = pd.merge(df_full, df_extra, left_on="AssemblyAccession", right_on="accession", how="left")
    df_merged.drop(columns=["accession"], inplace=True)

    output_file = get_unique_filename(f"{genus.lower()}_genomes_metadata.csv")
    df_merged.to_csv(output_file, index=False)
    logger.info("Archivo exportado: %s", output_file)

if __name__ == "__main__":
    main()



# Script para recuperar y enriquecer metadatos genómicos desde NCBI.
# Autor: Cristóbal [Tu Apellido] (2025)
# Licencia: GPL v3.0 - https://www.gnu.org/licenses/gpl-3.0.html

