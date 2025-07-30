import os

import hvac


class VaultWrapper:
    def __init__(self, url=None, token=None):
        self.client = hvac.Client(
            url=url or os.getenv("VAULT_ADDR"),
            token=token or os.getenv("VAULT_TOKEN"),
        )

    def __getitem__(self, path) -> dict:
        root = path.split("/")[0]
        vault_path = "/".join(path.split("/")[1:])

        response = self.client.secrets.kv.read_secret_version(
            path=vault_path, mount_point=root, raise_on_deleted_version=True
        )

        return response["data"]["data"]
