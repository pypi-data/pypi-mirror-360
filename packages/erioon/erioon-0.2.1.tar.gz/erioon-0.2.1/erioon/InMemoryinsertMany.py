import re
import uuid
import datetime
from io import BytesIO
import msgpack
from azure.storage.blob import ContainerClient
from erioon.functions import get_shard_limit

class InMemoryInsertMany:
    def __init__(self, user_id, db, collection, container_url):
        self.user_id = user_id
        self.db = db
        self.collection = collection
        self.container_url = container_url
        self.container_client = ContainerClient.from_container_url(container_url)

        self.shard_number = self._get_last_shard_number()
        self.shard_filename = f"{db}/{collection}/{collection}_{self.shard_number}.msgpack"
        self.index_filename = f"{db}/{collection}/index.msgpack"
        self.logs_filename = f"{db}/{collection}/logs.msgpack"
        self.shard_limit = get_shard_limit(user_id, db, collection, container_url)

        self._load_shard()
        self._load_index()
        self._load_logs()

        self.existing_ids = set()
        self._initialize_existing_ids()

    def _get_last_shard_number(self):
        prefix = f"{self.db}/{self.collection}/"
        blobs = self.container_client.list_blobs(name_starts_with=prefix)
        shard_pattern = re.compile(rf"{self.collection}_(\d+)\.msgpack$")
        shard_numbers = [int(m.group(1)) for b in blobs if (m := shard_pattern.search(b.name))]
        return max(shard_numbers) if shard_numbers else 0

    def _load_shard(self):
        blob_client = self.container_client.get_blob_client(self.shard_filename)
        if blob_client.exists():
            self.shard_records = msgpack.unpackb(blob_client.download_blob().readall(), raw=False)
        else:
            self.shard_records = []

    def _load_index(self):
        blob_client = self.container_client.get_blob_client(self.index_filename)
        try:
            data = msgpack.unpackb(blob_client.download_blob().readall(), raw=False)
            self.index_data = data if isinstance(data, dict) else {}
        except Exception:
            self.index_data = {}

    def _load_logs(self):
        blob_client = self.container_client.get_blob_client(self.logs_filename)
        try:
            self.logs_data = msgpack.unpackb(blob_client.download_blob().readall(), raw=False)
        except Exception:
            self.logs_data = {}

    def _initialize_existing_ids(self):
        self.existing_ids.clear()
        for rec in self.shard_records:
            if "_id" in rec:
                self.existing_ids.add(rec["_id"])

        shard_key = f"{self.collection}_{self.shard_number}"
        if shard_key in self.index_data:
            self.existing_ids.update(self.index_data[shard_key])

    def get_last_id(self):
        shard_key = f"{self.collection}_{self.shard_number}"
        if shard_key in self.index_data and self.index_data[shard_key]:
            return self.index_data[shard_key][-1]
        elif self.shard_records:
            return self.shard_records[-1].get("_id")
        return None

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
            self._initialize_existing_ids() 

        self.shard_records.append(record)
        self.existing_ids.add(record["_id"])

        shard_key = f"{self.collection}_{self.shard_number}"
        self.index_data.setdefault(shard_key, []).append(record["_id"])

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
        with BytesIO() as buf:
            buf.write(msgpack.packb(self.index_data, use_bin_type=True))
            buf.seek(0)
            blob_client.upload_blob(buf, overwrite=True)

    def flush_logs(self):
        blob_client = self.container_client.get_blob_client(self.logs_filename)
        with BytesIO() as buf:
            buf.write(msgpack.packb(self.logs_data, use_bin_type=True))
            buf.seek(0)
            blob_client.upload_blob(buf, overwrite=True)