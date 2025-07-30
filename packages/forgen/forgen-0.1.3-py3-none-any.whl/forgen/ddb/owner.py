from datetime import datetime
import boto3
import logging

ddb = boto3.resource("dynamodb", region_name="us-east-1")
owner_table = ddb.Table("OwnerRegistry")


def add_verify_owner(owner_id: str, domain: str, email: str, wallet: str):
    item = {
        "owner_id": owner_id,
        "domain": domain,
        "email": email,
        "wallet": wallet,
        "verified": True, # domain not in [],
        "created_at": datetime.utcnow().isoformat()
    }
    owner_table.put_item(Item=item)
    logging.info(f"Owner onboarded: {wallet} from {email}")


def remove_owner(wallet: str):
    owner_table.delete_item(Key={"owner_id": wallet})
    logging.info(f"Owner removed: {wallet}")


def update_owner_wallet(old_wallet: str, new_wallet: str):
    item = owner_table.get_item(Key={"owner_id": old_wallet}).get("Item")
    if not item:
        raise ValueError("Old wallet not found.")

    item["owner_id"] = new_wallet
    remove_owner(old_wallet)
    owner_table.put_item(Item=item)
    logging.info(f"Owner wallet updated: {old_wallet} → {new_wallet}")


def verify_owner(owner_id: str):
    item = owner_table.get_item(Key={"owner_id": owner_id})
    if "verified" in item:
        return True
    return False