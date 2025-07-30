import argparse

from dutch_med_hips.hips_functions import HideInPlainSight


def main():
    parser = argparse.ArgumentParser(description="Process some reports.")
    parser.add_argument(
        "--input_file",
        type=str,
        required=True,
        help="Path to the input file containing reports.",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="Path to the output file to save modified reports.",
    )
    parser.add_argument("--seed", type=int, default=42, help="The random seed to use.")
    parser.add_argument(
        "--ner_labels", type=list, default=None, help="Named entity recognition labels."
    )
    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as f:
        report = f.read()

    hips = HideInPlainSight()
    report = hips.apply_hips(report=report, seed=args.seed, ner_labels=args.ner_labels)

    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(report)


if __name__ == "__main__":
    main()
