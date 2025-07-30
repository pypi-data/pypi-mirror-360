from autoomics.cli import parse_args
from autoomics.runner import run_pipeline

args = parse_args()
run_pipeline(args)