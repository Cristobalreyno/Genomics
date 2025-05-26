#!/usr/bin/env python3
"""
Improved Genomes Metadata Fetcher
Author: Cristobal Reyno
Version: 2.0
Description: Downloads and enriches genomic metadata from NCBI Assembly and Datasets, with extended retrieval while preserving previously obtained fields.
"""

import subprocess
import xmltodict
import pandas as pd
import json
import logging
import concurrent.futures
import os
import sys
import shutil
import argparse
import multiprocessing
from datetime import datetime

logger = logging.getLogger(__name__)

def setup_logger():
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_filename = get_unique_filename("error_log.txt")
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger, log_filename


def get_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(new_filename):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    return new_filename


def check_dependencies():
    for tool in ['esearch', 'efetch', 'datasets']:
        if shutil.which(tool) is None:
            logger.error(f"La herramienta '{tool}' no está instalada o no está en el PATH.")
            sys.exit(1)


def fetch_ncbi_data(genus):
    try:
        logger.info("Obteniendo lista de IDs desde NCBI...")
        search_cmd = f'esearch -db assembly -query "{genus}[Organism]" | efetch -format uid'
        result = subprocess.run(search_cmd, shell=True, capture_output=True, text=True, check=True)
        ids = result.stdout.strip().splitlines()
        if not ids:
            logger.error("No se encontraron IDs para el género.")
            return None

        logger.info(f"{len(ids)} genomas encontrados. Descargando metadatos...")
        all_summaries = []
        for i in range(0, len(ids), 200):
            batch = ",".join(ids[i:i+200])
            cmd = f'efetch -db assembly -id {batch} -format docsum'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            raw_block = result.stdout.strip()

            summaries = []
            in_summary = False
            current = []
            for line in raw_block.splitlines():
                if "<DocumentSummary>" in line:
                    in_summary = True
                    current = [line]
                elif "</DocumentSummary>" in line:
                    current.append(line)
                    summaries.append("\n".join(current))
                    in_summary = False
                elif in_summary:
                    current.append(line)

            all_summaries.extend(summaries)

        if not all_summaries:
            logger.error("No se extrajo ninguna entrada DocumentSummary.")
            return None

        header = '<?xml version="1.0" encoding="UTF-8" ?>\n<!DOCTYPE DocumentSummarySet>\n<DocumentSummarySet status="OK">'
        return header + "\n" + "\n".join(all_summaries) + "\n</DocumentSummarySet>"

    except subprocess.CalledProcessError as e:
        logger.error("Error en esearch/efetch: %s", e)
        return None


def parse_genomes(xml_data):
    try:
        data = xmltodict.parse(xml_data)
        genomes = data['DocumentSummarySet']['DocumentSummary']
        if isinstance(genomes, dict):
            genomes = [genomes]
    except Exception as e:
        logger.error("Error al parsear XML: %s", e)
        with open("error_debug_output.xml", "w", encoding="utf-8") as f:
            f.write(xml_data)
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
            'SubmitterOrganization': genome.get('SubmitterOrganization', ''),
            'BioSampleAccn': genome.get('BioSampleAccn', ''),
            'FtpPath_GenBank': genome.get('FtpPath_GenBank', ''),
            'FtpPath_RefSeq': genome.get('FtpPath_RefSeq', ''),
            'Synonym_Genbank': genome.get('Synonym', {}).get('Genbank', ''),
            'Synonym_RefSeq': genome.get('Synonym', {}).get('RefSeq', ''),
            'BioProject_Accn': genome.get('GB_BioProjects', {}).get('Bioproj', {}).get('BioprojectAccn', ''),
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
            'RepresentativeStatus': genome.get('Meta', {}).get('representative-status', '')
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


