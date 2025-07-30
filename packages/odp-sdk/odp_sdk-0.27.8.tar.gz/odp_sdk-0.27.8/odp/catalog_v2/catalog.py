import logging
from typing import Optional

import requests

from odp.new_client import Client


# TEMPORARY
class Dataset:
    def __init__(self, cli: Client, data: dict):
        self.cli = cli
        meta = data["metadata"]
        self.uuid = meta["uuid"]
        self.name = meta.get("name", None)

    @classmethod
    def by_name(cls, cli: Client, name: str) -> Optional["Dataset"]:
        res = cli._request(
            requests.Request(
                method="GET",
                url=cli.base_url + "/catalog/catalog.hubocean.io/dataset/" + name,
            )
        )
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return Dataset(cli, res.json())

    @classmethod
    def find(cls, cli: Client, name: Optional[str] = None) -> list["Dataset"]:
        conds = [{"#EQUALS": ["$kind", "catalog.hubocean.io/dataset"]}]
        if name is not None:
            conds.append({"#EQUALS": ["$metadata.name", name]})
        res = cli._request(
            requests.Request(
                method="POST",
                url=cli.base_url + "/catalog/list/",
                data={"#AND": conds},
            )
        )
        return [Dataset(cli, item) for item in res.json()["results"]]

    @classmethod
    def create(cls, cli: Client, name: str, description: str = "n/a") -> "Dataset":
        res = cli._request(
            requests.Request(
                method="POST",
                url=cli.base_url + "/catalog",
                data={
                    "kind": "catalog.hubocean.io/dataset",
                    "version": "v1alpha3",
                    "metadata": {
                        "name": name,
                        "description": description,
                        "labels": {},
                    },
                    "spec": {
                        "storage_controller": "registry.hubocean.io/storageController/storage-tabular",
                        "storage_class": "registry.hubocean.io/storageClass/tabular",
                        "maintainer": {
                            "contact": "Just Me <raw_client_example@hubocean.earth>"
                        },  # <-- strict syntax here
                    },
                },
            )
        )
        logging.info("created: %s", res.content)
        res.raise_for_status()
        return Dataset(cli, res.json())
