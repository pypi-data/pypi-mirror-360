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

import json
import io
import msgpack
from azure.storage.blob import ContainerClient
from erioon.functions import update_index_file_delete, check_nested_key, async_log

# DELETE ONE RECORD
def handle_delete_one(user_id, db_id, coll_id, data_to_delete, container_url):
    """
    Delete a single record from a collection.

    The record can be identified either by the unique '_id' field or by a nested key-value pair.

    Args:
        user_id: Identifier of the user performing the operation.
        db_id: Database ID containing the collection.
        coll_id: Collection ID.
        data_to_delete: Dictionary containing either '_id' or key-value pair to match.
        container_url: SAS URL pointing to the storage container.

    Returns:
        A tuple (response dict, status code) indicating success or failure.
    """
    if "_id" in data_to_delete:
        record_id = data_to_delete["_id"]
        return handle_delete_with_id(user_id, db_id, coll_id, record_id, container_url)
    else:
        return handle_delete_without_id(user_id, db_id, coll_id, data_to_delete, container_url)

# DELETE RECORD USING ID FILTER
def handle_delete_with_id(user_id, db_id, coll_id, record_id, container_url):
    """
    Delete a record exactly matching the given '_id'.

    Steps:
    - Parse container URL and create a ContainerClient.
    - Load the index.json file which maps shards to record IDs.
    - Locate the shard containing the target record_id.
    - Remove the record from the shard data.
    - Repack and upload the updated shard if record found.
    - Update index.json to reflect deletion.
    - Log success or errors asynchronously.

    Args:
        user_id, db_id, coll_id: Identifiers for user, database, and collection.
        record_id: The unique '_id' of the record to delete.
        container_url: Container SAS URL.

    Returns:
        Tuple (response dict, status code) indicating operation result.
    """
    
    container_client = ContainerClient.from_container_url(container_url)

    index_blob_client = container_client.get_blob_client(f"{db_id}/{coll_id}/index.json")

    if not index_blob_client.exists():
        return {"error": "Index file does not exist"}, 404

    index_data = json.loads(index_blob_client.download_blob().readall())
    shard_number = None

    for shard in index_data:
        for shard_key, ids in shard.items():
            if record_id in ids:
                shard_number = int(shard_key.split("_")[-1])
                break
        if shard_number:
            break

    if shard_number is None:
        async_log(user_id, db_id, coll_id, "DELETE", "ERROR", f"Record with _id {record_id} not found", 1, container_url)
        return {"error": f"Record with _id {record_id} not found"}, 404

    msgpack_blob_client = container_client.get_blob_client(f"{db_id}/{coll_id}/{coll_id}_{shard_number}.msgpack")

    try:
        msgpack_data = msgpack_blob_client.download_blob().readall()
        with io.BytesIO(msgpack_data) as buffer:
            records = []
            original_length = 0

            unpacked_data = msgpack.unpackb(buffer.read(), raw=False)
            if isinstance(unpacked_data, list):
                for record in unpacked_data:
                    original_length += 1
                    if record.get("_id") == record_id:
                        continue
                    records.append(record)

            if len(records) < original_length:
                with io.BytesIO() as out_file:
                    packed_data = msgpack.packb(records)
                    out_file.write(packed_data)
                    out_file.seek(0)
                    msgpack_blob_client.upload_blob(out_file, overwrite=True)

                update_index_file_delete(user_id, db_id, coll_id, record_id, shard_number, container_url)
                async_log(user_id, db_id, coll_id, "DELETE", "SUCCESS", f"Record with _id {record_id} deleted successfully", 1, container_url)
                return {"success": f"Record with _id {record_id} deleted successfully"}, 200
            else:
                async_log(user_id, db_id, coll_id, "DELETE", "ERROR", f"Record with _id {record_id} not found in shard", 1, container_url)
                return {"error": f"Record with _id {record_id} not found in shard"}, 404

    except Exception as e:
        async_log(user_id, db_id, coll_id, "DELETE", "ERROR", f"Error deleting record {record_id}: {str(e)}", 1, container_url)
        return {"error": f"Error deleting record {record_id}: {str(e)}"}, 500