def fetch_datasets_metadata(accession, missing_log_path):
    cmd = f"datasets summary genome accession {accession}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        json_data = json.loads(result.stdout)

        reports = json_data.get("reports", [])
        if not reports or not isinstance(reports, list):
            raise ValueError(f"JSON vacío o inválido para accession '{accession}'")

        report = reports[0]
        annotation_info = report.get("annotation_info", {})
        gene_counts = annotation_info.get("stats", {}).get("gene_counts", {})

        assembly_info = report.get("assembly_info", {})
        biosample = assembly_info.get("biosample", {})
        attributes = {attr.get("name"): attr.get("value") for attr in biosample.get("attributes", [])}

        assembly_stats = report.get("assembly_stats", {})
        ani = report.get("average_nucleotide_identity", {})
        checkm = report.get("checkm_info", {})
        sample_ids_list = biosample.get("sample_ids", [])

        return {
            "accession": accession,
            # Original fields
            "annotation_method": annotation_info.get("method") or annotation_info.get("name"),
            "annotation_provider": annotation_info.get("provider"),
            "annotation_release_date": annotation_info.get("release_date"),
            "pipeline": annotation_info.get("pipeline"),
            "non_coding": gene_counts.get("non_coding"),
            "protein_coding": gene_counts.get("protein_coding"),
            "pseudogene": gene_counts.get("pseudogene"),
            "total_genes": gene_counts.get("total"),
            "assembly_method": assembly_info.get("assembly_method"),
            "sequencing_tech": assembly_info.get("sequencing_tech"),
            "gc_percent": assembly_stats.get("gc_percent"),
            "completeness": checkm.get("completeness"),
            "isolation_source": attributes.get("isolation_source"),
            "host": attributes.get("host"),
            "geo_loc_name": attributes.get("geo_loc_name"),
            "collected_by": attributes.get("collected_by"),
            "collection_date": attributes.get("collection_date"),
            "environmental_medium": attributes.get("environmental_medium"),
            # Nuevos campos del JSON de ejemplo
            "ds_assembly_level": assembly_info.get("assembly_level"),
            "ds_assembly_name": assembly_info.get("assembly_name"),
            "ds_assembly_status": assembly_info.get("assembly_status"),
            "ds_assembly_type": assembly_info.get("assembly_type"),
            "ds_bioproject_accession": assembly_info.get("bioproject_accession"),
            "ds_refseq_category": assembly_info.get("refseq_category"),
            "ds_assembly_release_date": assembly_info.get("release_date"),
            "ds_assembly_submitter": assembly_info.get("submitter"),
            "ds_biosample_accession": biosample.get("accession"),
            "ds_biosample_description": biosample.get("description", {}).get("title"),
            "ds_biosample_organism_name": biosample.get("description", {}).get("organism", {}).get("organism_name"),
            "ds_biosample_tax_id": biosample.get("description", {}).get("organism", {}).get("tax_id"),
            "ds_biosample_last_updated": biosample.get("last_updated"),
            "ds_biosample_package": biosample.get("package"),
            "ds_biosample_publication_date": biosample.get("publication_date"),
            "ds_biosample_strain": biosample.get("strain"),
            "ds_biosample_submission_date": biosample.get("submission_date"),
            "ds_sample_ids": ";".join([f"{item.get('label', item.get('db'))}:{item.get('value')}" for item in sample_ids_list]),
            "ds_contig_l50": assembly_stats.get("contig_l50"),
            "ds_contig_n50": assembly_stats.get("contig_n50"),
            "ds_gc_count": assembly_stats.get("gc_count"),
            "ds_number_of_contigs": assembly_stats.get("number_of_contigs"),
            "ds_number_of_scaffolds": assembly_stats.get("number_of_scaffolds"),
            "ds_scaffold_l50": assembly_stats.get("scaffold_l50"),
            "ds_scaffold_n50": assembly_stats.get("scaffold_n50"),
            "ds_total_number_of_chromosomes": assembly_stats.get("total_number_of_chromosomes"),
            "ds_total_sequence_length": assembly_stats.get("total_sequence_length"),
            "ds_total_ungapped_length": assembly_stats.get("total_ungapped_length"),
            "ds_ani_best": ani.get("best_ani_match", {}).get("ani"),
            "ds_ani_best_assembly": ani.get("best_ani_match", {}).get("assembly"),
            "ds_match_status": ani.get("match_status"),
            "ds_submitted_organism": ani.get("submitted_organism"),
            "ds_taxonomy_check_status": ani.get("taxonomy_check_status"),
            "ds_checkm_marker_set": checkm.get("checkm_marker_set"),
            "ds_checkm_version": checkm.get("checkm_version"),
            "ds_contamination": checkm.get("contamination"),
            "ds_completeness_percentile": checkm.get("completeness_percentile"),
            "ds_paired_accession": report.get("paired_accession"),
            "ds_source_database": report.get("source_database"),
        }

    except Exception as e:
        logger.error("Fallo en metadata de '%s': %s", accession, e)
        with open(missing_log_path, "a") as f:
            f.write(f"{accession} - {str(e)}\n")
        return None


