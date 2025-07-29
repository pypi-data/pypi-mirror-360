from tallyfy import TallyfySDK, TallyfyError
from dotenv import load_dotenv
import os
load_dotenv()

def get_api_key() -> str:
    """Get API key from environment"""
    api_key = os.getenv('TALLYFY_API_KEY')
    if not api_key:
        raise TallyfyError("TALLYFY_API_KEY environment variable is required")
    return api_key


def get_org_id() -> str:
    """Get org_id from environment"""
    org_id = os.getenv('TALLYFY_ORG_ID')
    if not org_id:
        raise TallyfyError("TALLYFY_ORG_ID environment variable is required")
    return org_id

api_key = get_api_key()
org_id = get_org_id()

with TallyfySDK(api_key=api_key, base_url='https://staging.api.tallyfy.com') as sdk:
    # print(sdk.get_organization_guests(org_id=org_id))
    sdk.close()
    pass
print(sdk.get_organization_guests(org_id=org_id))