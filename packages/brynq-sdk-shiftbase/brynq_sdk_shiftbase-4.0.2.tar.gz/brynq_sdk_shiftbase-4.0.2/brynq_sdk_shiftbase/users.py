from typing import Dict, Optional, List, Any
import json
import pandas as pd
import re
from .schemas.users import UserSchema, UsersGroupSchema, UserCreateSchema, UserUpdateSchema
from brynq_sdk_functions import Functions

class Users:
    """
    Handles all User related operations in Shiftbase
    """
    def __init__(self, shiftbase):
        self.shiftbase = shiftbase
        self.uri = "users"

    def get(self,
            active: Optional[str] = None,
            allow_hidden: Optional[str] = None,
            department_id: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves all users from Shiftbase.

        Endpoint: GET https://api.shiftbase.com/api/users

        Notes:
            - It will only return users that are part of departments you have access to.
            - Depending on permissions, more user information may be available.

        Args:
            active (str, optional): '1' to fetch only active users, '0' to fetch only inactive users
            allow_hidden (str, optional): Set to any value to include hidden users
            department_id (str, optional): Filter on department ID

        Returns:
            pd.DataFrame: Users data

        Raises:
            ValueError: If parameters are invalid or user data fails validation
            requests.HTTPError: If the API request fails
        """
        # Validate parameters
        if active is not None and active not in ['0', '1']:
            raise ValueError("active must be '0' or '1'")

        if department_id is not None and not re.match(r"^[0-9]+$", department_id):
            raise ValueError("department_id must contain only digits")

        # Prepare query parameters
        params = {}
        if active is not None:
            params["active"] = active
        if allow_hidden is not None:
            params["allow_hidden"] = allow_hidden
        if department_id is not None:
            params["department_id"] = department_id

        # Make the request
        response_data = self.shiftbase.get(self.uri, params)

        if not response_data:
            return pd.DataFrame()

        # Validate with Functions.validate_pydantic_data
        try:
            valid_data, invalid_data = Functions.validate_pydantic_data(response_data, UserSchema)
            if len(invalid_data) > 0:
                raise ValueError(f"Invalid user data: {len(invalid_data)} records failed validation")

            if len(valid_data) > 0:
                df_users = pd.json_normalize([entry["User"] for entry in valid_data])
                df_users["team_ids"] = [[t.get("id") for t in entry.get("Team", [])] for entry in valid_data]
                df_users["group_ids"] = [[g.get("group_id") for g in entry.get("UsersGroup", [])] for entry in valid_data]
                return df_users
            return pd.DataFrame()
        except Exception as e:
            raise ValueError(f"Invalid user data: {str(e)}")

    def get_by_id(self, identifier: str) -> pd.DataFrame:
        """
        Retrieves a specific user by its ID or email.

        Endpoint: GET https://api.shiftbase.com/api/users/{identifier}

        Notes:
            - It will only return users that are part of departments you have access to.
            - Required permissions: View user details, View own profile, Edit own profile

        Args:
            identifier (str): A user ID or an email address

        Returns:
            pd.DataFrame: User details as single row DataFrame

        Raises:
            ValueError: If identifier is invalid or user data fails validation
            requests.HTTPError:
                - 404: User not found
                - 403: Unauthorized access
        """
        # Validate identifier
        if not identifier:
            raise ValueError("identifier cannot be empty")

        # Construct the endpoint URL
        endpoint = f"{self.uri}/{identifier}"

        try:
            # Make the request
            response_data = self.shiftbase.get(endpoint)

            # Validate with Functions.validate_pydantic_data

            valid_data, invalid_data = Functions.validate_pydantic_data(response_data, UserSchema)
            if len(invalid_data) > 0:
                raise ValueError(f"Invalid user data: {len(invalid_data)} records failed validation")

            if len(valid_data) > 0:
                df_users = pd.json_normalize([entry["User"] for entry in valid_data])
                df_users["team_ids"] = [[t.get("id") for t in entry.get("Team", [])] for entry in valid_data]
                df_users["group_ids"] = [[g.get("group_id") for g in entry.get("UsersGroup", [])] for entry in
                                         valid_data]
                return df_users
            return pd.DataFrame()
        except Exception as e:
            if "404" in str(e):
                raise ValueError(f"User with identifier {identifier} not found.")
            if "403" in str(e):
                raise ValueError("Unauthorized access: You don't have permission to view this user.")
            raise


    def create(self, data: Dict) -> Dict:
        """
        Creates a new user in Shiftbase.

        Args:
            data (Dict): Must be of format:
                {
                    "User": { ...validated user fields... },
                    "Team": [...],
                    "UsersGroup": [...],
                    "Contract": [...],
                    "Skill": [...]
                }

        Returns:
            Dict: Response from Shiftbase API

        Raises:
            ValueError: On validation issues
            requests.HTTPError: On API response error
        """
        # Validate the "User" section against the schema
        try:
            user_data = data.get("User", {})
            valid_data, invalid_data = Functions.validate_pydantic_data(data=user_data, schema=UserCreateSchema)
            if invalid_data:
                raise ValueError(f"Invalid user data: {invalid_data}")
        except Exception as e:
            raise ValueError(f"Invalid user data: {str(e)}")

        # Use the first (and only) validated user
        validated_user = valid_data[0]

        # Strip None values
        cleaned_user = {k: v for k, v in validated_user.items() if v is not None}

        # Build request payload
        request_payload = {
            "User": cleaned_user
        }

        # Attach any optional sections
        for key in ["Team", "UsersGroup", "Contract", "Skill"]:
            if key in data and data[key]:
                request_payload[key] = data[key]

        # Serialize request body with proper date handling
        request_body_json = json.dumps(request_payload, default=self.shiftbase.datetime_converter)

        # Execute request
        response = self.shiftbase.session.post(
            f"{self.shiftbase.base_url}{self.uri}",
            data=request_body_json,
            headers={"Content-Type": "application/json"}
        )

        # Raise any errors and return response
        response.raise_for_status()
        
        # Return the response JSON
        return response.json()

    def update(self, identifier: str, data: Dict) -> Dict:
        """
        Updates an existing user in Shiftbase.

        Calls the API endpoint: PUT https://api.shiftbase.com/api/users/{identifier}

        Args:
            identifier (str): A user ID or an email address
            data (Dict): Dictionary containing the user data to update.
                Must match the UserUpdateSchema structure.

        Returns:
            Dict: Response from the API containing the updated user details.

        Raises:
            ValueError: If the data fails validation or if the update fails
            requests.HTTPError: If the API returns a non-successful status
                - 400: Bad request or invalid parameters
                - 403: Missing required permission(s) - Need 'Edit users' or 'Edit own profile'
                - 404: User not found
                - 422: Unprocessable entity (e.g., validation failed)
        """
        # Validate identifier
        if not identifier:
            raise ValueError("identifier cannot be empty")

        # Validate input data against the schema
        try:
            valid_data, invalid_data = Functions.validate_pydantic_data(data=data, schema=UserUpdateSchema)
            if invalid_data:
                raise ValueError(f"Invalid user data: {invalid_data}")
        except Exception as e:
            raise ValueError(f"Invalid user data: {str(e)}")

        # Prepare request body - filter out None values
        request_body = {k: v for k, v in valid_data[0].items() if v is not None}

        # Serialize request body with proper date handling
        request_body_json = json.dumps(request_body, default=self.shiftbase.datetime_converter)

        # Make PUT request
        endpoint = f"{self.uri}/{identifier}"
        response = self.shiftbase.session.put(
            f"{self.shiftbase.base_url}{endpoint}", 
            data=request_body_json,
            headers={"Content-Type": "application/json"}
        )

        # Raise exception if the request failed
        response.raise_for_status()

        # Return the response JSON
        return response.json()

    def deactivate(self, identifier: str) -> Dict:
        """
        Deactivates a user in Shiftbase.

        This will disable the user from logging in but won't delete the user data completely.

        Calls the API endpoint: DELETE https://api.shiftbase.com/api/users/{identifier}

        Args:
            identifier (str): A user ID or an email address

        Returns:
            Dict: Response from the API confirming the deactivation.

        Raises:
            ValueError: If identifier is invalid
            requests.HTTPError: If the API returns a non-successful status
                - 403: Missing required permission(s) - Need 'Delete users'
                - 404: User not found
        """
        # Validate identifier
        if not identifier:
            raise ValueError("identifier cannot be empty")

        # Make DELETE request
        endpoint = f"{self.uri}/{identifier}"
        response = self.shiftbase.session.delete(f"{self.shiftbase.base_url}{endpoint}")

        # Raise exception if the request failed
        response.raise_for_status()

        # Return the response JSON
        return response.json()

    def activate(self, identifier: str) -> Dict:
        """
        (Re)activates a user in Shiftbase.

        This will enable a previously deactivated user to login again.

        Calls the API endpoint: PUT https://api.shiftbase.com/api/users/{identifier}/activate

        Args:
            identifier (str): A user ID or an email address

        Returns:
            Dict: Response from the API confirming the activation.

        Raises:
            ValueError: If identifier is invalid
            requests.HTTPError: If the API returns a non-successful status
                - 403: Missing required permission(s) - Need 'Activate users'
                - 404: User not found
        """
        # Validate identifier
        if not identifier:
            raise ValueError("identifier cannot be empty")

        # Make PUT request
        endpoint = f"{self.uri}/{identifier}/activate"
        response = self.shiftbase.session.put(f"{self.shiftbase.base_url}{endpoint}")

        # Raise exception if the request failed
        response.raise_for_status()

        # Return the response JSON
        return response.json()

    def anonymize(self, identifier: str) -> Dict:
        """
        Anonymizes a user's data in Shiftbase.

        This will anonymize the data of inactive employees.
        The user must be inactive (deactivated) before they can be anonymized.

        Calls the API endpoint: DELETE https://api.shiftbase.com/api/users/{identifier}/anonymize

        Args:
            identifier (str): A user ID or an email address

        Returns:
            Dict: Response from the API confirming the anonymization.

        Raises:
            ValueError: If identifier is invalid
            requests.HTTPError: If the API returns a non-successful status
                - 403: Missing required permission(s) - Need 'Delete users'
                - 404: User not found
                - 422: User is still active (must be deactivated first)
        """
        # Validate identifier
        if not identifier:
            raise ValueError("identifier cannot be empty")

        # Make DELETE request
        endpoint = f"{self.uri}/{identifier}/anonymize"
        response = self.shiftbase.session.delete(f"{self.shiftbase.base_url}{endpoint}")

        # Raise exception if the request failed
        response.raise_for_status()

        # Return the response JSON
        return response.json()
