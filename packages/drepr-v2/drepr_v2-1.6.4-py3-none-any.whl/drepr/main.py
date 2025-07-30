from __future__ import annotations

import importlib.util
from hashlib import sha256
from pathlib import Path
from typing import Literal, Mapping, Optional
from uuid import uuid4

from drepr.models.prelude import (
    DRepr,
    OutputFormat,
    PreprocessResourceOutput,
    ResourceData,
)
from drepr.planning.class_map_plan import ClassesMapExecutionPlan
from drepr.program_generation.main import FileOutput, MemoryOutput, gen_program


def convert(
    repr: DRepr | Path,
    resources: Mapping[str, Path | ResourceData],
    progfile: Optional[Path | str] = None,
    outfile: Optional[Path] = None,
    format: OutputFormat = OutputFormat.TTL,
    tmpdir: Path = Path("/tmp/drepr"),
    tmp_idgen: Literal["uuid", "hash"] = "uuid",
    debuginfo: bool = False,
    cleanup: bool = True,
):
    if not isinstance(repr, DRepr):
        repr = DRepr.parse_from_file(repr)

    exec_plan = ClassesMapExecutionPlan.create(repr)

    if outfile is not None:
        output = FileOutput(outfile, format)
    else:
        output = MemoryOutput(format)

    prog = gen_program(exec_plan.desc, exec_plan, output, debuginfo).to_python()
    if progfile is not None:
        progfile = Path(progfile)
        cleanup = False

    if progfile is not None:
        with open(progfile, "w") as f:
            f.write(prog)
    else:
        tmpdir.mkdir(parents=True, exist_ok=True)
        if tmp_idgen == "uuid":
            unique_id = str(uuid4()).replace("-", "_")
        else:
            unique_id = sha256(prog.encode()).hexdigest()
        progfile = tmpdir / f"main_{unique_id}.py"
        progfile.write_text(prog)

    if len(resources) == 0:
        return

    spec = importlib.util.spec_from_file_location("drepr_prog", progfile)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if outfile is not None:
        output = module.main(
            *[
                resources[r.id]
                for r in exec_plan.desc.resources
                if not isinstance(r, PreprocessResourceOutput)
            ],
            outfile,
        )
    else:
        output = module.main(
            *[
                resources[r.id]
                for r in exec_plan.desc.resources
                if not isinstance(r, PreprocessResourceOutput)
            ]
        )

    if cleanup:
        progfile.unlink()

    return output
