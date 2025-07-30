from autoomics.modules import detect_data_type
from autoomics.modules import add_scrna_section
import subprocess
import sys

def run_pipeline(args):
    input_path = args.input
    species = args.species
    output_dir = args.output

    data_type = detect_data_type(input_path)
    print(f"🔍 Données détectées : {data_type}")

    if data_type == "scrna-seq":
        subprocess.run([
            "nextflow", "run", "pipelines/scrna_seq/main.nf",
            "--reads", input_path,
            "--transcriptome", "ref/cellranger_ref/",
            "--sample", "sample"
        ])
        subprocess.run(["Rscript", "pipelines/scrna_seq/seurat_analysis.R"])

    elif data_type == "rnaseq":
        subprocess.run(["nextflow", "run", "pipelines/rna_seq/main.nf", "--reads", input_path])
    
    add_scrna_section(output_dir)