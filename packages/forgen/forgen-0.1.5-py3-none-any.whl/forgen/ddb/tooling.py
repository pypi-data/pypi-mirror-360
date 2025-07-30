from forgen.ddb.ddb import ddb
from datetime import datetime
from decimal import Decimal


tool_registry_table = ddb.Table("ToolRegistry")

tool_usage_table = ddb.Table("ToolUsage")

def log_tool_usage(
    tool_id: str,
    author_id: str,
    version: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
):
    timestamp = datetime.utcnow().isoformat()
    usage_log = {
        "usage_id": f"{tool_id}#{timestamp}",  # PK in DDB, or use uuid4
        "timestamp": timestamp,
        "tool_id": tool_id,
        "author_id": author_id,
        "version": version,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }
    try:
        tool_usage_table.put_item(Item=usage_log)
    except Exception as e:
        print(f"[ERROR] Failed to write usage log: {e}")


def add_tool_to_tool_registry_in_ddb(username, tool_id, author_id=None, **kwargs):
        """Add (put) a new item into ToolRegistry using primary key and additional attributes."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "username": username,
            "tool_id": tool_id,
            "create_date": now,
            "last_accessed_date": now
        }
        if author_id:
            item["author_id"] = author_id  # ← wallet address
        item.update(kwargs)
        return tool_registry_table.put_item(Item=item)

def get_tool_registry_items_by_id(username, tool_id):
        """Retrieve item from ToolRegistry by its primary key and update last_accessed_date."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        key = { 'username': username, 'tool_id': tool_id }
        response = tool_registry_table.get_item(Key=key)
        item = response.get('Item', None)
        if item:
            tool_registry_table.update_item(
                Key=key,
                UpdateExpression="SET last_accessed_date = :ts",
                ExpressionAttributeValues={":ts": now}
            )
        return item

