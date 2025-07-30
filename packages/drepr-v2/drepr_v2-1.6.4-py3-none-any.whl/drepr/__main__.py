from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from threading import local
from typing import Annotated, Optional
from uuid import uuid4

import typer

from drepr.models.prelude import DRepr, OutputFormat, PreprocessResourceOutput
from drepr.planning.class_map_plan import ClassesMapExecutionPlan
from drepr.program_generation.main import FileOutput, MemoryOutput, Output, gen_program

app = typer.Typer(pretty_exceptions_short=True, pretty_exceptions_enable=False)


@dataclass
class ResourceInput:
    id: str
    file: Path

    @staticmethod
    def from_string(value: str) -> ResourceInput:
        lst = value.split("=", 1)
        if len(lst) != 2:
            raise Exception(f"Invalid resource format. Expect <id>`=`<file_path>")

        id, file = lst
        file = Path(file)
        if not file.exists():
            raise Exception(f"Resource file `{file}` does not exist")

        return ResourceInput(id, file)


@app.command()
def main(
    repr: Annotated[
        Path,
        typer.Argument(
            help="A path to a file containing representation (support 2 formats: JSON & YML)",
            exists=True,
            dir_okay=False,
        ),
    ],
    resource: Annotated[
        Optional[list[str]],
        typer.Argument(
            help="file paths of resources in this format: <resource_id>=<file_path>",
        ),
    ] = None,
    progfile: Annotated[
        Optional[Path],
        typer.Option(
            help="A path to a file to save the generated program", exists=False
        ),
    ] = None,
    outfile: Annotated[
        Optional[Path],
        typer.Option(
            help="A path to a file to save the transformed data", exists=False
        ),
    ] = None,
    format: Annotated[
        OutputFormat,
        typer.Option(
            help="The output format",
        ),
    ] = OutputFormat.TTL,
    tmpdir: Annotated[
        Path,
        typer.Option(
            help="A directory to save temporary files",
            default="/tmp/drepr",
        ),
    ] = Path("/tmp/drepr"),
    debuginfo: Annotated[
        bool, typer.Option(help="Whether to add debug information to the program")
    ] = False,
):
    parsed_repr = DRepr.parse_from_file(repr)
    exec_plan = ClassesMapExecutionPlan.create(parsed_repr)

    if outfile is not None:
        output = FileOutput(outfile, format)
    else:
        output = MemoryOutput(format)

    prog = gen_program(exec_plan.desc, exec_plan, output, debuginfo).to_python()
    cleanup = progfile is None
    if progfile is not None:
        with open(progfile, "w") as f:
            f.write(prog)
    else:
        tmpdir.mkdir(parents=True, exist_ok=True)
        unique_id = str(uuid4()).replace("-", "_")
        progfile = tmpdir / f"main_{unique_id}.py"
        progfile.write_text(prog)

    if resource is None:
        return

    parsed_resources = {
        (x := ResourceInput.from_string(r)).id: x.file for r in resource
    }
    spec = importlib.util.spec_from_file_location("drepr_prog", progfile)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if outfile is not None:
        module.main(
            *[
                parsed_resources[r.id]
                for r in exec_plan.desc.resources
                if not isinstance(r, PreprocessResourceOutput)
            ],
            outfile,
        )
    else:
        print(
            module.main(
                *[
                    parsed_resources[r.id]
                    for r in exec_plan.desc.resources
                    if not isinstance(r, PreprocessResourceOutput)
                ]
            )
        )

    if cleanup:
        progfile.unlink()


if __name__ == "__main__":
    app()
