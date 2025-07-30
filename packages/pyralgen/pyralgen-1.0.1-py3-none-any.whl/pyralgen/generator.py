import logging
from pathlib import Path
import sys
from systemrdl import RDLCompiler, RDLCompileError
from peakrdl_uvm import UVMExporter

def generate_ral(
    config_path: Path, 
    templates_dir: Path, 
    output_dir: Path
) -> None:
    """
    Generate UVM RAL code from SystemRDL
    """

    logging.info(f"Config Path:    {config_path}")
    logging.info(f"Templates Dir:  {templates_dir}")
    logging.info(f"Output Dir:     {output_dir}")

    rdlc = RDLCompiler()

    try:
        rdlc.compile_file(config_path)
        root = rdlc.elaborate()
        exporter = UVMExporter(user_template_dir=templates_dir.as_posix())
        exporter.export(
            node=root,
            path=output_dir.as_posix(),
            export_as_package=True,
            reuse_class_definitions=True,
            use_uvm_factory=True,
        )
    except RDLCompileError:
        sys.exit(1)
