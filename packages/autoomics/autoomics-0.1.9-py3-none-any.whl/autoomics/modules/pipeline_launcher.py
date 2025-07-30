import subprocess

def launch_pipeline(data_type, read_path, genome, gtf):
    if data_type == 'bulk-seq':
        nf_script = 'pipelines/bulk_seq/main.nf'
    elif data_type == 'atac-seq':
        nf_script = 'pipelines/atac_seq/main.nf'
    elif data_type == 'scRNA-seq':
        nf_script = 'pipelines/scrna_seq/main.nf'
    elif data_type == 'chip-seq':
        nf_script = 'pipelines/chip_seq/main.nf'
    else:
        raise ValueError("Type d'analyse non supporté.")

    cmd = [
        "nextflow", "run", nf_script,
        "--reads", read_path,
        "--genomeDir", genome,
        "--gtf", gtf
    ]
    subprocess.run(cmd, check = True)


def run_seurat_analysis():
    print("📊 Analyse scRNA-seq avec Seurat...")
    subprocess.run(["Rscript", "pipelines/scrna_seq/seurat_analysis.R"], check=True)
