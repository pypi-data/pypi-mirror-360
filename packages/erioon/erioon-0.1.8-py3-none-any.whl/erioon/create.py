# Copyright 2025-present Erioon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Visit www.erioon.com/dev-docs for more information about the python SDK

import uuid
from erioon.functions import (
    create_msgpack_file,
    update_index_file_insert,
    calculate_shard_number,
    async_log,
    is_duplicate_id
)

# INSERT ONE RECORD
def handle_insert_one(user_id_cont, database, collection, record, container_url):
    """
    Insert a single record into the collection.

    - If no '_id' provided, generate a new UUID.
    - If provided '_id' is duplicate, generate a new one and update the record.
    - Create or append the record in a shard file.
    - Update index.json to map the record to the appropriate shard.
    - Log success or errors asynchronously.

    Args:
        user_id_cont: User identifier.
        database: Database name.
        collection: Collection name.
        record: Dict representing the record to insert.
        container_url: Container SAS URL.

    Returns:
        Tuple (response dict, status code) indicating success or failure.
    """
    try:
        if "_id" not in record or not record["_id"]:
            record["_id"] = str(uuid.uuid4())

        rec_id = record["_id"]

        if is_duplicate_id(user_id_cont, database, collection, rec_id, container_url):
            new_id = str(uuid.uuid4())
            record["_id"] = new_id
            rec_id = new_id
            msg = f"Record inserted successfully in {collection} with a new _id {rec_id} because the provided _id was already present."
        else:
            msg = f"Record inserted successfully in {collection} with _id {rec_id}"

        async_log(user_id_cont, database, collection, "POST", "SUCCESS", msg, 1, container_url)

        create_msgpack_file(user_id_cont, database, collection, record, container_url)

        shard_number = calculate_shard_number(user_id_cont, database, collection, container_url)
        update_index_file_insert(user_id_cont, database, collection, rec_id, shard_number, container_url)

        return {"status": "OK", "message": msg, "record": record}, 200

    except Exception as e:
        error_msg = f"An error occurred during insert in {collection}: {str(e)}"
        async_log(user_id_cont, database, collection,"POST", "ERROR", error_msg, 1, container_url)
        return {"status": "KO", "message": "Failed to insert record.", "error": str(e)}, 500

# INSERT MANY RECORDS
def handle_insert_many(user_id_cont, database, collection, data, container_url):
    """
    Insert multiple records in bulk.

    - `data` is a list of dicts, each representing a record.
    - For each record:
      - Ensure it has a unique _id (generate new UUID if missing or duplicate).
      - Write the record to the appropriate shard.
      - Update index.json with _id to shard mapping.
    - Log the batch insert operation with details.
    - Return aggregate success or failure response.

    Args:
        user_id_cont: User identifier.
        database: Database name.
        collection: Collection name.
        data: List of record dicts.
        container_url: Container SAS URL.

    Returns:
        Tuple (response dict, status code) with summary of insert results.
    """
    insert_results = []
    count = len(data)

    try:
        for record in data:
            if "_id" not in record or not record["_id"]:
                record["_id"] = str(uuid.uuid4())

            rec_id = record["_id"]

            if is_duplicate_id(user_id_cont, database, collection, rec_id, container_url):
                new_id = str(uuid.uuid4())
                record["_id"] = new_id
                rec_id = new_id
                msg = f"Inserted with new _id {rec_id} (original _id was already present)."
            else:
                msg = f"Inserted with _id {rec_id}."

            create_msgpack_file(user_id_cont, database, collection, record, container_url)

            shard_number = calculate_shard_number(user_id_cont, database, collection, container_url)
            update_index_file_insert(
                user_id_cont, database, collection, rec_id, shard_number, container_url
            )

            insert_results.append({"_id": rec_id, "message": msg})

        async_log(user_id_cont, database, collection, "POST", "SUCCESS", insert_results, count, container_url)
        return {"success": "Records inserted successfully", "details": insert_results}, 200

    except Exception as e:
        general_error_msg = f"Unexpected error during bulk insert: {str(e)}"
        async_log(user_id_cont, database, collection, "POST", "ERROR", general_error_msg, 1, container_url)
        return {"status": "KO", "message": general_error_msg}, 500
