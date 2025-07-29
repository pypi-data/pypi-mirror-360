import json
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Union, Type

from datamodel_code_generator import InputFileType, generate
from pydantic import BaseModel


def _write_json_schema_to_tempfile(schema: dict) -> Tuple[Path, tempfile.TemporaryDirectory]:
    """
    Write the JSON schema to a temporary file and return the file path and its temp directory.

    Parameters
    ----------
    schema : dict
        The JSON schema dictionary to write.

    Returns
    -------
    Tuple[Path, tempfile.TemporaryDirectory]
        The path to the temporary schema file and its temp directory (to keep alive).
    """
    temp_dir = tempfile.TemporaryDirectory()
    json_path = Path(temp_dir.name) / "schema.json"
    json_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    return json_path, temp_dir


def _run_datamodel_codegen(input_path: Path, output_path: Optional[Path] = None) -> str:
    """
    Run datamodel-code-generator on the given schema file path.

    Parameters
    ----------
    input_path : Path
        Path to the input JSON schema file.
    output_path : Path, optional
        If provided, code will be written to this file and also returned as a string.

    Returns
    -------
    str
        The generated Python source code as a string.
    """
    generate(
        input_=input_path,
        input_file_type=InputFileType.JsonSchema,
        output=output_path if output_path else None,
    )

    if output_path:
        return output_path.read_text(encoding="utf-8")
    else:
        # datamodel-codegen defaults to writing to model.py
        default_file = Path("model.py")
        return default_file.read_text(encoding="utf-8")


def generate_class_code(
    model: Type[BaseModel],
    output_path: Optional[Union[str, Path]] = None,
    model_name: Optional[str] = None,
) -> str:
    """
    Generate Pydantic model class source code from a BaseModel instance using datamodel-code-generator.

    Parameters
    ----------
    model : Type[BaseModel]
        The Pydantic model to generate code for.
    output_path : str or Path, optional
        If given, writes code to this file. Otherwise returns code as string only.
    model_name : str, optional
        Optional name override for the model title.

    Returns
    -------
    str
        The generated Python source code as a string.
    """
    if hasattr(model, "model_json_schema"):
        schema = model.model_json_schema()
    else:
        schema = model.schema()

    if model_name:
        schema["title"] = model_name

    schema_path, temp_dir = _write_json_schema_to_tempfile(schema)

    output_file_path = Path(output_path) if output_path else None

    code = _run_datamodel_codegen(schema_path, output_file_path)

    # Keep temp_dir alive until after codegen is finished
    return code
