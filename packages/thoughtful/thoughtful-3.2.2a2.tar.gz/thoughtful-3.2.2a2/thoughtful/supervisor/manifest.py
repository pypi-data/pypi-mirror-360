"""
This module contains the code for the manifest and it's dependencies. At the
base of the yaml model we have manifest metadata including UID, name,
source, author, yaml version, and default record column titles. The main
event of the manifest is the `workflow` attribute which contains a tree
of the intended workflow of the digital worker.

The `workflow` object is a list of ``Step`` yaml models. Each contains step
metadata including step ID, description, name, and overriding record column
titles. Each step can likewise contain a list of ``Step`` yaml models,
allowing for a tree of sub-steps to be defined.

For example:

.. code-block:: yaml

    uid: appnGPBr50yrJImj1
    name: CellStaff1 - Job Board Posting
    description: ""
    author: Kaleb Smith
    source: https://www.somesite.com/
    version: 0.1.0
    columns:
      succeeded: Finished
      failed: Error

    workflow:
      - step_id: 1
        title: Prepare for Process
        description: do this
        steps:
          - step_id: 1.1
            title: Get Credentials from Bitwarden
            description: do that
          - step_id: 1.2
            title: Get mapping files
            description: |-
              Get the mapping files from the server
            columns:
              succeeded: Done
              warning: Warning!
            steps:
              - step_id: 1.2.1
                title: Get mapping file from S3
      - step_id: 2
        title: Populate job postings
        description: do this
        steps:
          - step_id: 2.1
            title: Aya Connect
            description: Just your average step

The columns attributes are optional, as are each of their three values. If you
choose to override the record status column titles at the base, it will be the
default throughout the entire workflow. If you choose to override the record
status column titles at the step level, it will be the default for that step
only.
"""

from __future__ import annotations

import json
import pathlib
from collections import defaultdict
from typing import Any, List, Optional, TypeVar, Union

import pydantic
import yaml
from pydantic import BaseModel, field_validator

StepId = TypeVar("StepId", bound=str)


class RecordStatusColumns(BaseModel):
    """
    Columns is a list of column names that are used to display the
    output of a step in a table. When left blank, the default values
    are used. This is an attribute of the ``Step`` yaml model, as well as the
    base ``Manifest`` yaml model. When defined at the base, it will be the
    default for all steps. When defined at the step level, it will be the
    default for that step only.
    """

    succeeded: Optional[str] = None
    """
    str, optional: The name of the column that contains the succeeded records.
    """

    failed: Optional[str] = None
    """
    str, optional: The name of the column that contains the failed records.
    """

    warning: Optional[str] = None
    """
    str, optional: The name of the column that contains the warning records.
    """

    def __json__(self):
        return self.model_dump_json(indent=4)


class Step(BaseModel):
    """
    A step to execute in a manifest workflow. This is an attribute of the
    ``Manifest`` yaml model. Each step can contain a list of ``Step`` yaml
    models, allowing for a tree of sub-steps to be defined.
    """

    step_id: str
    """
    str: The ID of the step.
    """

    title: str
    """
    str: The name of the step.
    """

    description: Optional[str] = None
    """
    str: A description of the step.
    """

    steps: Optional[List[Step]] = []
    """
    List[Step], optional: A list of children steps. Empty list if no children.
    """

    columns: Optional[RecordStatusColumns] = None
    """
    RecordStatusColumns, optional: The columns to display in the UI for record
    statuses. If none, it will use manifest defaults.
    """

    # PyCharm can't recognize that `@validator` creates a class method
    # noinspection PyMethodParameters
    @field_validator("steps", mode="before")
    def set_steps(cls, v: List[Step]):
        """
        Validator: Set the steps attribute to an empty list if it is None.
        """
        return v or []

    def __json__(self):
        return {
            "step_id": self.step_id,
            "title": self.title,
            "description": self.description,
            "steps": [step.__json__() for step in self.steps],
            "columns": self.columns.__json__() if self.columns else self.columns,
        }


