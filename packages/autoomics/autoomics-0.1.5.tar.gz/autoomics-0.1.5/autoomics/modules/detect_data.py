def detect_data_type(fastq_files):
    if any('R2' in f or 'I1' in f for f in fastq_files) and 'barcodes' in f:
        return 'scRNA-seq'
    elif len(fastq_files) >= 2:
        return 'bulk-seq'
    else:
        return 'chip-seq'