def update_attr_for_tool_in_ddb(username, tool_id, attr_name, attr_value):
        """Update any single attribute of an item in ToolRegistry, also refresh last_accessed_date."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        tool_registry_table.update_item(
            Key={ 'username': username, 'tool_id': tool_id },
            UpdateExpression="SET #attrName = :attrValue, last_accessed_date = :ts",
            ExpressionAttributeNames={"#attrName": attr_name},
            ExpressionAttributeValues={":attrValue": attr_value, ":ts": now}
        )

def delete_tool_registry_item_by_id(username, tool_id):
        """Delete item from ToolRegistry by its primary key."""
        return tool_registry_table.delete_item(Key={ 'username': username, 'tool_id': tool_id })

def query_tool_registry_table_by_partition_key(username):
            """Query items from ToolRegistry by partition key only."""
            response = tool_registry_table.query(
                KeyConditionExpression="username = :pkval",
                ExpressionAttributeValues={":pkval": username}
            )
            return response.get('Items', [])

def query_tool_registry_table_by_sort_key_prefix(username, prefix):
                """Query items from ToolRegistry by partition key and sort key prefix."""
                response = tool_registry_table.query(
                    KeyConditionExpression="username = :pkval AND begins_with(tool_id, :skprefix)",
                    ExpressionAttributeValues={":pkval": username, ":skprefix": prefix}
                )
                return response.get('Items', [])

def query_tool_registry_items_by_sort_key_range(username, start_key, end_key):
                """Query items from ToolRegistry by partition key and sort key range."""
                response = tool_registry_table.query(
                    KeyConditionExpression="username = :pkval AND tool_id BETWEEN :skstart AND :skend",
                    ExpressionAttributeValues={":pkval": username, ":skstart": start_key, ":skend": end_key}
                )
                return response.get('Items', [])

def scan_all_tool_registry_items(filter_expression=None, expression_values=None, limit=None):
            """Scan all items from ToolRegistry with optional filtering and pagination."""
            scan_kwargs = {}
            if filter_expression:
                scan_kwargs['FilterExpression'] = filter_expression
            if expression_values:
                scan_kwargs['ExpressionAttributeValues'] = expression_values
            if limit:
                scan_kwargs['Limit'] = limit

            response = tool_registry_table.scan(**scan_kwargs)
            items = response.get('Items', [])

            # Paginate if there are more items
            while 'LastEvaluatedKey' in response:
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = tool_registry_table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))
                if limit and len(items) >= limit:
                    items = items[:limit]
                    break

            return items

def query_tool_registry_items_by_attribute(attr_name, attr_value, index_name=None):
            """Query items from ToolRegistry by any attribute with optional use of secondary index."""
            query_kwargs = {
                'FilterExpression': "#attrName = :attrValue",
                'ExpressionAttributeNames': {"#attrName": attr_name},
                'ExpressionAttributeValues': {":attrValue": attr_value}
            }

            if index_name:
                # Use query if index is provided
                query_kwargs['IndexName'] = index_name
                response = tool_registry_table.query(**query_kwargs)
            else:
                # Fallback to scan if no index provided
                response = tool_registry_table.scan(**query_kwargs)

            return response.get('Items', [])

def batch_get_tool_registry_items(keys_list):
            """Retrieve multiple items from ToolRegistry by their primary keys using BatchGetItem."""

            # Prepare the list of keys in the proper format
            formatted_keys = []
            for key_dict in keys_list:
                formatted_key = {}
                if 'username' in key_dict:
                    formatted_key['username'] = key_dict['username']
                if 'tool_id' in key_dict:
                    formatted_key['tool_id'] = key_dict['tool_id']
                formatted_keys.append(formatted_key)

            # Batch get can only process 100 items at a time
            all_items = []
            for i in range(0, len(formatted_keys), 100):
                batch_keys = formatted_keys[i:i+100]
                response = ddb.batch_get_item(
                    RequestItems={
                        'ToolRegistry': {
                            'Keys': batch_keys
                        }
                    }
                )
                all_items.extend(response.get('Responses', {})                    .get('ToolRegistry', []))

            return all_items

def count_tool_registry_items(filter_expression=None, expression_values=None):
            """Count items in ToolRegistry with optional filtering."""
            scan_kwargs = {'Select': 'COUNT'}
            if filter_expression:
                scan_kwargs['FilterExpression'] = filter_expression
            if expression_values:
                scan_kwargs['ExpressionAttributeValues'] = expression_values

            response = tool_registry_table.scan(**scan_kwargs)
            count = response.get('Count', 0)

            # Continue counting if there are more items
            while 'LastEvaluatedKey' in response:
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = tool_registry_table.scan(**scan_kwargs)
                count += response.get('Count', 0)

            return count

def get_tool_registry_items_by_tool_name(tool_name):
            """Retrieve items from ToolRegistry where tool_name matches the given value."""
            response = tool_registry_table.scan(
                FilterExpression="tool_name = :val",
                ExpressionAttributeValues={":val": tool_name}
            )
            return response.get('Items', [])

def update_tool_registry_items_tool_name_by_pk(username, tool_id, new_value):
            """Update tool_name attribute of item in ToolRegistry by primary key and refresh last_accessed_date."""
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).isoformat()
            return tool_registry_table.update_item(
                Key={ 'username': username, 'tool_id': tool_id },
                UpdateExpression="SET tool_name = :val, last_accessed_date = :ts",
                ExpressionAttributeValues={":val": new_value, ":ts": now}
            )

def update_tool_registry_table_item_tool_name_by_pk(username, tool_id, new_value):
            """Update tool_name attribute of item in ToolRegistry by primary key."""
            return tool_registry_table.update_item(
                Key={ 'username': username, 'tool_id': tool_id },
                UpdateExpression="SET tool_name = :val",
                ExpressionAttributeValues={":val": new_value}
            )

def delete_tool_registry_items_by_tool_name(tool_name):
            """Delete items from ToolRegistry where tool_name matches."""
            items = get_tool_registry_items_by_tool_name(tool_name)
            for item in items:
                key = { 'username': item['username'], 'tool_id': item['tool_id'] }
                tool_registry_table.delete_item(Key=key)

def check_tool_registry_items_tool_name_is_set(username, tool_id):
            """Check if the tool_name attribute is set for a given item in ToolRegistry."""
            item = get_tool_registry_items_by_id(username, tool_id)
            return item and 'tool_name' in item and item['tool_name'] is not None
