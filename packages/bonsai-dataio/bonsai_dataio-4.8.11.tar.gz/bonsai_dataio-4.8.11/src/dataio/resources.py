from datetime import date, datetime, timedelta
from functools import cmp_to_key
from logging import getLogger
from pathlib import Path
from typing import List, Optional, Tuple, Union
import uuid

import classifications as classif
from currency_converter import CurrencyConverter, ECB_URL
import pandas as pd
from pint import DimensionalityError, UndefinedUnitError, UnitRegistry
import requests
import semantic_version

from dataio._classifications_helper import (
    filter_classifications,
    generate_classification_mapping,
    generate_classification_mapping_multi_column,
    increment_version,
)
from dataio.load import load, load_api
from dataio.save import save, save_to_api
from dataio.schemas import bonsai_api
from dataio.schemas.bonsai_api import *
from dataio.schemas.bonsai_api import DataResource

logger = getLogger("root")


def map_to_bonsai(row, column_names, mapping_dict):
    """Map values from two column_names together"""
    key = tuple(row[column_names])
    if all(key) and key in mapping_dict:
        return mapping_dict[key]  # Return the mapped bonsai values
    else:  # Keep original values if no mapping exists
        return key


def compare_version_strings(resource1: DataResource, resource2: DataResource):
    try:
        version1 = semantic_version.Version.coerce(resource1.data_version)
        version2 = semantic_version.Version.coerce(resource2.data_version)
        return (version1 > version2) - (version1 < version2)
    except ValueError:
        # Fallback to regular string comparison if semantic_version fails
        return (resource1.data_version > resource2.data_version) - (
            resource1.data_version < resource2.data_version
        )


