from typing import List

from google.cloud import compute_v1
from google.oauth2 import service_account


def get_gcp_regions(gcp_service_account_file: str) -> List[str]:
    credentials = service_account.Credentials.from_service_account_file(filename=gcp_service_account_file)
    return [
        region.name
        for region in compute_v1.RegionsClient(credentials=credentials).list(project=credentials.project_id).items
    ]
