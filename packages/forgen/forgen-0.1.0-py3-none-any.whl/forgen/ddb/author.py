from datetime import datetime
import boto3
import logging

ddb = boto3.resource("dynamodb", region_name="us-east-1")
author_table = ddb.Table("AuthorRegistry")


def add_verify_author(cognito_user: dict, wallet: str):
    email = cognito_user.get("email")
    user_id = cognito_user.get("sub")
    if not email or not user_id or not wallet:
        raise ValueError("Missing required user fields.")

    domain = email.split("@")[-1]
    item = {
        "author_id": wallet,
        "email": email,
        "cognito_id": user_id,
        "domain": domain,
        "verified": True, # domain not in [],
        "created_at": datetime.utcnow().isoformat()
    }

    author_table.put_item(Item=item)
    logging.info(f"Author onboarded: {wallet} from {email}")


def remove_author(wallet: str):
    author_table.delete_item(Key={"author_id": wallet})
    logging.info(f"Author removed: {wallet}")


def update_author_wallet(old_wallet: str, new_wallet: str):
    item = author_table.get_item(Key={"author_id": old_wallet}).get("Item")
    if not item:
        raise ValueError("Old wallet not found.")

    item["author_id"] = new_wallet
    remove_author(old_wallet)
    author_table.put_item(Item=item)
    logging.info(f"Author wallet updated: {old_wallet} → {new_wallet}")


def verify_author(author_id: str):
    item = author_table.get_item(Key={"author_id": author_id})
    if "verified" in item:
        return True
    return False