class ResourceRepository:
    """
    Repository for managing data resources within a CSV file storage system.

    Attributes
    ----------
    db_path : Path
        Path to the directory containing the resource CSV file.
    table_name : str
        Name of the table (used for naming the CSV file).
    resources_list_path : Path
        Full path to the CSV file that stores resource information.
    schema : DataResource
        Schema used for resource data validation and storage.
    cache_dir: str
        cache_dir determinds the location of the cached data resources. Default: ./data_cache/

    Methods
    -------
    add_or_update_resource_list(resource: DataResource, **kwargs)
        Adds a new resource or updates an existing one in the repository.
    add_to_resource_list(resource: DataResource)
        Adds a new resource to the repository.
    update_resource_list(resource: DataResource)
        Updates an existing resource in the repository.
    get_resource_info(**filters)
        Retrieves resource information based on specified filters.
    add_from_dataframe(data, loc, task_name, task_relation, last_update, **kwargs)
        Adds resource information from a DataFrame.
    get_dataframe_for_task(name, **kwargs)
        Retrieves a DataFrame for a specific task.
    write_dataframe_for_task(data, name, **kwargs)
        Writes a DataFrame to the storage based on resource information.
    write_dataframe_for_resource(data, resource, overwrite)
        Validates and writes a DataFrame to the resource location. list_available_resources()
        Lists all available resources in the repository.
    comment_resource(resource, comment)
        Adds a comment to a resource and updates the repository.
    """

    def __init__(
        self,
        storage_method="local",
        db_path: Optional[str] = None,
        table_name: Optional[str] = "resources",
        API_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        cache_dir: str = "./data_cache/",
        MAX_CACHE_FILES: int = 3,
    ) -> None:
        """
        Initializes the ResourceRepository with the path to the database and table name.

        Parameters
        ----------
        db_path : str
            The file system path where the CSV database is located.
        table_name : str, optional
            The name of the table, default is 'resources'.
        storage_method: str, optional
            options are either "local" or "api" and this defines the default behavior which can be overwritten later in
            individual save/load methods
            if local, it uses a resources.csv file for loading/saving changes to files
            if api, it uses the versions table from the API to get this information
            if hybrid, it uses versions table from the API but stores results locally
        username : str, optional
            The user's username for authentication.
        password : str, optional
            The user's password for authentication.
        API_token : str, optional
            A pre-existing authentication token, if one is already known.
        """
        self.db_path = Path(db_path)
        self.table_name = table_name
        self.ureg = UnitRegistry()

        # Try this to make sure, that there are no SSL CERTIFICATE errors
        try:
            self.currency_converter = CurrencyConverter(
                ECB_URL, fallback_on_missing_rate=True
            )
        except:
            self.currency_converter = CurrencyConverter(fallback_on_missing_rate=True)

        if storage_method == "local":
            self.load_storage_method = "local"
            self.save_storage_method = "local"
        elif storage_method == "hybrid":
            self.load_storage_method = "api"
            self.save_storage_method = "local"
        elif storage_method == "api":
            self.load_storage_method = "api"
            self.save_storage_method = "api"
        else:
            raise ValueError("storage_method must be set to local, hybrid or api")

            # 2. Check parameters required for each storage method
        # Dictionary of basic required params
        required_params = {
            "local": ["db_path", "table_name"],
            "api": [],
            "hybrid": ["db_path", "table_name"],  # local + API
        }

        # Check "local" requirements (also "hybrid" because it needs local, too)
        if storage_method in required_params:
            for param_name in required_params[storage_method]:
                if not locals()[param_name]:
                    raise ValueError(
                        f"'{param_name}' must be set when storage_method='{storage_method}'."
                    )

        # 3. For "api" or "hybrid", check that EITHER API_token OR (username + password) is provided
        if storage_method in ["api", "hybrid"]:
            if not API_token and not (username and password):
                raise ValueError(
                    "When storage_method='{storage_method}', you must provide either:\n"
                    "  - API_token, OR\n"
                    "  - username AND password."
                )

        if db_path:
            if self.db_path.is_dir():
                self.resources_list_path = self.db_path / (self.table_name + ".csv")
            else:
                self.resources_list_path = self.db_path
            self.schema = DataResource

            csv_resource = DataResource(
                table_name,
                DataResource.__name__,
                location=str(self.resources_list_path),
            )
            self.resources_list_path = Path(csv_resource.location)
            self.root_dir = self.resources_list_path.parent.absolute()
            # Initialize CSV file if it does not exist
            if not self.resources_list_path.exists():
                if not self.resources_list_path.parent.exists():
                    self.resources_list_path.parent.mkdir(parents=True)
                self.schema.get_empty_dataframe().to_csv(
                    self.resources_list_path, index=False
                )

            self.available_resources = self.schema.get_empty_dataframe()
            if self.load_storage_method == "local":
                self._reload_resources_csv()

            # If freshly initialized, set to empty pd.DataFrame
            # --> will be empty dict if this is the case
            if isinstance(self.available_resources, dict):
                self.available_resources = self.schema.get_empty_dataframe()

        # API part
        self.base_url = "https://lca.aau.dk/api/"
        self.session = requests.Session()
        self.API_token = None  # Will be set if/when we successfully authenticate
        self.cache_dir = cache_dir
        self.MAX_CACHE_FILES = MAX_CACHE_FILES
        if storage_method in ["hybrid", "api"]:
            # If a token is already provided, set it. Otherwise, try to log in.
            if API_token:
                self._set_auth_headers(API_token)
                self.token = API_token
            elif username and password:
                # Attempt to create a token using provided credentials
                self.token = self._create_token(username, password)
                self._set_auth_headers(self.token)
            else:
                # No valid auth method provided
                raise ValueError("Must provide either a token or (username, password).")

    def _set_auth_headers(self, token: str) -> None:
        """
        Sets the session headers for authorization with the provided token.
        """
        self.session.headers.update({"Authorization": f"Token {token}"})

    def _determine_storage_method(self, override: str | None, is_write: bool) -> str:
        """
        Decide which storage method to use. If 'override' is provided,
        use that. Otherwise, use either load_storage_method or
        save_storage_method depending on is_write.
        """
        if override:
            return override
        return self.save_storage_method if is_write else self.load_storage_method


    def _reload_resources_csv(self):
        if not self.resources_list_path.exists():
            return  # Nothing to reload

        loaded = load(self.resources_list_path, {self.table_name: self.schema})

        # Handle both single return and dict return
        if isinstance(loaded, dict):
            self.available_resources = loaded.get(self.table_name, self.schema.get_empty_dataframe())
        else:
            self.available_resources = loaded

        self._resources_last_loaded = datetime.datetime.now()


    def _create_token(self, username: str, password: str) -> str:
        """
        Authenticate against the server to retrieve a token.

        This method depends on your specific auth endpoint. Adjust as needed.
        """
        endpoint = f"{self.base_url}user/token/"
        payload = {"email": username, "password": password}

        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()  # Raise an exception if the call wasn't successful
        except requests.exceptions.HTTPError as e:
            # You can also check specific status codes here if needed
            if response.status_code == 401:
                raise ValueError(
                    "Invalid credentials. Please check username/password."
                ) from e
            else:
                raise ValueError(
                    f"Failed to authenticate: {e}. Server responded with: {response.text}"
                ) from e

        data = response.json()
        if "token" not in data:
            raise ValueError(
                "Token not found in the response. Check your API endpoint."
            )
        return data["token"]

    def add_or_update_resource_list(
        self, resource: DataResource, storage_method: str | None = None, **kwargs
    ) -> str:
        """
        Adds a new resource to the repository or updates it if it already exists.

        Parameters
        ----------
        resource : DataResource
            The resource data to add or update.
        kwargs : dict
            Additional keyword arguments used for extended functionality.

        Returns
        -------
        str of the versions uuid
        """
        effective_method = self._determine_storage_method(storage_method, is_write=True)
        if effective_method == "local":
                self._reload_resources_csv()

        if self.resource_exists(resource, storage_method):
            version_uuid = self.update_resource_list(resource, storage_method)
        else:
            version_uuid = self.add_to_resource_list(resource, storage_method)

        return version_uuid

    def add_to_resource_list(
        self, resource: DataResource, storage_method: str | None = None
    ) -> None:
        """
        Appends a new resource to the repository.

        Parameters
        ----------
        resource : DataResource
            The resource data to add.

        Returns
        -------
        str of the generated uuid
        """
        effective_method = self._determine_storage_method(storage_method, is_write=True)
        generated_uuid = ""
        if effective_method == "local":
            # Append new record
            new_record = resource.to_pandas()
            self.available_resources = pd.concat(
                [self.available_resources, new_record], ignore_index=True
            )
            self.available_resources.to_csv(self.resources_list_path, index=False)
        elif effective_method == "api":
            # 1) Convert your Pydantic model to a dictionary
            resource_dict = resource.to_pandas().squeeze().to_dict()
            resource_dict = self._clear_resource_dict(resource_dict)
            if "api_endpoint" not in resource_dict or not resource_dict["api_endpoint"]:
                raise ValueError(
                    "No API endpoint was provided for early binding. "
                    "Please set 'resource.api_endpoint' before calling add_to_resource_list using API."
                )

            # 2) Generate a UUID for the required 'id' field (if the API needs it).
            generated_uuid = str(uuid.uuid4())
            resource_dict["id"] = generated_uuid

            # 3) POST the new resource to the API endpoint
            endpoint = f"{self.base_url}version-dataio/"
            try:
                response = self.session.post(endpoint, json=resource_dict)
                response.raise_for_status()  # Raises HTTPError if 4XX or 5XX
            except requests.exceptions.HTTPError as e:
                # Optionally tailor error handling based on status code
                if response.status_code == 400:
                    raise ValueError(f"Bad request: {response.text}") from e
                elif response.status_code == 401:
                    raise ValueError(
                        "Unauthorized. Check your token or credentials."
                    ) from e
                else:
                    raise ValueError(
                        f"Failed to add resource via API: {response.status_code} - {response.text}"
                    ) from e
        return generated_uuid

    def update_resource_list(
        self, resource: DataResource, storage_method: str | None = None
    ) -> None:
        """
        Updates an existing resource in the repository.

        Parameters
        ----------
        resource : DataResource
            The resource data to update.
        """
        effective_method = self._determine_storage_method(storage_method, is_write=True)

        if effective_method == "local":
            # Update existing local record
            resource_as_dict = resource.to_pandas().squeeze().to_dict()
            cleared_dict = self._clear_resource_dict(resource_as_dict)
            mask = pd.Series([True] * len(self.available_resources))
            for key, value in cleared_dict.items():
                if not value:
                    continue
                mask &= self.available_resources[key] == value

            try:
                row_index = self.available_resources[mask].index[0]
                for key, value in resource_as_dict.items():
                    self.available_resources.at[row_index, key] = value

                self.available_resources.to_csv(self.resources_list_path, index=False)
                return ""
            except IndexError:
                # No matching row found — fallback to add
                logger.warning("No matching row found for update; appending new resource instead.")
                return self.add_to_resource_list(resource, storage_method)

        # -- API MODE --
        elif effective_method == "api":
            # 1. Build filters (same logic as resource_exists) to locate the resource
            filters = {
                "name": resource.name,
                "task_name": resource.task_name,
                "stage": resource.stage,
                "data_version": resource.data_version,
                "code_version": resource.code_version,
            }
            filters = {k: v for k, v in filters.items() if v is not None}

            # 2. Retrieve the existing resource from the API
            #    Since resource_exists was True, we assume exactly one match.
            list_endpoint = f"{self.base_url}version-dataio/"
            resp = self.session.get(list_endpoint, params=filters)
            resp.raise_for_status()

            # We assume exactly one matching resource; take the first item
            results = resp.json()
            matching_resource = results[0]  # no checks for "multiple" or "none"

            # 3. Extract the ID (guaranteed to exist if resource_exists was True)
            resource_id = matching_resource["id"]

            # 4. Prepare the data for PATCH
            resource_as_dict = resource.to_pandas().squeeze().to_dict()
            update_data = self._clear_resource_dict(resource_as_dict)
            # Optionally include 'id' if your API needs it in the request body:
            update_data["id"] = resource_id

            # 5. Perform the PATCH request
            update_endpoint = f"{list_endpoint}{resource_id}/"
            try:
                patch_resp = self.session.patch(update_endpoint, json=update_data)
                patch_resp.raise_for_status()
            except requests.exceptions.RequestException as e:
                # Convert to ValueError so your test sees a ValueError
                raise ValueError(f"Failed to update resource via API: {e}")

            return resource_id

        else:
            raise ValueError("Invalid storage method. Must be either 'local' or 'api'.")

    def _clear_resource_dict(self, resource_dict: dict):
        resource_dict = resource_dict.copy()
        # drop unnecessary fields
        if "comment" in resource_dict:
            del resource_dict["comment"]
        if "created_by" in resource_dict:
            del resource_dict["created_by"]
        if "license" in resource_dict:
            del resource_dict["license"]
        if "last_update" in resource_dict:
            del resource_dict["last_update"]
        if "license_url" in resource_dict:
            del resource_dict["license_url"]
        if "dag_run_id" in resource_dict:
            del resource_dict["dag_run_id"]

        return resource_dict

    def resource_exists(
        self, resource: DataResource, storage_method: str | None = None
    ) -> bool:
        """
        Checks if the given resource already exists in the repository
        (locally or via the API).

        Returns
        -------
        bool
            - True if exactly one matching resource is found.
            - False if none are found.
        Raises
        ------
        ValueError
            If multiple matches are found or if an invalid storage method is set.
        """
        effective_method = self._determine_storage_method(storage_method, is_write=True)
        # Gather the relevant fields for filtering (removing fields like comment, dag_run_id, etc.)
        resource_as_dict = resource.to_pandas().squeeze().to_dict()
        cleared_dict = self._clear_resource_dict(resource_as_dict)

        if effective_method == "local":
            self._reload_resources_csv()
            try:
                result = self.get_resource_info(storage_method, **cleared_dict)
                if isinstance(result, list):
                    if len(result) > 1:
                        raise ValueError(
                            f"Multiple matching resources found in local storage for filters: {cleared_dict}."
                        )
                    return True
                return True
            except ValueError:
                return False

        # -- API MODE --
        elif effective_method == "api":
            # Build query parameters to find a matching resource by these fields
            filters = {
                "name": resource.name,
                "task_name": resource.task_name,
                "stage": resource.stage,
                "data_version": resource.data_version,
                "code_version": resource.code_version,
            }
            # Drop any None values from the filter
            filters = {k: v for k, v in filters.items() if v is not None}

            endpoint = f"{self.base_url}version-dataio/"
            try:
                response = self.session.get(endpoint, params=filters)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                # Cannot confirm existence if we fail to query the API
                raise ValueError(
                    f"Error querying the API for resource existence: {e}"
                ) from e

            results = response.json()

            if len(results) > 1:
                raise ValueError(
                    f"Multiple matching resources found in API for {filters}."
                )
            return len(results) == 1
        else:
            raise ValueError("Invalid storage method. Must be either 'local' or 'api'.")

    def get_latest_version(self, storage_method: str | None = None, **filters: dict):
        resources = self.get_resource_info(storage_method=storage_method, **filters)

        if not isinstance(resources, list):
            return resources

        if len(resources) > 1:
            resources = sorted(
                resources, key=cmp_to_key(compare_version_strings), reverse=True
            )

        return resources[0]

    def get_resource_info(
        self, storage_method: str | None = None, **filters: dict
    ) -> DataResource | List[DataResource]:
        """
        Retrieves resource information based on specified filters, optionally
        overriding the default storage method for this call.

        Parameters
        ----------
        storage_method : str or None
            Override for this call. If None, use self.load_storage_method.
            Valid values: 'local', 'api'.
        filters : dict
            Key-value pairs of attributes to filter the resources by.

        Returns
        -------
        DataResource or List[DataResource]
            Matches found, either a single or multiple.
        """
        # Determine the effective method (local or api)
        effective_method = self._determine_storage_method(
            storage_method, is_write=False
        )

        if effective_method == "local":
            if self.resources_list_path.exists():
                self._reload_resources_csv()
            mask = pd.Series(True, index=self.available_resources.index)

            for k, v in filters.items():
                if not v:
                    continue
                # Normalize both sides
                series = self.available_resources[k].astype(str).str.strip()
                value = str(v).strip()
                mask = mask & (series == value)
            result = self.available_resources[mask]

            if result.empty:
                raise ValueError(
                    f"No resource found with the provided filters: {filters}"
                )

            if len(result.index) > 1:
                results = []
                for _, row in result.iterrows():
                    results.append(self._row_to_data_resource(row))
                return results
            else:
                return self._row_to_data_resource(result.iloc[0])

        elif effective_method == "api":
            # -----------------------
            # API LOGIC
            # -----------------------
            # Remove None filters
            api_filters = {k: v for k, v in filters.items() if v is not None}
            endpoint = f"{self.base_url}version-dataio/"
            try:
                resp = self.session.get(endpoint, params=api_filters)
                resp.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise ValueError(
                    f"Error querying the API for resource info with filters={api_filters}: {e}"
                ) from e

            data = resp.json()

            if not data:
                # Empty list returned -> no matches
                raise ValueError(
                    f"No resource found with the provided filters: {filters}"
                )

            if len(data) == 1:
                # Exactly one match -> return single DataResource
                return self._api_dict_to_data_resource(data[0])
            else:
                # Multiple matches -> return a list of DataResource
                return [self._api_dict_to_data_resource(item) for item in data]

        else:
            raise ValueError("Invalid storage method. Must be either 'local' or 'api'.")

    def add_from_dataframe(
        self,
        data: pd.DataFrame,
        loc: Union[Path, str],
        task_name: str | None = None,
        task_relation: str = "output",
        last_update: date = date.today(),
        **kwargs,
    ) -> DataResource:
        res = DataResource.from_dataframe(
            data,
            loc,
            task_name,
            task_relation=task_relation,
            last_update=last_update,
            **kwargs,
        )
        self.add_or_update_to_list(res)
        return res

    def get_dataframe_for_task(
        self,
        name: str,
        storage_method: str | None = None,
        **kwargs,
    ) -> pd.DataFrame:

        effective_method = self._determine_storage_method(
            storage_method, is_write=False
        )

        resource = self.get_resource_info(
            name=name, storage_method=effective_method, **kwargs
        )
        assert not isinstance(resource, list), (
            "Provided information points to more than one resource. "
            "Please add more information to filter uniquely."
        )
        if effective_method == "local":
            return load(
                Path(resource.location),
                {Path(resource.location).stem: globals()[resource.schema_name]},
            )
        elif effective_method == "api":
            return load_api(
                self,
                resource,
                CACHE_DIR=self.cache_dir,
                MAX_CACHE_FILES=self.MAX_CACHE_FILES,
            )
        else:
            raise ValueError("Invalid storage method. Must be either 'local' or 'api'.")

    def get_dataframe_for_resource(
        self,
        res: DataResource,
        storage_method: str | None = None,
    ):
        effective_method = self._determine_storage_method(
            storage_method, is_write=False
        )
        if effective_method == "local":
            return load(
                Path(res.location),
                {Path(res.location).stem: globals()[res.schema_name]},
            )
        elif effective_method == "api":
            return load_api(
                self, res, self.cache_dir, MAX_CACHE_FILES=self.MAX_CACHE_FILES
            )
        else:
            raise ValueError("Invalid storage method. Must be either 'local' or 'api'.")

    def write_dataframe_for_task(
        self,
        data: pd.DataFrame,
        name: str,
        data_version: str,
        overwrite=True,
        append=False,
        storage_method: str | None = None,
        **kwargs,
    ):

        try:
            # make sure only relevant fields are used when getting already existing resource
            effective_method = self._determine_storage_method(storage_method, is_write=True)
            if effective_method == "local":
                self._reload_resources_csv()
            cleaned_kwargs = self._clear_resource_dict(kwargs)
            resource = self.get_resource_info(
                storage_method, name=name, **cleaned_kwargs
            )

            if isinstance(resource, list):
                raise IndexError(
                    "Resource information is ambiguous. Multiple resources match the given description. Please provide more parameters."
                )
            # update resource based on kwargs
            for key, value in kwargs.items():
                if key == "location":
                    resource.__setattr__("_location", value)
                else:
                    resource.__setattr__(key, value)
        except ValueError:
            resource = DataResource(
                name=name,
                data_version=data_version,
                root_location=self.root_dir,
                **kwargs,
            )

        resource.data_version = data_version
        self.write_dataframe_for_resource(
            data,
            resource,
            overwrite=overwrite,
            append=append,
            storage_method=storage_method,
        )

    def write_dataframe_for_resource(
        self,
        data: pd.DataFrame,
        resource: DataResource,
        overwrite=True,
        append=False,
        storage_method: str | None = None,
    ):
        effective_method = self._determine_storage_method(storage_method, is_write=True)
        schema = globals()[resource.schema_name]

        if (
            self.resource_exists(resource, storage_method)
            and not overwrite
            and not append
        ):
            raise FileExistsError
        if overwrite and overwrite == append:
            raise Exception(
                "Error in parameter: 'Overwrite' and 'append' flags cannot be set to True"
            )

        if effective_method == "local":
            save(
                data=data,
                name=resource.name,
                path=Path(resource.location),
                schema=schema,
                overwrite=overwrite,
                append=append,
            )
            self.add_or_update_resource_list(resource)
        elif effective_method == "api":
            # Use the JSON-based save_to_api
            save_to_api(
                data=data,
                resource=resource,
                schema=schema,
                overwrite=overwrite,
                append=append,
            )
            self.add_or_update_resource_list(resource)
        else:
            raise ValueError("Invalid storage method. Must be either 'local' or 'api'.")

    def list_available_resources(
        self, storage_method: str | None = None
    ) -> list[DataResource]:
        """
        Lists all available resources in the repository, either from local CSV or from
        the API, depending on the storage method.

        Parameters
        ----------
        storage_method : str | None
            Optional override for single-call usage ('local' or 'api'). If None,
            uses self.load_storage_method.

        Returns
        -------
        list[DataResource]
            A list of all DataResource items found.
        """
        effective_method = self._determine_storage_method(
            storage_method, is_write=False
        )

        if effective_method == "local":
            # ----------------------------
            # LOCAL LOGIC
            # ----------------------------
            self._reload_resources_csv()
            resources = [
                self._row_to_data_resource(row)
                for _, row in self.available_resources.iterrows()
            ]
            return resources

        elif effective_method == "api":
            # ----------------------------
            # API LOGIC
            # ----------------------------
            # 1) Fetch all versions from the API.
            endpoint = f"{self.base_url}/version-dataio/"

            try:
                resp = self.session.get(endpoint)
                resp.raise_for_status()
            except requests.RequestException as e:
                raise ValueError(
                    f"Failed to retrieve list of available resources from API: {e}"
                )

            # 2) Parse JSON. We assume the server returns a list of dictionaries.
            items = resp.json()  # e.g. [ {...}, {...}, ... ]
            if not isinstance(items, list):
                raise ValueError(
                    "Expected a list of resource objects from the API. Got something else."
                )

            # 3) Convert each dict item into a DataResource.
            resources = []
            for item in items:
                # Merge 'root_location' if needed
                item["root_location"] = self.root_dir
                # Create a new DataResource
                resource_obj = DataResource(**item)
                resources.append(resource_obj)

            return resources

        else:
            raise ValueError("Invalid storage method. Must be either 'local' or 'api'.")

    # TODO Needs API update
    def comment_resource(self, resource: DataResource, comment: str) -> DataResource:
        resource.append_comment(comment)
        self.add_or_update_resource_list(resource)
        return resource

    def _row_to_data_resource(self, row):
        args = {"root_location": self.root_dir, **row}
        return DataResource(**args)

    def _api_dict_to_data_resource(self, record: dict) -> DataResource:
        """
        Convert a JSON record from the API into a DataResource instance.
        Adjust field names if they differ in your API response.
        """
        # Optionally, add root_location if your DataResource expects that
        # e.g., record["root_location"] = self.root_dir
        return DataResource(**record)

    def valid_units(self):
        return set(self.ureg) | self.currency_converter.currencies

    def _get_currency_unit_and_year(self, unit: str) -> tuple[str, object]:
        # Extract base currency and year if unit specifies a historical year
        if unit[-4:].isdigit():
            base_currency = unit[:-4].upper()
            year = datetime.datetime(int(unit[-4:]), 1, 1)
        else:
            base_currency = unit.upper()
            year = None
        return base_currency, year

    def convert_units(
        self, data: pd.DataFrame, target_units: list[str]
    ) -> pd.DataFrame:
        """
        Converts values in the 'value' column of a DataFrame to the specified target units in the list.
        Units not listed in the target_units remain unchanged.

        Args:
            dataframe (pd.DataFrame): A DataFrame with 'unit' and 'value' columns.
            target_units (list): A list of target units to convert compatible units to.
                                 Example: ["kg", "J", "m"]

        Returns:
            pd.DataFrame: A DataFrame with the converted values and target units.
        """

        # Check if input DataFrame has required columns
        if "unit" not in data.columns or "value" not in data.columns:
            raise ValueError("The DataFrame must contain 'unit' and 'value' columns.")

        # Check for the 'year' column
        use_historical = "year" in data.columns

        # Create columns for converted values and units
        new_values = []
        new_units = []

        no_target_units = set()
        not_defined_units = set()

        sanitized_targets = []
        for target in target_units:
            if target in self.ureg:
                sanitized_targets.append(target)
            else:
                potential_currency, _ = self._get_currency_unit_and_year(target)

                if potential_currency in self.currency_converter.currencies:
                    sanitized_targets.append(target)
                else:
                    logger.warning(
                        f"Target unit {target} not defined, will be skipped when converting"
                    )

        for _, row in data.iterrows():
            # Parse the current value and unit
            current_value = row["value"]
            current_unit = row["unit"]

            if not current_unit in self.ureg:
                # potentially a currency!
                potential_currency, _ = self._get_currency_unit_and_year(current_unit)
                if not potential_currency in self.currency_converter.currencies:
                    not_defined_units.add(current_unit)
                    new_values.append(current_value)
                    new_units.append(current_unit)
                    continue

            # Initialize target unit as None
            target_unit = None
            target_currency = None

            # Find a matching target unit based on dimensionality
            for target in sanitized_targets:
                try:
                    if (
                        self.ureg.parse_units(current_unit).dimensionality
                        == self.ureg.parse_units(target).dimensionality
                    ):
                        target_unit = target
                        break
                except UndefinedUnitError:
                    # Handle currency conversion
                    base_currency, base_year = self._get_currency_unit_and_year(
                        current_unit
                    )
                    new_currency, new_year = self._get_currency_unit_and_year(target)

                    if (
                        base_currency in self.currency_converter.currencies
                        and new_currency in self.currency_converter.currencies
                    ):
                        target_currency = new_currency
                        break

            if target_unit:
                # Convert the value
                quantity = self.ureg.Quantity(current_value, current_unit)
                converted_quantity = quantity.to(target_unit)
                new_values.append(converted_quantity.magnitude)
                new_units.append(target_unit)

            elif target_currency and target_currency == current_unit:
                new_values.append(current_value)
                new_units.append(target_currency)

            elif target_currency:
                # Get the historical date from the 'year' column
                historical_date = None
                if use_historical:
                    year = row["year"]
                    historical_date = (
                        datetime.datetime(int(year), 1, 1)
                        if not pd.isnull(year)
                        else None
                    )

                # If a year is defined in the target or in base unit use that over year column
                target_date = new_year or base_year or historical_date
                # Use the historical date if available
                if new_year and base_year and new_year != base_year:
                    logger.warning(
                        f"Both base year and target year are defined for currency conversion. Converting between different years is currently not supported. The currency is converted, assuming the base year {new_year} for both values."
                    )

                if target_date:
                    converted_value = self.currency_converter.convert(
                        current_value, base_currency, target_currency, date=target_date
                    )
                else:
                    converted_value = self.currency_converter.convert(
                        current_value, base_currency, target_currency
                    )

                new_values.append(converted_value)
                new_units.append(target_currency)
            else:
                no_target_units.add(current_unit)
                new_values.append(current_value)
                new_units.append(current_unit)

        if not_defined_units:
            logger.warning(
                f"The following units could not be converted because they are not defined in the unit registry: {not_defined_units}"
            )

        if no_target_units:
            logger.warning(
                f"The following units could not be converted because for their dimensionality no target unit was defined: {no_target_units}"
            )

        data["unit"] = new_units
        data["value"] = new_values

        return data

    def convert_units_pandas(
        self, data: pd.DataFrame, target_units: list[str]
    ) -> pd.DataFrame:
        """
        Converts values in the 'value' column of a DataFrame to the specified target units in the list.
        Units not listed in the target_units remain unchanged.

        Args:
            dataframe (pd.DataFrame): A DataFrame with 'unit' and 'value' columns.
            target_units (list): A list of target units to convert compatible units to.
                                 Example: ["kg", "J", "m"]

        Returns:
            pd.DataFrame: A DataFrame with the converted values and target units.
        """

        # Check if input DataFrame has required columns
        if "unit" not in data.columns or "value" not in data.columns:
            raise ValueError("The DataFrame must contain 'unit' and 'value' columns.")

        # Create lists for converted values and units
        new_units = []
        multipliers = []

        no_target_units = set()
        not_defined_units = set()

        sanitized_targets = []
        for target in target_units:
            if target in self.ureg:
                sanitized_targets.append(target)
            else:
                potential_currency, _ = self._get_currency_unit_and_year(target)

                if potential_currency in self.currency_converter.currencies:
                    sanitized_targets.append(target)
                else:
                    logger.warning(
                        f"Target unit {target} not defined, will be skipped when converting"
                    )

        # Find the unique units and currencies for mapping.
        u_uniq = data["unit"].unique()

        currencies = pd.DataFrame(columns=["unit", "year"])
        for unit in u_uniq:
            # Check for currencies, and add a base_year to it if missing
            base_currency, base_year = self._get_currency_unit_and_year(unit)
            if base_currency in self.currency_converter.currencies:
                if "year" in data.columns:
                    currency_year = data.loc[data.unit == unit, ["unit", "year"]]
                    currency_year.drop_duplicates(inplace=True)
                    currency_year["year"] = currency_year["year"].apply(
                        lambda y: datetime.datetime(y, 1, 1)
                    )
                    currencies = pd.concat(
                        [currencies, currency_year], ignore_index=True
                    )
                else:
                    currencies.loc[len(currencies)] = [unit, base_year]
        u_uniq = list(set(u_uniq) - set(currencies["unit"]))

        # Find multipliers for units
        for current_unit in u_uniq:
            if current_unit in sanitized_targets + [""]:
                new_units.append(current_unit)
                multipliers.append(1)
                continue
            elif not current_unit in self.ureg:
                not_defined_units.add(current_unit)
                new_units.append(current_unit)
                multipliers.append(1)
                continue

            # Find a matching target unit based on dimensionality
            target_unit = None
            for target in sanitized_targets:
                try:
                    if (
                        self.ureg.parse_units(current_unit).dimensionality
                        == self.ureg.parse_units(target).dimensionality
                    ):
                        target_unit = target
                        break
                except UndefinedUnitError:
                    continue
            if target_unit:  # Get the conversion factor
                quantity = self.ureg.Quantity(1, current_unit)
                multipliers.append(quantity.to(target_unit).magnitude)
                new_units.append(target_unit)
            else:  # No target_unit found
                no_target_units.add(current_unit)
                multipliers.append(1)
                new_units.append(current_unit)

        # Find exchange rate for currencies
        currencies["multiplier"] = 1
        currencies["new_unit"] = None
        for ix, (currency, base_year, _, _) in currencies.iterrows():
            base_currency, currency_year = self._get_currency_unit_and_year(currency)
            target_currency = None

            for target in sanitized_targets:
                new_currency, new_year = self._get_currency_unit_and_year(target)
                if (
                    base_currency in self.currency_converter.currencies
                    and new_currency in self.currency_converter.currencies
                ):
                    target_currency = new_currency
                    break

            if target_currency and target_currency == base_currency:
                currencies.loc[ix, "new_unit"] = target_currency

            elif target_currency:
                # If a year is defined in the target or in base unit use that over year column
                target_date = new_year or currency_year or base_year
                # Use the historical date if available
                if new_year and currency_year and new_year != currency_year:
                    logger.warning(
                        f"Both base year and target year are defined for currency conversion. Converting between different years is currently not supported. The currency is converted, assuming the base year {new_year.year} for both values."
                    )

                if target_date:
                    exchange_rate = self.currency_converter.convert(
                        1, base_currency, target_currency, date=target_date
                    )
                else:
                    exchange_rate = self.currency_converter.convert(
                        1, base_currency, target_currency
                    )

                currencies.loc[ix, "multiplier"] = exchange_rate
                currencies.loc[ix, "new_unit"] = target_currency

            else:
                not_defined_units.add(currency)

        if not_defined_units:
            logger.warning(
                f"The following units could not be converted because they are not defined in the unit registry: {not_defined_units}"
            )
        if no_target_units:
            logger.warning(
                f"The following units could not be converted because for their dimensionality no target unit was defined: {no_target_units}"
            )

        # Combine new_units and currencies in a mapping_df
        mapping_df = pd.DataFrame(
            {"unit": u_uniq, "new_unit": new_units, "multiplier": multipliers}
        )
        mapping_df = pd.concat([mapping_df, currencies])

        # Merge and apply units without a year
        general_map = mapping_df[mapping_df["year"].isna()].drop(columns="year")
        converted_data = data.merge(general_map, how="left")

        mask_new = converted_data["new_unit"].notna()
        converted_data.loc[mask_new, "unit"] = converted_data["new_unit"]
        converted_data.loc[mask_new, "value"] *= converted_data["multiplier"]

        # Merge and apply currencies with a year
        specific_map = mapping_df[mapping_df["year"].notna()].copy()
        if specific_map.empty:
            return converted_data[data.columns]
        else:
            specific_map["year"] = specific_map["year"].dt.year  # Convert date to year
        converted_data = converted_data[data.columns].merge(specific_map, how="left")

        mask_new = converted_data["new_unit"].notna()
        converted_data.loc[mask_new, "unit"] = converted_data["new_unit"]
        converted_data.loc[mask_new, "value"] *= converted_data["multiplier"]

        return converted_data[data.columns]

    def group_and_sum(
        self, df, code_column: str, group_columns: list, values_to_sum: list | set
    ):
        """Grouping function to handle unit compatibility"""
        results = []
        for value in values_to_sum:
            group = df[df[code_column] == value].copy()
            if not group.empty:
                # Further group by all columns except 'Value' and 'Unit'
                grouped = group.groupby(group_columns, as_index=False)
                for _, sub_group in grouped:
                    try:
                        # Attempt to convert all values to the first unit in the subgroup
                        base_unit = sub_group["unit"].iloc[0]
                        sub_group["base_value"] = sub_group.apply(
                            lambda row: row["value"]
                            * self.ureg(row["unit"]).to(base_unit).magnitude,
                            axis=1,
                        )
                        # Sum the converted values
                        summed_value = sub_group["base_value"].sum()
                        result = sub_group.drop(columns="base_value").iloc[:1]
                        result["value"] = summed_value
                        result["unit"] = base_unit
                        results.append(result)
                    except DimensionalityError:
                        # If units are not compatible, append the rows as is
                        results.append(sub_group)
                    except UndefinedUnitError:
                        # If units are not found in pint, append the rows as is
                        results.append(sub_group)

        if results:  # Combine the summed and remaining data rows
            results += [df[~df[code_column].isin(list(values_to_sum))]]
            return pd.concat(results, ignore_index=True)
        else:  # Return the original DataFrame
            return df

    def convert_dataframe_to_bonsai_classification(
        self, data: pd.DataFrame, original_schema, units=None
    ) -> Tuple[pd.DataFrame, dict[str, set[str]]]:
        return self.convert_dataframe(
            data,
            original_schema,
            classifications=classif.core.get_bonsai_classification(),
            units=units,
        )

    def convert_dataframe(
        self,
        data: pd.DataFrame,
        original_schema,
        classifications: dict,
        units: list[str] | None = None,
    ) -> Tuple[pd.DataFrame, dict[str, set[str]]]:
        unmapped_values: dict[str, set[str]] = dict()

        # Check if the class exists and has the method you want to call
        if original_schema and hasattr(original_schema, "get_classification"):
            from_class = original_schema.get_classification()
        else:
            raise AttributeError(
                f"{original_schema} does not have a 'get_classification' method."
            )

        concordances = {}
        pair_wise_concs = {}
        classif_to_columns_name = {}

        def get_clean_classif_type(classif, column):
            classif_type = classif[column][1]
            if classif_type.endswith("_pair"):
                classif_type = classif_type[:-5]
            return classif_type

        for column_name, (classif_name, classif_type) in from_class.items():

            classif_type_name = classif_type
            category = classif_type
            if classif_type.endswith("_pair"):
                category = "flow"
                classif_type_name = classif_type[:-5]

            if not classif_type_name in classifications:
                logger.warning(
                    f"No target classification provided for column name {column_name} [{classif_type_name}]"
                )
                continue

            classif_to_columns_name[classif_type_name] = column_name

            try:
                concordance = classif.get_concordance(
                    classif_name, classifications[classif_type_name], category=category
                )
            except FileNotFoundError:
                logger.warning(f"Correspondence for {classif_name} to {classifications[classif_type_name]} not found. Skipping")
                continue


            # this is a pairwise concordance and needs to be treated specificly
            if {
                "activitytype_from",
                "flowobject_from",
                "activitytype_to",
                "flowobject_to",
            }.issubset(concordance.columns):
                from_pair: list[str] = []
                to_pair: list[str] = []
                this_classif_columns = []
                for name in concordance.columns:
                    if "_from" in name and not name.startswith("classification"):
                        from_pair.append(name)
                    elif "_to" in name and not name.startswith("classification"):
                        to_pair.append(name)
                    if classif_type_name in name:
                        this_classif_columns.append(name)

                pair_key = (tuple(from_pair), tuple(to_pair))
                if pair_key not in pair_wise_concs:
                    pair_wise_concs[pair_key] = concordance

                concordances[column_name] = concordance  # FIXME: why this?
            else:
                concordances[column_name] = concordance

        missing = set(data.columns) - set(concordances.keys())
        if any(missing):
            logger.debug(f"No concordance found for columns: {missing}.")

        for (from_columns, to_columns), concordance in pair_wise_concs.items():
            # Select all columns that start with 'tree_'
            tree_columns = list(from_columns + to_columns)

            # Filter rows where none of the selected columns have NaNs
            dropped_rows = concordance[concordance[tree_columns].isna().any(axis=1)]
            filtered_concordance = concordance.dropna(subset=tree_columns)

            column_names = [
                classif_to_columns_name[c.split("_")[0]] for c in from_columns
            ]
            classif_names = [c.split("_")[0] for c in from_columns]

            # save the left_over concordances for indidual mapping afterwards
            for column_name, from_column, to_column in zip(
                column_names, from_columns, to_columns
            ):
                concordances[column_name] = dropped_rows[
                    [from_column, to_column] + ["comment", "skos_uri", "accounttype"]
                ].copy()
            mapping_dict, many_to_one = generate_classification_mapping_multi_column(
                filtered_concordance, classif_names
            )

            # Step 2: Apply the mapping function to the DataFrame
            data[column_names] = data.apply(
                lambda row: pd.Series(map_to_bonsai(row, column_names, mapping_dict)),
                axis=1,
            )

        for column, concordance in concordances.items():
            if column not in data.columns:
                logger.info(
                    f"Skipping concordance {column} as there are no corresponding columns found for it"
                )
                continue  # Skip if the column doesn't exist in the dataframe

            unmapped_values[column] = set()

            # filter many to many correspondences since they can't be used
            # use the valid correspondences only
            using_regex = "regex" in from_class[column][0]

            filtered_correspondence = filter_classifications(
                concordance,
                data[column].unique(),
                get_clean_classif_type(from_class, column) + "_from",
                using_regex=using_regex,
            )

            # Generate and apply classification mapping
            mapping_dict, codes_to_be_summed = generate_classification_mapping(
                filtered_correspondence, get_clean_classif_type(from_class, column)
            )

            # Apply transformation with a lambda function that tracks unmapped values
            data[column] = data[column].apply(
                lambda x: (
                    mapping_dict[x]
                    if x in mapping_dict
                    else unmapped_values[column].add(x) or x
                )
            )

            if codes_to_be_summed:
                # Group by all columns except 'Value' and 'Unit'
                ignore_columns = ["value", "unit"]
                group_columns = [
                    col for col in data.columns if col not in ignore_columns
                ]

                # Apply the grouping and summing function
                data = self.group_and_sum(
                    data, column, group_columns, codes_to_be_summed
                )

            if unmapped_values[column]:
                logger.info(
                    f"Unmapped classifications in column {column}: "
                    + ", ".join(unmapped_values[column])
                )

        if units:
            data = self.convert_units(data, units)

        
        # Extract account_type from the concordance if it exists
        # FIXME: why is this using concordance directly if this is possibly unbound? why not do this in the
        # concpair table statement???
        if isinstance(concordance, pd.DataFrame) and "accounttype" in concordance.columns:
            logger.info("accounttype column in concpair table found")

            concordance = classif.get_concordance(
                classif_name, classifications[classif_type_name], category=category
            )

            # Function to extract the first code from a pipe-separated string
            def extract_first(value):
                return value.split("|")[0]

            # Apply extraction to df1
            data["activity_first"] = data["activity"].apply(extract_first)
            data["product_first"] = data["product"].apply(extract_first)

            # Initialize a list to store accounttypes
            accounttypes = []

            # Iterate through each row of df1 to find the corresponding accounttype
            for _, row in data.iterrows():
                # Check df2 for matching activity and product from either pair of columns
                activity = row["activity_first"]
                product = row["product_first"]

                # Check for matching in the first pair of columns in df2 (activitytype_from, flowobject_from)
                match_from = concordance[
                    (concordance["activitytype_from"] == activity)
                    & (concordance["flowobject_from"] == product)
                ]

                # Check for matching in the second pair of columns in df2 (activitytpe_to, flowobject_to)
                match_to = concordance[
                    (concordance["activitytype_to"] == activity)
                    & (concordance["flowobject_to"] == product)
                ]

                # If no exact match found, check for activity-only mappings (flowobject empty)
                match_activity_only_from = concordance[
                    (concordance["activitytype_from"] == activity)
                    & (pd.isna(concordance["flowobject_from"]))
                ]
                match_activity_only_to = concordance[
                    (concordance["activitytype_to"] == activity)
                    & (pd.isna(concordance["flowobject_to"]))
                ]

                # Prioritize matching with both activity and product
                if not match_from.empty:
                    accounttypes.append(match_from.iloc[0]["accounttype"])
                elif not match_to.empty:
                    accounttypes.append(match_to.iloc[0]["accounttype"])
                # If no match, check for activity-only mappings
                elif not match_activity_only_from.empty:
                    accounttypes.append(match_activity_only_from.iloc[0]["accounttype"])
                elif not match_activity_only_to.empty:
                    accounttypes.append(match_activity_only_to.iloc[0]["accounttype"])
                else:
                    accounttypes.append(None)

            # Add the accounttype to df1
            data["accounttype"] = accounttypes

            # Drop the intermediate columns
            data = data.drop(columns=["activity_first", "product_first"])

        return data, unmapped_values

    def load_with_classification(
        self,
        classifications: dict,
        units: list[str] | None = None,
        storage_method: str | None = None,
        **kwargs,
    ) -> Tuple[pd.DataFrame, dict[str, set[str]]]:
        """
        loads data with a certain classificaiton. for the selected fields. Rows that can't
        be automatically transformed are ignored and returned as is
        """
        # Retrieve resource information and dataframe for task
        resource_info = self.get_resource_info(storage_method, **kwargs)
        data = self.get_dataframe_for_task(storage_method=storage_method, **kwargs)

        schema_name = resource_info.schema_name
        schema_class = getattr(bonsai_api, schema_name, None)

        return self.convert_dataframe(
            data,
            original_schema=schema_class,
            classifications=classifications,
            units=units,
        )

    def load_with_bonsai_classification(
        self, storage_method: str | None = None, **kwargs
    ) -> Tuple[pd.DataFrame, dict[str, set[str]]]:
        """
        This method loads the selected data based on kwargs with the default BONSAI classifications.
        The default classifications for BONSAI are the following:

        location: ISO3
        flowobject: BONSAI
        """

        return self.load_with_classification(
            classifications=classif.core.get_bonsai_classification(),
            storage_method=storage_method,
            **kwargs,
        )

    def harmonize_with_resource(
        self, dataframe, storage_method: str | None = None,overwrite=True, **kwargs
    ):
        # Load the base DataFrame
        base_df = self.get_dataframe_for_task(storage_method=storage_method, **kwargs)

        # Define the columns to check for overlaps
        overlap_columns = ["time", "location", "product", "unit"]

        # Ensure the overlap columns exist in both DataFrames
        for column in overlap_columns:
            if column not in base_df.columns or column not in dataframe.columns:
                raise ValueError(
                    f"Column '{column}' is missing in one of the DataFrames"
                )

        # Concatenate the DataFrames
        combined_df = pd.concat([base_df, dataframe], ignore_index=True)

        # Identify duplicate rows based on overlap columns
        duplicates = combined_df[
            combined_df.duplicated(subset=overlap_columns, keep=False)
        ]
        # TODO handle duplicates somehow. Based on source and uncertainty

        # # Find and display duplicate pairs
        # duplicate_pairs = (
        #     combined_df.groupby(overlap_columns).size().reset_index(name="Count")
        # )
        # duplicate_pairs = duplicate_pairs[duplicate_pairs["Count"] > 1]
        #
        # # Display all duplicate pairs
        # if not duplicate_pairs.empty:
        #     print("Duplicate Pairs:")
        #     print(duplicate_pairs)
        # else:
        #     print("No duplicate pairs found.")

        unique_df = combined_df.drop_duplicates(subset=overlap_columns, keep=False)
        # TODO check if there is any changes if not then no need to create a new resource

        resource = self.get_latest_version(storage_method, **kwargs)
        resource.data_version = increment_version(resource.data_version)
        self.write_dataframe_for_resource(
            unique_df, resource,overwrite=overwrite, storage_method=storage_method
        )


class CSVResourceRepository:
    def __new__(
        cls, db_path: str, table_name: str = "resources", **kwargs
    ) -> ResourceRepository:
        """
        On creation, return a ResourceRepository initialized with 'local' storage.
        """
        return ResourceRepository(
            storage_method="local", db_path=db_path, table_name=table_name, **kwargs
        )
