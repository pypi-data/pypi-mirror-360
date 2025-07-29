import argparse
from .train import run_training
from .run import run_inference

    
def main():
    parser = argparse.ArgumentParser(prog="gpgin", description="GPGIN CLI tool: train and infer")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Train subcommand
    train_parser = subparsers.add_parser("train", help="Train a model")
    train_parser.add_argument("-X", required=True, help="Input sdf file (e.g., dataset.sdf)")
    train_parser.add_argument("-y", required=True, help="Target newline-separated values file (e.g., targets.txt)")
    train_parser.add_argument("--name", required=True, help="Model name")
    train_parser.add_argument('--force_reload_data', action='store_true', help='Reprocess data')
    train_parser.add_argument('--force_retrain', action='store_true', help='Overwrite previous model with the same name')
    train_parser.add_argument('--batch_size', default=32, type=int, help='training batch size')
    train_parser.add_argument('--n_epochs', default=100, type=int, help='number of epochs used in training')
    train_parser.add_argument('--target_name', default='undefined', help='(e.g., u0 on QM9)')
    train_parser.add_argument('--dataset_name', default='undefined', help='(e.g., QM9)')
    
    # Run subcommand
    run_parser = subparsers.add_parser("run", help="Run inference")
    run_parser.add_argument("-X", required=True, help="Input dataset file or directory")
    run_parser.add_argument("--out", required=True, help="Output file for predictions")
    run_parser.add_argument("--name", required=True, help="Model name")
    run_parser.add_argument('--force_reload_data', action='store_true', help='Reprocess data')
    run_parser.add_argument('--batch_size', default=32, type=int, help='inference batch size')

    args = parser.parse_args()

    if args.command == "train":
        run_training(args)
    elif args.command == "run":
        run_inference(args)
