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

class InMemoryInsertOne:
    """
    InMemoryInsertOne class manages inserting single records efficiently into a sharded collection stored on storage.

    Key features:
    - Initializes by loading existing shard data, index, and logs from blobs.
    - Preloads existing record IDs into memory for fast duplicate detection.
    - Manages shards based on a shard size limit, flushing full shards to blob storage.
    - Keeps an in-memory index mapping record IDs to shards, and flushes it to blob storage.
    - Buffers insertions and flushes data, index, and logs when a threshold is reached or explicitly called.
    - Uses msgpack for efficient binary serialization of shard data.
    - Logs insertion operations with timestamps and metadata for auditing.
    - Automatically handles shard rollover when the current shard exceeds the size limit.

    Intended usage:
    - Create an instance per user/database/collection/container combination.
    - Use add_record(record) to insert a new record; duplicates will raise an error.
    - Periodically call flush_all() to persist data and logs.
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

        self.insert_count_since_flush = 0
        self.flush_threshold = 10

        self.existing_ids = self._preload_existing_ids()

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

    def _preload_existing_ids(self):
        ids = set()
        for shard_map in self.index_data:
            for shard_key, id_list in shard_map.items():
                ids.update(id_list)
        return ids

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
        rec_id = record["_id"]

        if rec_id in self.existing_ids:
            raise ValueError(f"Duplicate _id detected: {rec_id}")

        self.existing_ids.add(rec_id)

        if len(self.shard_records) >= self.shard_limit:
            self.flush_shard()
            self.shard_number += 1
            self.shard_filename = f"{self.db}/{self.collection}/{self.collection}_{self.shard_number}.msgpack"
            self.shard_records = []

        self.shard_records.append(record)

        shard_key = f"{self.collection}_{self.shard_number}"
        found = False
        for shard in self.index_data:
            if shard_key in shard:
                shard[shard_key].append(rec_id)
                found = True
                break
        if not found:
            self.index_data.append({shard_key: [rec_id]})

        self.insert_count_since_flush += 1

        if self.insert_count_since_flush >= self.flush_threshold:
            self.flush_all()
            self.insert_count_since_flush = 0

    def flush_all(self):
        if self.shard_records or self.index_data or self.logs_data:
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
