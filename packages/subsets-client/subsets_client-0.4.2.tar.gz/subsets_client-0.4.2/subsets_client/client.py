import json
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

from .exceptions import AuthenticationError, SubsetsError, UploadError


class SubsetsClient:
    def __init__(self, api_key: str, base_url: str = "https://api.subsets.io"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _request(
        self, method: str, endpoint: str, **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        url = urljoin(self.base_url, endpoint)
        
        # Merge headers
        headers = kwargs.pop("headers", {})
        headers.update(self.headers)
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            
            try:
                error_data = e.response.json()
                message = error_data.get("detail", str(e))
            except (json.JSONDecodeError, AttributeError):
                message = str(e)
                
            raise SubsetsError(f"API request failed: {message}")
        except requests.exceptions.RequestException as e:
            raise SubsetsError(f"Request failed: {str(e)}")

    def create_dataset(self, dataset_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dataset with the given configuration."""
        return self._request("POST", "/datasets", json=dataset_config)

    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """Get dataset metadata by ID."""
        return self._request("GET", f"/datasets/{dataset_id}")

    def delete_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """Delete a dataset and all its data."""
        return self._request("DELETE", f"/datasets/{dataset_id}")

    def list_datasets(
        self, 
        limit: int = 10, 
        offset: int = 0,
        q: Optional[str] = None,
        license: Optional[str] = None,
        source: Optional[str] = None,
        owner: Optional[str] = None,
        min_score: Optional[float] = None,
        detailed: bool = False
    ) -> Dict[str, Any]:
        """List datasets with optional search and filtering.
        
        Args:
            limit: Maximum number of datasets to return (1-100, default: 10)
            offset: Number of datasets to skip for pagination (default: 0)
            q: Search query for semantic search
            license: Filter by license type
            source: Filter by source ID
            owner: Filter by owner ID
            min_score: Minimum relevance score threshold for search results (0.0-2.0)
            detailed: Include detailed summary data (column stats, query metrics, etc.)
            
        Returns:
            Dictionary containing 'datasets' list and 'total' count
        """
        params = {"limit": limit, "offset": offset, "detailed": detailed}
        if q:
            params["q"] = q
        if license:
            params["license"] = license
        if source:
            params["source"] = source
        if owner:
            params["owner"] = owner
        if min_score is not None:
            params["min_score"] = min_score
            
        response = self._request("GET", "/datasets", params=params)
        # Always return the full response object with datasets and total
        return response

    def add_data(self, dataset_id: str, table: pa.Table, validate_schema: bool = True) -> Dict[str, Any]:
        """Add data to a dataset using a PyArrow Table."""
        # Optionally validate schema matches dataset
        if validate_schema:
            dataset = self.get_dataset(dataset_id)
            expected_columns = {col["id"]: col["type"] for col in dataset["columns"]}
            
            # Check all required columns exist
            table_columns = set(table.column_names)
            expected_cols = set(expected_columns.keys())
            missing = expected_cols - table_columns
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
            
            # Basic type validation
            for col_name in expected_columns:
                if col_name in table_columns:
                    actual_type = str(table.field(col_name).type)
                    expected_type = expected_columns[col_name]
                    # Simple mapping - can be expanded
                    type_map = {
                        "integer": ["int32", "int64"],
                        "long": ["int64"],
                        "float": ["float32"],
                        "double": ["float64", "double"],
                        "string": ["string", "utf8"],
                        "boolean": ["bool"],
                        "date": ["date32", "date64"],
                        "timestamp": ["timestamp"]
                    }
                    if expected_type in type_map:
                        valid_types = type_map[expected_type]
                        if not any(t in actual_type for t in valid_types):
                            raise ValueError(
                                f"Column '{col_name}' has type {actual_type} "
                                f"but expected {expected_type}"
                            )
        
        import io
        buffer = io.BytesIO()
        pq.write_table(table, buffer)
        parquet_bytes = buffer.getvalue()
        filename = "data.parquet"
        
        # Request presigned URL
        upload_request = {
            "filename": filename,
            "file_size": len(parquet_bytes)
        }
        
        response = self._request("POST", f"/data/{dataset_id}", json=upload_request)
        upload_url = response["upload_url"]
        
        # Upload to presigned URL
        upload_response = requests.put(
            upload_url,
            data=parquet_bytes,
            headers={"Content-Type": "application/octet-stream"}
        )
        upload_response.raise_for_status()
        
        return {
            "status": "success",
            "dataset_id": dataset_id,
            "bytes_uploaded": len(parquet_bytes)
        }

    def delete_data(self, dataset_id: str) -> Dict[str, Any]:
        """Delete all data from a dataset (keeps the dataset definition)."""
        return self._request("DELETE", f"/data/{dataset_id}")

    def query(self, sql: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a DataFrame."""
        response = self._request("POST", "/sql/query", json={"query": sql})
        return pd.DataFrame(response['data'])