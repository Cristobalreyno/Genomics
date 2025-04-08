🔬 Genomes Metadata Fetcher for NCBI Assemblies
Este script en Python automatiza la recuperación y enriquecimiento de metadatos genómicos para un género bacteriano desde la base de datos NCBI (Assembly). Integra herramientas de línea de comandos de NCBI (esearch, efetch, datasets) para generar un archivo .csv limpio y estructurado, ideal para estudios de genómica comparativa, vigilancia ambiental o bioinformática evolutiva.

⚙️ Características
Consulta todos los ensamblajes genómicos disponibles para un género específico.

Parsea metadatos detallados (ensamblaje, taxonomía, técnicas de secuenciación, GC%, número de genes, etc.).

Enriquecimiento mediante datasets summary genome.

Procesamiento paralelo para mayor velocidad.

Exportación automatizada a CSV.

Registro de errores en un archivo error_log.txt.

🧪 Requisitos
Dependencias de Python

Instalar con:
pip install -r requirements.txt
Herramientas adicionales (no incluidas en pip)
Este script requiere herramientas de línea de comandos proporcionadas por el NCBI, las cuales deben estar instaladas en el sistema y disponibles en el entorno ($PATH), ya que se invocan mediante subprocess.

Herramientas requeridas:

esearch y efetch (parte del paquete Entrez Direct)
datasets (parte del paquete NCBI Datasets CLI)

El script verifica automáticamente la presencia de estas herramientas al inicio. Si alguna falta, se mostrará un mensaje como:

La herramienta 'esearch' no está instalada o no está en el PATH.
Instalación de herramientas requeridas
Entrez Direct (esearch, efetch)
Instalación manual en Linux/macOS:

cd ~
ftp https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/edirect.tar.gz
tar -xvzf edirect.tar.gz
export PATH=${HOME}/edirect:$PATH
Guía oficial

NCBI Datasets CLI (datasets)
Instalación recomendada con Conda:

conda install -c conda-forge ncbi-datasets-cli
O desde el sitio oficial:
https://www.ncbi.nlm.nih.gov/datasets/docs/command-line-start/

▶️ Uso
Ejecutar desde la terminal:

python get_ncbi_genomes_metadata.py <nombre_del_género>
Ejemplo:

python get_ncbi_genomes_metadata.py Pantoea
Esto generará un archivo pantoea_genomes_metadata.csv con todos los genomas disponibles del género, incluyendo información detallada y enriquecida.

📁 Archivos generados
género_genomes_metadata.csv: archivo con metadatos completos.

error_log.txt: registro de errores durante la ejecución.

🧬 Estructura general del script
check_dependencies(): verifica que las herramientas de NCBI estén instaladas.

fetch_ncbi_data(): obtiene los ensamblajes del género.

parse_genomes(): transforma el XML en un DataFrame.

fetch_datasets_metadata(): recupera metadatos adicionales por accession.

main(): coordina la ejecución, paraleliza las tareas y exporta los resultados.

👨‍🔬 Autor
Cristóbal Reyno
PhD (c) en Biología Celular y Molecular Aplicada – Universidad de La Frontera
Investigador en resistencia antimicrobiana en ambientes acuáticos
📍 Temuco, Chile

Este script fue desarrollado como parte de una investigación académica orientada al estudio de bacterias ambientales resistentes a múltiples antibióticos.
Puede ser reutilizado libremente con fines científicos o educativos.