import argparse
import logging
from pathlib import Path
from .generator import generate_ral

def main() -> None:
    script_path = Path(__file__).resolve()
    script_dir = script_path.parent

    parser = argparse.ArgumentParser(description="UVM RAL code generator")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        required=True,
        #default=script_dir / "rdl/example.rdl",
        help="SystemRDL configuration file",
    )
    parser.add_argument(
        "-t",
        "--templates",
        type=Path,
        default=script_dir / "templates",
        help="Directory with Jinja2 templates",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("ral_regs_pkg.sv"),
        help="Output filename",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s]: %(message)s",
    )

    logging.info("Starting UVM-RAL generation...")

    generate_ral(
        config_path=args.config,
        templates_dir=args.templates,
        output_dir=args.output
    )

if __name__ == "__main__":
    main()