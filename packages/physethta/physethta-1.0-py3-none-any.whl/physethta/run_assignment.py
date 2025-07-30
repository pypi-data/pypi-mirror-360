import argparse
from physethta.loader import load_data
from physethta.config import load_config
from physethta.assigner import build_pis_dict, build_course_dict
from physethta.report import generate_summary
from physethta.external import build_external_mappings


def main():
    parser = argparse.ArgumentParser(description="Run TA assignment processing")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml (default: ./config.yaml)")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    parser.add_argument("--input", type=str, default=".", help="Directory containing input files (default: current directory)")
    parser.add_argument("--draft", action="store_true", help="Generate draft version of the summary")
    args = parser.parse_args()

    paths = {
        "externe": f"{args.input}/Externe.xlsx",
        "vorg": f"{args.input}/vorg.csv",
        "alle": f"{args.input}/alle.csv",
        "sprachen": f"{args.input}/sprachen.csv",
        "config": args.config
    }

    data = load_data(paths)
    config = load_config(paths["config"])

    external, external_pis = build_external_mappings(data["externe"])

    pis = build_pis_dict(data, external, external_pis, config)
    courses, emails, langs, stats = build_course_dict(data, external, config)
    generate_summary(pis, courses, config, langs, emails, draft=args.draft)