# DELETE RECORD USING KEY FILTER
def handle_delete_without_id(user_id, db_id, coll_id, data_to_delete, container_url):
    """
    Delete a single record matching a nested key-value pair when '_id' is not provided.
    Behaves like MongoDB's delete_one: deletes only the first matched record.
    """
    container_client = ContainerClient.from_container_url(container_url)

    nested_key = list(data_to_delete.keys())[0]
    key, value = nested_key, data_to_delete[nested_key]

    directory_path = f"{db_id}/{coll_id}/"
    blob_list = container_client.list_blobs(name_starts_with=directory_path)

    for blob in blob_list:
        if blob.name.endswith(".msgpack"):
            try:
                blob_client = container_client.get_blob_client(blob.name)
                msgpack_data = blob_client.download_blob().readall()

                with io.BytesIO(msgpack_data) as buffer:
                    unpacked_data = msgpack.unpackb(buffer.read(), raw=False)
                    if isinstance(unpacked_data, list):
                        for record in unpacked_data:
                            if check_nested_key(record, key, value):
                                delete_response, status = handle_delete_with_id(user_id, db_id, coll_id, record["_id"], container_url)
                                if status == 200:
                                    return {"success": f"Record with _id {record['_id']} deleted successfully"}, 200
                                else:
                                    return delete_response, status
            except Exception as e:
                continue

    async_log(user_id, db_id, coll_id, "DELETE", "ERROR", f"No matching record found for key-value pair {key}:{value}", 1, container_url)
    return {"error": f"No matching record found for the specified key-value pair {key}:{value}"}, 404

# DELETE MULTIPLE RECORDS
def handle_delete_many(user_id, db_id, coll_id, data_to_delete_list, container_url, batch_size=10):
    """
    Delete multiple records from a collection.

    Supports a mix of deletions by '_id' and by key-value pair filters.
    Processes deletions in batches for performance and error isolation.

    Args:
        user_id: Identifier of the user making the request.
        db_id: The database identifier.
        coll_id: The collection identifier.
        data_to_delete_list: List of dictionaries representing deletion filters (must contain either '_id' or a key-value pair).
        container_url: Container SAS URL.
        batch_size: Number of deletions to process per batch.

    Returns:
        Tuple (response dict, status code). The response includes a summary of successes and failures.
    """
    
    batch_results = []

    for i in range(0, len(data_to_delete_list), batch_size):
        batch = data_to_delete_list[i : i + batch_size]

        ids_to_delete = [d["_id"] for d in batch if "_id" in d]
        non_id_queries = [d for d in batch if "_id" not in d]

        batch_success = []
        batch_errors = []

        if ids_to_delete:
            results = handle_delete_many_with_id(user_id, db_id, coll_id, ids_to_delete, container_url)
            for data_to_delete, (response, status_code) in zip([{"_id": rid} for rid in ids_to_delete], results):
                if 200 <= status_code < 300:
                    batch_success.append({
                        "delete_query": data_to_delete,
                        "message": response.get("success", "Record deleted successfully"),
                    })
                else:
                    batch_errors.append({
                        "delete_query": data_to_delete,
                        "error": response.get("error", f"Failed to delete record - Status code {status_code}"),
                    })

        if non_id_queries:
            deleted_results, errors = handle_delete_many_without_id(user_id, db_id, coll_id, non_id_queries, container_url)

            for res in deleted_results:
                batch_success.append({
                    "delete_query": res["query"],
                    "message": "Records deleted successfully",
                })

            for err in errors:
                batch_errors.append({
                    "delete_query": err["query"],
                    "error": err.get("error", "Unknown error"),
                })

        batch_results.append({
            "queries": len(batch),
            "success": batch_success,
            "errors": batch_errors,
        })

    total_success = sum(len(batch["success"]) for batch in batch_results)
    total_errors = sum(len(batch["errors"]) for batch in batch_results)

    if total_errors == 0:
        return {
            "success": f"Selected records deleted successfully",
            "details": batch_results,
            "total_deleted": total_success,
        }, 200
    elif total_success > 0:
        return {
            "warning": "Partial success deleting selected records",
            "details": batch_results,
            "total_deleted": total_success,
            "total_errors": total_errors,
        }, 207
    else:
        return {
            "error": "Error deleting selected records",
            "details": batch_results,
        }, 500