class Manifest(BaseModel):
    """
    A digital worker manifest, typically read from a `manifest.yaml` file.
    """

    uid: str
    """
    str: The unique ID of the manifest.
    """

    name: str
    """
    str: The name of the process.
    """

    description: Optional[str] = None
    """
    str: Manifest/process description.
    """

    author: Optional[str] = None
    """
    str, optional: Who wrote the manifest.
    """

    source: str
    """
    str: Where the manifest came from.
    """

    version: Optional[str] = None
    """
    str: Version of manifest (added for backwards compatibility)
    """

    columns: Optional[RecordStatusColumns] = None
    """
    RecordStatusColumns, optional: The columns to display in the UI for record
    statuses. If none, it will use defaults.
    """

    workflow: List[Step]
    """
    List[Step]: The list of steps to execute.
    """

    @classmethod
    def from_file(cls, filename: Union[str, pathlib.Path]) -> Manifest:
        """
        Creates an instance of this class from a YAML file.

        Args:
            filename: The name of the manifest .yaml file.

        Returns:
            Manifest: The new Manifest instance.
        """
        # Load the manifest using the base class importer
        try:
            manifest_yaml = yaml.safe_load(open(filename))
            manifest_in_flight = cls.model_validate(manifest_yaml)

        except pydantic.ValidationError as ex:
            errors = ex.errors()
            error_message = (
                f"Invalid manifest file with {len(errors)} "
                f"validation error(s) at the root "
                f"level\n{_pretty_errors_string(errors)}"
            )
            raise ValueError(error_message) from ex

        # The base importer loads the steps as dicts, so convert them into
        # proper steps
        step_dicts = manifest_in_flight.workflow
        final_steps: List[Step] = cls._load_manifest_file_steps(step_dicts)
        manifest_in_flight.workflow = final_steps

        return manifest_in_flight

    @classmethod
    def yaml_to_json(
        cls,
        manifest_path: Union[str, pathlib.Path],
        json_path: Union[str, pathlib.Path],
    ) -> None:
        """
        Converts a YAML manifest into a JSON manifest by converting the raw YAML
        contents into a JSON dictionary. This function is "dumb" and just writes
        the direct-to-JSON version of the YAML file.

        Args:
            manifest_path: The manifest YAML to consume.
            json_path: The output file to write the JSON payload to.
        """
        with manifest_path.open("r") as f:
            manifest_yaml = yaml.safe_load(f)

        with pathlib.Path(json_path).open("w") as json_path:
            json.dump(manifest_yaml, json_path)

    def __json__(self) -> dict[str, Any]:
        """
        Returns the values of this instance as a dictionary that are needed
        for a report.
        Returns:
            dict: The JSON-able dictionary (of only primitives) representation
                of this instance.
        """
        # Only return the keys we want in the report
        keys = ["uid", "name", "description", "author", "source", "columns"]
        manifest_json = {k: v for k, v in self.__dict__.items() if k in keys}
        manifest_json["workflow"] = [step.__json__() for step in self.workflow]
        return manifest_json

    def write_to_json_file(self, json_path):
        _json = self.__json__()
        with open(json_path, "w+") as json_file:
            json.dump(_json, json_file)

    # Private implementation
    @classmethod
    def _load_manifest_file_steps(
        cls, step_dicts: List[Union[dict, Step]]
    ) -> List[Step]:
        """
        Creates a list of Step instances based on a list of steps in dictionary
        format (usually loaded from a raw YAML file).

        Args:
            step_dicts: The steps as dictionaries to parse.

        Returns:
            List[Step]: The new Step instances.

        """
        successful_steps = []
        # Keep track of errors for specific step IDs, and also errors for any
        # steps that don't have a step ID
        errors_for_step_ids: dict[str, List[Any]] = defaultdict(list)
        errors_for_unknown_steps: List[Any] = []

        # Try parsing each step
        for step_dict in step_dicts:
            try:
                new_step = Step.model_validate(step_dict)
                successful_steps.append(new_step)
            except pydantic.ValidationError as ex:
                errors = ex.errors()
                if "step_id" in step_dict:
                    _id = step_dict["step_id"]
                    errors_for_step_ids[_id].extend(errors)
                else:
                    errors_for_unknown_steps.append(errors)

        # Back out if there's no errors
        if not (errors_for_step_ids or errors_for_unknown_steps):
            return successful_steps

        # Otherwise, build the pretty print error string
        message = "Manifest step(s) are invalid"
        for step_id, errors in errors_for_step_ids.items():
            message += f"\nstep id: {step_id}\n"
            message += _pretty_errors_string(errors, indent=4)

        for index, step_errors in enumerate(errors_for_unknown_steps):
            message += f"\nunknown step {index + 1} (no step ID found)\n"
            message += _pretty_errors_string(step_errors, indent=4)

        raise ValueError(message)


def _pretty_errors_string(errors: list, indent: int = 0) -> str:
    """
    A custom string formatter for pydantic errors.

    See Also:
        The original implementation of this (with a slightly different format)
        is here - https://github.com/samuelcolvin/pydantic/blob/8846ec4685e749b93907081450f592060eeb99b1/pydantic/error_wrappers.py#L82-L83
    """

    def pretty_error(error: dict) -> str:
        loc_str = " -> ".join(str(ll) for ll in error["loc"])
        spacer = " " * indent
        return f'{spacer}{loc_str}\n    {spacer}{error["msg"]}'

    return "\n".join(pretty_error(err) for err in errors)
