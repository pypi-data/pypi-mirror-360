from autoomics.modules import detect_data_type
from autoomics.modules import add_scrna_section
import subprocess
import sys

def run_pipeline(args):
    input_path = args.input
    species = args.species
    output_dir = args.output

    # Détecte le type de données
    data_type = detect_data_type(input_path)
    print(f"🔍 Données détectées : {data_type}")

    # Si les données sont de type 'scrna-seq'
    if data_type == "scrna-seq":
        subprocess.run([
            "nextflow", "run", "pipelines/scrna_seq/main.nf",
            "--reads", input_path,
            "--transcriptome", "ref/cellranger_ref/",
            "--sample", "sample"
        ])
        subprocess.run(["Rscript", "pipelines/scrna_seq/seurat_analysis.R"])

    # Si les données sont de type 'rnaseq'
    elif data_type == "rnaseq":
        subprocess.run(["nextflow", "run", "pipelines/rna_seq/main.nf", "--reads", input_path])

    # Si les données sont de type 'chipseq'
    elif data_type == "chipseq":
        subprocess.run(["nextflow", "run", "pipelines/chip_seq/main.nf", "--reads", input_path])

    # Si aucun type de données connu
    else:
        print(f"⚠️ Type de données non pris en charge : {data_type}")
        
    add_scrna_section(output_dir)