# DELETE MULTIPLE RECORDS WITH ID FILTER
def handle_delete_many_with_id(user_id, db_id, coll_id, record_ids, container_url):
    """
    Delete multiple records by their '_id' values.

    Args:
        user_id: User identifier.
        db_id: Database identifier.
        coll_id: Collection identifier.
        record_ids: List of '_id' values of records to delete.
        container_url: Container SAS URL.

    Returns:
        List of tuples (response dict, status code) for each deletion attempt.
    """
    
    results = []
    for record_id in record_ids:
        resp, status = handle_delete_with_id(user_id, db_id, coll_id, record_id, container_url)
        results.append((resp, status))
    return results

# DELETE MULTIPLE RECORDS WITH KEY FILTER
def handle_delete_many_without_id(user_id, db_id, coll_id, queries, container_url):
    """
    Delete multiple records that match key-value queries across all shards.

    For each query in the list, it finds all records matching the key-value condition
    and deletes them.

    Args:
        user_id: ID of the user performing the operation.
        db_id: Database ID containing the collection.
        coll_id: Collection ID.
        queries: List of dictionaries containing key-value match conditions.
        container_url: Container SAS URL.

    Returns:
        Tuple of:
            - deleted_results (list): List of queries that resulted in deletion.
            - errors (list): List of dictionaries containing error details for failed deletions.
    """
    
    container_client = ContainerClient.from_container_url(container_url)
    deleted_results = []
    errors = []

    directory_path = f"{db_id}/{coll_id}/"
    blob_list = list(container_client.list_blobs(name_starts_with=directory_path))

    for query in queries:
        key = list(query.keys())[0]
        value = query[key]
        deleted_any = False
        for blob in blob_list:
            if blob.name.endswith(".msgpack"):
                try:
                    blob_client = container_client.get_blob_client(blob.name)
                    msgpack_data = blob_client.download_blob().readall()

                    with io.BytesIO(msgpack_data) as buffer:
                        records = msgpack.unpackb(buffer.read(), raw=False)
                        if not isinstance(records, list):
                            continue
                        new_records = []
                        deleted_in_blob = False
                        for record in records:
                            if check_nested_key(record, key, value):
                                deleted_in_blob = True
                                deleted_any = True
                            else:
                                new_records.append(record)

                        if deleted_in_blob:
                            with io.BytesIO() as out_file:
                                out_file.write(msgpack.packb(new_records))
                                out_file.seek(0)
                                blob_client.upload_blob(out_file, overwrite=True)

                            deleted_ids = [r["_id"] for r in records if check_nested_key(r, key, value)]
                            shard_number = int(blob.name.split("_")[-1].split(".")[0])
                            for rid in deleted_ids:
                                update_index_file_delete(user_id, db_id, coll_id, rid, shard_number, container_url)
                                async_log(user_id, db_id, coll_id, "DELETE", "SUCCESS", f"Record with _id {rid} deleted successfully", 1, container_url)

                except Exception as e:
                    errors.append({"query": query, "error": str(e)})

        if deleted_any:
            deleted_results.append({"query": query, "status": "deleted"})
        else:
            errors.append({"query": query, "error": "No matching records found"})

    return deleted_results, errors