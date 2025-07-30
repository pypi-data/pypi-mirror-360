import boto3

from forgen.user.user import UserRegistry

ddb = boto3.resource("dynamodb", region_name="us-east-1")
table = ddb.Table("UserRegistry")

def save_user_registry_to_ddb(user: UserRegistry):

    item = {
        "user_id": user.user_id,
        "display_name": user.display_name,
        "wallet": user.wallet,
        "email": user.email,
        "domain": user.domain,
        "verified": user.verified,
    }
    table.put_item(Item=item)
