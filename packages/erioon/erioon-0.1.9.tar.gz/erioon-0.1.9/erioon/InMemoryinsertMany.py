import uuid
import json
import datetime
from io import BytesIO
import msgpack
from azure.storage.blob import ContainerClient
from erioon.functions import (
    calculate_shard_number,
    get_shard_limit
)

class InMemoryInsertMany:
    """
    InMemoryInsertMany class manages batch insertion of multiple records efficiently into a sharded collection stored on storage.

    Key features:
    - Initializes by loading existing shard data, index, and logs from blobs.
    - Builds an in-memory set of existing record IDs from shard data and index for quick duplicate checks.
    - Manages shards based on a shard size limit, flushing full shards to blob storage.
    - Maintains an in-memory index mapping record IDs to shards, updating it as new records are added.
    - Supports batch inserts by appending records to the current shard and updating the index accordingly.
    - Flushes shard data, index, and logs to blob storage on demand or when shards reach their size limits.
    - Uses msgpack for efficient binary serialization of shard data.
    - Logs insertion operations with timestamps and metadata for auditing.

    Intended usage:
    - Instantiate per user/database/collection/container combination.
    - Use add_record(record) repeatedly to add records to the current shard.
    - Call flush_all() to persist all data and logs after batch insertions.
    """
    
    def __init__(self, user_id, db, collection, container_url):
        self.user_id = user_id
        self.db = db
        self.collection = collection
        self.container_url = container_url
        self.container_client = ContainerClient.from_container_url(container_url)

        self.shard_number = calculate_shard_number(user_id, db, collection, container_url)
        self.shard_filename = f"{db}/{collection}/{collection}_{self.shard_number}.msgpack"
        self.index_filename = f"{db}/{collection}/index.json"
        self.logs_filename = f"{db}/{collection}/logs.json"

        self._load_shard()
        self._load_index()
        self._load_logs()

        self.shard_limit = get_shard_limit(user_id, db, collection, container_url)

        self.existing_ids = set()
        self._initialize_existing_ids()

    def _initialize_existing_ids(self):
        for rec in self.shard_records:
            if "_id" in rec:
                self.existing_ids.add(rec["_id"])

        for shard_map in self.index_data:
            for _ids in shard_map.values():
                self.existing_ids.update(_ids)

    def _load_shard(self):
        blob_client = self.container_client.get_blob_client(self.shard_filename)
        if blob_client.exists():
            self.shard_records = msgpack.unpackb(blob_client.download_blob().readall(), raw=False)
        else:
            self.shard_records = []

    def _load_index(self):
        blob_client = self.container_client.get_blob_client(self.index_filename)
        try:
            self.index_data = json.loads(blob_client.download_blob().readall())
        except:
            self.index_data = []

    def _load_logs(self):
        blob_client = self.container_client.get_blob_client(self.logs_filename)
        try:
            self.logs_data = json.loads(blob_client.download_blob().readall())
        except:
            self.logs_data = {}

    def add_log(self, method, log_type, log_message, count):
        log_id = str(uuid.uuid4())
        self.logs_data[log_id] = {
            "timestamp": datetime.datetime.now().isoformat(),
            "method": method.upper(),
            "type": log_type.upper(),
            "log": log_message,
            "count": count
        }

    def add_record(self, record):
        if len(self.shard_records) >= self.shard_limit:
            self.flush_shard()

            self.shard_number += 1
            self.shard_filename = f"{self.db}/{self.collection}/{self.collection}_{self.shard_number}.msgpack"
            self.shard_records = []

        self.shard_records.append(record)
        self.existing_ids.add(record["_id"])

        shard_key = f"{self.collection}_{self.shard_number}"
        for shard in self.index_data:
            if shard_key in shard:
                shard[shard_key].append(record["_id"])
                return
        self.index_data.append({shard_key: [record["_id"]]})

    def flush_all(self):
        self.flush_shard()
        self.flush_index()
        self.flush_logs()

    def flush_shard(self):
        blob_client = self.container_client.get_blob_client(self.shard_filename)
        with BytesIO() as buf:
            buf.write(msgpack.packb(self.shard_records, use_bin_type=True))
            buf.seek(0)
            blob_client.upload_blob(buf, overwrite=True)

    def flush_index(self):
        blob_client = self.container_client.get_blob_client(self.index_filename)
        blob_client.upload_blob(json.dumps(self.index_data), overwrite=True)

    def flush_logs(self):
        blob_client = self.container_client.get_blob_client(self.logs_filename)
        blob_client.upload_blob(json.dumps(self.logs_data, indent=2), overwrite=True)
