def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True)
    parser.add_argument('--output', '-o', default='result/')
    parser.add_argument('--explain',action = 'store_true')
    parser.add_argument('--config',  default='..autoomocsrc.yaml')
    parse_args()