# This script is an adapted version of 
# https://github.com/FG-AI4H-TG-Symptom/fgai4h-tg-symptom-models-schemas/blob/master/generators/berlin-model-schema-generator.py
# To maintain the single source of truth this script is using data.json which is produced
# during berlin model parsing.

import json
import os
import pandas as pd
import pathlib
import hashlib
from typing import Optional


real_path = os.path.dirname(os.path.realpath(__file__))


def create_const(value, description):
    return {"const": value, "default": value, "description": description}


def lookup_const(json_schema_object, property_name):
    return json_schema_object["properties"][property_name]["const"]


def add_properties(json_schema_object, properties: dict):
    for key, value in properties.items():
        json_schema_object["properties"][key] = value
        json_schema_object["required"].append(key)


def concept_template(
    concept_name, id_raw, name, generated_id
):
    sctid = None

    if "CUSTOM" not in id_raw:
        sctid = int(id_raw)

    concept = {
        "type": "object",
        "title": name,
        "properties": {
            "id": create_const(generated_id, f"{concept_name} ID"),
            "name": create_const(name, f"{concept_name} name"),
            "standardOntologyUris": create_const([], f"URIs referencing this {concept_name.lower()} in standard ontologies")
        },
        "required": ["id", "name", "standardOntologyUris"],
        "additionalProperties": False,
    }

    if sctid is not None:
        concept['properties']['standardOntologyUris']['const'].append(f'http://snomed.info/id/{sctid}')

    return concept


def get_conditions():
    data_path = os.path.join(pathlib.Path(real_path).parent, "mmvb_backend/common/fixtures/data.json")
            
    with open(data_path, 'r') as _file:
        data = _file.read()
    data_obj = json.loads(data)

    return data_obj['conditions']


def get_clinical_findings():
    data_path = os.path.join(pathlib.Path(real_path).parent, "mmvb_backend/common/fixtures/data.json")
            
    with open(data_path, 'r') as _file:
        data = _file.read()
    data_obj = json.loads(data)

    return data_obj['symptoms']


def register_conditions(schema_json):

    conditions = get_conditions()
    conditions_refs = []

    for condition_ in conditions:
        
        condition_sctid = condition_['sctid']
        condition_name = condition_['short_name']
        condition_id = condition_['id']
        
        condition = concept_template("Condition", condition_sctid, condition_name, condition_id)

        schema_json["definitions"][condition_id] = condition

        conditions_refs.append(
            {"title": condition_name, "$ref": f"#/definitions/{condition_id}", }
        )

        schema_json["definitions"]["condition"] = {"oneOf": conditions_refs}



def register_clinical_finding(clinical_finding_sctid, clinical_finding_name, clinical_finding_id, schema_json):

    current_clinical_finding = concept_template(
        "Clinical finding",
        clinical_finding_sctid,
        clinical_finding_name,
        clinical_finding_id,
    )
    # clinical_finding_id = lookup_const(current_clinical_finding, "id")
    add_properties(
        current_clinical_finding,
        {"state": {"$ref": "#/definitions/clinicalFindingState"}},
    )

    add_properties(
        current_clinical_finding,
        {
            "attributes": {
                "type": "array",
                "items": {
                    "oneOf": []
                },  # attributes register themselves later
                "uniqueItems": True,
            }
        },
    )

    schema_json["definitions"][clinical_finding_id] = current_clinical_finding


def register_attribute(attribute_, clinical_finding_id, schema_json):

    attribute_sctid = attribute_['sctid']
    attribute_name = attribute_['short_name']
    attribute_id = attribute_['id']
    attribute_multiselect = attribute_['multiselect']

    attribute = concept_template(
        "Attribute",
        attribute_sctid,
        attribute_name,
        attribute_id
    )

    if attribute_multiselect:
        # values register themselves later
        add_properties(
            attribute,
            {
                "values": {
                    "type": "array",
                    "description": "Possible values for this attribute "
                    "(at least one, multi-selection possible)",
                    "items": {"oneOf": []},
                    "uniqueItems": True,
                    "minItems": 1,
                }
            },
        )
    else:
        # values register themselves later
        add_properties(
            attribute,
            {
                "value": {
                    "description": "Possible values for this attribute (exactly one)",
                    "oneOf": [],
                }
            },
        )

    already_registered_attribute = schema_json["definitions"].get(
        attribute_id, None
    )

    attribute_ref = {
        "title": attribute_name
        if already_registered_attribute is None
        else lookup_const(already_registered_attribute, "name"),
        "$ref": f"#/definitions/{attribute_id}",
    }

    schema_json["definitions"][clinical_finding_id]["properties"][
        "attributes"
    ]["items"]["oneOf"].append(attribute_ref)

    attribute["properties"]["scope"] = create_const(
        clinical_finding_id,
        "ID of clinical finding this attribute is scoped to",
    )

    schema_json["definitions"][attribute_id] = attribute

    return attribute_ref