def main():
    total_failed = 0
    parser = argparse.ArgumentParser(description="Descarga y parsea metadatos de genomas bacterianos.")
    parser.add_argument("genus", help="Nombre del género (ej: Pantoea)")
    parser.add_argument("--max-workers", type=int, help="Número de hilos (por defecto: núcleos de CPU)")

    args = parser.parse_args()
    genus = args.genus
    max_workers = args.max_workers or multiprocessing.cpu_count()

    global logger
    logger, log_file = setup_logger()
    check_dependencies()

    logger.info(f"Procesando género: {genus}")
    xml_data = fetch_ncbi_data(genus)
    if not xml_data:
        sys.exit(1)

    genomes_data = parse_genomes(xml_data)
    if genomes_data is None:
        sys.exit(1)

    df_full = pd.DataFrame(genomes_data).dropna(subset=["AssemblyAccession"])
    logger.info("Genomas parseados: %d", len(df_full))

    missing_log_path = get_unique_filename("missing_metadata.log")

    extra_metadata = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_datasets_metadata, row["AssemblyAccession"], missing_log_path): row["AssemblyAccession"]
            for _, row in df_full.iterrows()
        }
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            acc = futures[future]
            try:
                result = future.result()
                if result:
                    extra_metadata.append(result)
                    logger.info("%d/%d: %s procesado", i, len(futures), acc)
                else:
                    logger.warning("%d/%d: %s sin metadata extra", i, len(futures), acc)
                    total_failed += 1
            except Exception as e:
                logger.error("Error procesando %s: %s", acc, e)
                with open(missing_log_path, "a") as f:
                    f.write(f"{acc} - {str(e)}\n")
                total_failed += 1

    df_extra = pd.DataFrame(extra_metadata)
    df_merged = pd.merge(df_full, df_extra, left_on="AssemblyAccession", right_on="accession", how="left")
    df_merged.drop(columns=["accession"], inplace=True)

    missing_count = df_merged["gc_percent"].isna().sum()
    logger.warning("Genomas sin metadata completa tras merge: %d", missing_count)

    output_csv = get_unique_filename("genomes_metadata.csv")
    df_merged.to_csv(output_csv, index=False)
    logger.info("Archivo CSV exportado: %s", output_csv)

    try:
        df_merged.to_excel(output_csv.replace(".csv", ".xlsx"), index=False)
    except ImportError:
        logger.warning("openpyxl no instalado. Solo se generó CSV.")

    completitud = (len(df_extra) / len(df_full)) * 100
    logger.info("Porcentaje de genomas con metadata extra: %.2f%%", completitud)

    if total_failed > 0:
        logger.info("Total de accesiones sin metadata enriquecida: %d. Ver archivo: %s", total_failed, missing_log_path)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Proceso interrumpido por el usuario.")
        sys.exit(1)

