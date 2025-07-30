def add_scrna_section(report_path="results/report.html"):
    with open("umap_clusters.png", "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode("utf-8")

    with open(report_path, "a") as f:
        f.write("<h2>🧬 scRNA-seq - Clustering Seurat</h2>")
        f.write(f'<img src="data:image/png;base64,{img_base64}" width="600">')