def register_clinical_findings_and_attributes(schema_json):
    clinical_findings_ = get_clinical_findings()
    
    clinical_findings_refs = []
    attributes_refs = []

    for clinical_finding_ in clinical_findings_:

        clinical_finding_sctid = clinical_finding_['sctid']
        clinical_finding_name  = clinical_finding_['short_name']
        clinical_finding_id  = clinical_finding_['id']

        register_clinical_finding (
            clinical_finding_sctid,
            clinical_finding_name,
            clinical_finding_id,
            schema_json
        )
        clinical_findings_refs.append(
            {
                "title": clinical_finding_name,
                "$ref": f"#/definitions/{clinical_finding_id}",
            }
        )

        for attribute_ in clinical_finding_['attributes']:
            attribute_ref = register_attribute(attribute_, clinical_finding_id, schema_json)
            attributes_refs.append(attribute_ref)


        for attribute_ in clinical_finding_['attributes']:
            register_attribute_value_set(attribute_, clinical_finding_id, schema_json)

    schema_json["definitions"]["clinicalFinding"] = {"oneOf": clinical_findings_refs}
    # likely not necessary: attributes are never referenced generically, always explicitly by a linked symptom
    schema_json["definitions"]["attribute"] = {"oneOf": attributes_refs}

    for clinical_finding in clinical_findings_refs:
        clinical_finding_id = clinical_finding['$ref'].split('/')[-1]
        clinical_finding_definition = schema_json["definitions"][clinical_finding_id]
        if len(clinical_finding_definition['properties']['attributes']['items']['oneOf']) == 0:
            del clinical_finding_definition['properties']['attributes']['items']

            clinical_finding_definition['properties']['attributes']['const'] = [
            ]


def register_attribute_value_set(attribute_, clinical_finding_id, schema_json):

    values = []
    current_attribute_id = attribute_['id']

    for value_ in attribute_['value_set']:

        value_name = value_['short_name']
        value_id = value_['id']
        value_sctid = value_['sctid']

        value = concept_template(
            "Value",
            value_sctid,
            value_name,
            value_id
        )

        schema_json["definitions"][value_id] = value

        value_ref = {"title": value_name, "$ref": f"#/definitions/{value_id}"}

        attribute_properties = schema_json["definitions"][current_attribute_id][
            "properties"
        ]

        attribute_value_list = (
            attribute_properties["values"]["items"]["oneOf"]
            if "values" in attribute_properties
            else attribute_properties["value"]["oneOf"]
        )

        attribute_value_list.append(value_ref)

        values.append(value_ref)

    # likely not necessary: values are never referenced generically, always explicitly by a linked attribute
    schema_json["definitions"]["value"] = {"oneOf": values}


def generate_schema():
    generic_schema_path   = os.path.join(pathlib.Path(real_path), "schemas/berlin-model-generic.schema.json")
    generated_schema_path = os.path.join(pathlib.Path(real_path), "schemas/berlin-model.schema.json")
    
    with open(
        generic_schema_path, "r"
    ) as base_schema_json_file:
        base_schema_json = json.load(base_schema_json_file)

    base_schema_json["$id"] = (
        "https://raw.githubusercontent.com/FG-AI4H-TG-Symptom/"
        "fgai4h-tg-symptom-models-schemas/master/schemas/berlin-model.schema.json"
    )

    base_schema_json[
        "description"
    ] = "FGAI4H TG Symptom Cases Schema – Berlin (generated)"

    base_schema_json[
        "$comment"
    ] = "This model is auto-generated! Don't manually make changes you wish to persist."


    register_conditions(base_schema_json)
    register_clinical_findings_and_attributes(base_schema_json)

    with open(generated_schema_path, "w") as generated_schema_json_file:
        json.dump(base_schema_json, generated_schema_json_file, indent=2)


if __name__ == "__main__":
    generate_schema()
