from datetime import datetime
from typing import Dict

from forgen.ddb.ddb import ddb

job_status_table = ddb.Table("JobStatus")

def get_status_by_job_id_from_ddb(job_id: str) -> Dict[str, int]:
    response = job_status_table.get_item(Key={"job_id": job_id})
    if "Item" not in response or "status" not in response["Item"]:
        raise Exception(f"Job status not found: {response}")
    item = response["Item"]
    return {
        "status": item.get("status", None),
        "error_type": item.get("error_type", None),
        "error_message": item.get("error_message", None)
    }


def set_job_in_ddb(job_id: str, status, resource_id=None, resource_name=None) -> None:
    response = job_status_table.get_item(Key={"job_id": job_id})
    current_item = response.get('Item', {})
    new_item = {
        "job_id": job_id,
        "status": status,
        "create_date": datetime.now().isoformat(),
        "resource_id": current_item.get("resource_id"),
        "resource_name": current_item.get("resource_name")
    }
    if resource_id is not None:
        new_item["resource_id"] = resource_id

    if resource_name is not None:
        new_item["resource_name"] = resource_name

    job_status_table.put_item(Item=new_item)


def update_status_by_job_id_in_ddb(job_id: str, status: str, error_type: str = None, error_message: str = None, s3_key: str = None) -> None:
    # Define initial update expressions
    update_expression = "SET #statusAttr = :statusValue"
    expression_attribute_names = {"#statusAttr": "status"}
    expression_attribute_values = {":statusValue": status}

    # Conditionally add error_type to the update expression
    if error_type is not None:
        update_expression += ", #errorTypeAttr = :errorTypeValue"
        expression_attribute_names["#errorTypeAttr"] = "error_type"
        expression_attribute_values[":errorTypeValue"] = error_type

    # Conditionally add error_message to the update expression
    if error_message is not None:
        update_expression += ", #errorMessageAttr = :errorMessageValue"
        expression_attribute_names["#errorMessageAttr"] = "error_message"
        expression_attribute_values[":errorMessageValue"] = error_message

    # Conditionally add error_message to the update expression
    if s3_key is not None:
        update_expression += ", #s3KeyAttr = :s3KeyValue"
        expression_attribute_names["#s3KeyAttr"] = "s3_key"
        expression_attribute_values[":s3KeyValue"] = s3_key

    # Perform the update operation
    job_status_table.update_item(
        Key={"job_id": job_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values
    )