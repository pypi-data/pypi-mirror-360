from decimal import Decimal
import os
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Attr

from forgen.ddb import cache

ddb = boto3.resource("dynamodb", region_name="us-east-1")

MASTER_SECRET_CODE = os.environ.get("MASTER_SECRET_CODE", "")


user_usage_table = ddb.Table("UserUsage")
user_products_table = ddb.Table("UserProducts")

MAX_ITEM_SIZE_BYTES = 400 * 1024


class DdbError(Exception):
    """Exception raised for errors where an item cannot be written to ddb."""
    pass


class DdbItemTooLargeError(Exception):
    """Exception raised for errors where an item is too large."""
    pass


def get_all_items_dynamodb(table_name):
    table = ddb.Table(table_name)
    response = table.scan()
    data = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response.get('Items', []))
    return data


def calculate_attribute_size(value):
    """
    Calculates the size of a ddb attribute based on its type.
    """
    if isinstance(value, dict):
        size = 3  # overhead for map type
        for k, v in value.items():
            size += len(k.encode('utf-8'))  # Size of the key in the map
            size += calculate_attribute_size(v)
        return size
    elif isinstance(value, list):
        size = 3  # overhead for list type
        for item in value:
            size += calculate_attribute_size(item)
        return size
    elif isinstance(value, str):
        return len(value.encode('utf-8')) + 1  # 1 byte for string type
    elif isinstance(value, (int, float)):
        return len(str(value)) + 1  # 1 byte for number type
    elif isinstance(value, bool):
        return 1 + 1  # 1 byte for boolean type
    elif value is None:
        return 1  # Null type takes 1 byte
    else:
        raise TypeError(f"Unsupported type: {type(value)}")


def get_ddb_item_size(item):
    """
    Calculates the size of an item.
    """
    item_size = 0
    for key, value in item.items():
        item_size += len(key.encode('utf-8'))
        item_size += calculate_attribute_size(value)
    return item_size


def can_upload_to_ddb(item):
    """
    Checks if the given item can be uploaded to ddb based on size constraints.
    """
    size = get_ddb_item_size(item)
    print(f"can_upload_to_ddb: Item size is {size} bytes.")
    if size > MAX_ITEM_SIZE_BYTES:
        print(f"can_upload_to_ddb: Item size is {size} bytes, which exceeds the 400 KB limit.")
        return False
    return True


def get_item_from_dynamodb(table_name, primary_key):
    table = ddb.Table(table_name)
    try:
        response = table.get_item(Key=primary_key)
    except Exception as e:
        print("dynamodb: " + str(e))
        return None
    else:
        return response.get('Item')


def set_user_usage(username, time_period, usage):
    print(f"set_user_usage: username: {username}, time_period: {time_period}, usage_count: {usage}")
    user_usage_table.put_item(
        Item={
            "username": username,
            "time_period": cache.get_time_period(),
            "usage_count": usage,
        }
    )


def increment_usage(username, model_id, input_tokens, output_tokens, total_tokens):
    if "gpt-4" in model_id and "preview" in model_id:
        model_id = "gpt_4_turbo"
    else:
        model_id = "gpt_4"

    dollar_cost = (Decimal(input_tokens) / Decimal(16000)) + (Decimal(output_tokens) / Decimal(4000))
    response = user_usage_table.update_item(
        Key={
            "username": username,
            "time_period": cache.get_time_period(),
        },
        UpdateExpression="SET " + model_id + " = if_not_exists(" + model_id + ", :start) + :inc, "
                          "input_tokens = if_not_exists(input_tokens, :start) + :input_inc, "
                          "output_tokens = if_not_exists(output_tokens, :start) + :output_inc, "
                          "total_tokens = if_not_exists(total_tokens, :start) + :total_inc, "
                          "total_dollar_cost = if_not_exists(total_dollar_cost, :start) + :cost_inc",
        ExpressionAttributeValues={
            ':inc': 1,
            ':start': Decimal(0),
            ':input_inc': input_tokens,
            ':output_inc': output_tokens,
            ':total_inc': total_tokens,
            ':cost_inc': dollar_cost,
        },
        ReturnValues="UPDATED_NEW"
    )
    return response


def get_usage_by_username_from_ddb(username) -> str:
    print(f"get_usage_by_username_from_ddb: username: {username}")
    response = user_usage_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("username").eq(username)
    )
    return response.get("Items", [])


def create_user_product_obj(product, username, email):
    print(f"create_user_product_obj: product: {product}, username: {username}, email: {email}")
    user_products_table.put_item(
        Item={
            "product": product,
            "username": username,
            "email": email,
            "has_paid": False,
            "create_date": datetime.now().isoformat(),
        }
    )


def get_email_by_username_from_ddb(product, username) -> str:
    print(f"get_email_by_username_from_ddb: product: {product}, username: {username}")
    response = user_products_table.get_item(Key={
        "product": product,
        "username": username
    })
    if "Item" not in response or "email" not in response["Item"]:
        return "unknown"
    return response["Item"]["email"]


def update_has_paid_by_product_and_username_in_ddb(product: str, username: str, has_paid: bool) -> None:
    user_products_table.update_item(
        Key={
            "product": product,
            "username": username
        },
        UpdateExpression="SET has_paid = :hasPaidValue",
        ExpressionAttributeValues={
            ":hasPaidValue": has_paid
        },
    )


def get_has_paid_by_product_and_username_from_ddb(product: str, username: str) -> bool:
    response = user_products_table.get_item(Key={
        "product": product,
        "username": username
    })
    if "Item" not in response or "has_paid" not in response["Item"]:
        return False
    return response["Item"]["has_paid"]
