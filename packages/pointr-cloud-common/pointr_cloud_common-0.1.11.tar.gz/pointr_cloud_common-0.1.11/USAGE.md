# Pointr Cloud Commons Usage Guide

> ⚠️ This software is proprietary to Pointr Limited.  
> Use is permitted only by authorized individuals or organizations.  
> Access to API functionality requires credentials provided by Pointr. Unauthorized use is prohibited.

## Table of Contents

- [Installation](#installation)
- [Authentication](#authentication)
- [Basic Usage](#basic-usage)
- [Services Overview](#services-overview)
  - [V9ApiService](#v9apiservice)
  - [SiteApiService](#siteapiservice)
  - [BuildingApiService](#buildingapiservice)
  - [LevelApiService](#levelapiservice)
  - [ClientApiService](#clientapiservice)
  - [SdkApiService](#sdkapiservice)
- [Data Transfer Objects (DTOs)](#data-transfer-objects-dtos)
- [Error Handling](#error-handling)
- [Examples](#examples)
  - [Site Management](#site-management)
  - [Building Management](#building-management)
  - [Level Management](#level-management)
  - [SDK Configuration Management](#sdk-configuration-management)
  - [Token Management](#token-management)
- [Best Practices](#best-practices)

## Installation

### Using UV (Recommended)

```bash
uv pip install pointr-cloud-common
```

### Using pip

```bash
pip install pointr-cloud-common
```

## Authentication

The Pointr Cloud Commons library supports two authentication methods:

1. **Username and Password**: Provide your credentials when initializing the API service.
2. **Pre-authenticated Token**: If you already have a valid token, you can provide it directly.

```python
from pointr_cloud_common.api.v9 import V9ApiService

# Method 1: Username and Password
config = {
    "api_url": "https://api.example.com",
    "client_identifier": "your-client-id",
    "username": "your-username",
    "password": "your-password"
}

api_service = V9ApiService(config, user_email="your-email@example.com")

# Method 2: Pre-authenticated Token
api_service = V9ApiService(config, user_email="your-email@example.com", token="your-token")
```

## Basic Usage

Here's a simple example of using the Pointr Cloud Commons library to get client metadata and list sites:

```python
from pointr_cloud_common.api.v9 import V9ApiService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configuration
config = {
    "api_url": "https://api.example.com",
    "client_identifier": "your-client-id",
    "username": "your-username",
    "password": "your-password"
}

# Create the API service
api_service = V9ApiService(config)

# Get client metadata
client_metadata = api_service.get_client_metadata()
print(f"Client name: {client_metadata.name}")

# Get sites
sites = api_service.get_sites()
print(f"Found {len(sites)} sites:")
for site in sites:
    print(f"  - {site.name} (FID: {site.fid})")
```

## Services Overview

The Pointr Cloud Commons library is organized into several services, each responsible for a specific area of functionality.

### V9ApiService

The main service that provides access to all other services. It handles authentication and API requests.

**Methods:**

| Method          | Description                 | Parameters                                                                                                           | Returns              |
| --------------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------- |
| `__init__`      | Initialize the API service  | `config`: Configuration dictionary<br>`user_email`: Optional user email<br>`token`: Optional pre-authenticated token | -                    |
| `_get_token`    | Get an authentication token | -                                                                                                                    | Authentication token |
| `_make_request` | Make a request to the API   | `method`: HTTP method<br>`endpoint`: API endpoint<br>`json_data`: Optional JSON data                                 | API response         |

The `V9ApiService` also provides delegated methods for all other services, so you can call them directly from the main service instance.

### SiteApiService

Service for site-related API operations.

**Methods:**

| Method                   | Description                  | Parameters                                                                                          | Returns                    |
| ------------------------ | ---------------------------- | --------------------------------------------------------------------------------------------------- | -------------------------- |
| `get_sites`              | Get all sites for the client | -                                                                                                   | List of `SiteDTO` objects  |
| `get_site_by_fid`        | Get a site by its FID        | `site_fid`: Site FID                                                                                | `SiteDTO` object           |
| `create_site`            | Create a site                | `site`: `SiteDTO` object<br>`source_api_service`: Optional source API service                       | FID of the created site    |
| `update_site`            | Update a site                | `site_id`: Site ID<br>`site`: `SiteDTO` object<br>`source_api_service`: Optional source API service | FID of the updated site    |
| `update_site_extra_data` | Update site extra data       | `site_fid`: Site FID<br>`extra_data`: Extra data dictionary                                         | Boolean indicating success |

### BuildingApiService

Service for building-related API operations.

**Methods:**

| Method                       | Description                  | Parameters                                                                                                                                    | Returns                       |
| ---------------------------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| `get_buildings`              | Get all buildings for a site | `site_fid`: Site FID                                                                                                                          | List of `BuildingDTO` objects |
| `get_building_by_fid`        | Get a building by its FID    | `site_fid`: Site FID<br>`building_fid`: Building FID                                                                                          | `BuildingDTO` object          |
| `create_building`            | Create a building            | `site_fid`: Site FID<br>`building`: `BuildingDTO` object<br>`source_api_service`: Optional source API service                                 | FID of the created building   |
| `update_building`            | Update a building            | `site_fid`: Site FID<br>`building_fid`: Building FID<br>`building`: `BuildingDTO` object<br>`source_api_service`: Optional source API service | FID of the updated building   |
| `update_building_extra_data` | Update building extra data   | `site_fid`: Site FID<br>`building_fid`: Building FID<br>`extra_data`: Extra data dictionary                                                   | Boolean indicating success    |

### LevelApiService

Service for level-related API operations.

**Methods:**

| Method            | Description                   | Parameters                                                                                                     | Returns                    |
| ----------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------- |
| `get_levels`      | Get all levels for a building | `site_fid`: Site FID<br>`building_fid`: Building FID                                                           | List of `LevelDTO` objects |
| `get_level_by_id` | Get a level by its ID         | `site_fid`: Site FID<br>`building_fid`: Building FID<br>`level_id`: Level ID                                   | `LevelDTO` object          |
| `create_level`    | Create a level                | `site_fid`: Site FID<br>`building_fid`: Building FID<br>`level`: Level data dictionary                         | FID of the created level   |
| `update_level`    | Update a level                | `site_fid`: Site FID<br>`building_fid`: Building FID<br>`level_id`: Level ID<br>`level`: Level data dictionary | FID of the updated level   |
| `delete_level`    | Delete a level                | `site_fid`: Site FID<br>`building_fid`: Building FID<br>`level_id`: Level ID                                   | Boolean indicating success |

### ClientApiService

Service for client-related API operations.

**Methods:**

| Method                     | Description                      | Parameters                                                      | Returns                          |
| -------------------------- | -------------------------------- | --------------------------------------------------------------- | -------------------------------- |
| `get_client_metadata`      | Get metadata for the client      | -                                                               | `ClientMetadataDTO` object       |
| `update_client`            | Update a client                  | `client_id`: Client ID<br>`client_data`: Client data dictionary | Boolean indicating success       |
| `create_client`            | Create a client                  | `client_data`: Client data dictionary                           | Identifier of the created client |
| `get_client_gps_geofences` | Get GPS geofences for the client | -                                                               | List of GPS geofence features    |

### SdkApiService

Service for SDK configuration-related API operations.

**Methods:**

| Method                            | Description                           | Parameters                                                                                               | Returns                               |
| --------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| `get_client_sdk_config`           | Get SDK configurations for the client | -                                                                                                        | List of `SdkConfigurationDTO` objects |
| `get_site_sdk_config`             | Get SDK configurations for a site     | `site_fid`: Site FID                                                                                     | List of `SdkConfigurationDTO` objects |
| `get_building_sdk_config`         | Get SDK configurations for a building | `site_fid`: Site FID<br>`building_fid`: Building FID                                                     | List of `SdkConfigurationDTO` objects |
| `put_global_sdk_configurations`   | Update global SDK configurations      | `configs`: List of `SdkConfigurationDTO` objects                                                         | Boolean indicating success            |
| `put_site_sdk_configurations`     | Update site SDK configurations        | `site_fid`: Site FID<br>`configs`: List of `SdkConfigurationDTO` objects                                 | Boolean indicating success            |
| `put_building_sdk_configurations` | Update building SDK configurations    | `site_fid`: Site FID<br>`building_fid`: Building FID<br>`configs`: List of `SdkConfigurationDTO` objects | Boolean indicating success            |

## Data Transfer Objects (DTOs)

The Pointr Cloud Commons library uses Data Transfer Objects (DTOs) to represent data structures. Here are the main DTOs:

- **SiteDTO**: Represents a site
- **BuildingDTO**: Represents a building
- **LevelDTO**: Represents a level
- **ClientMetadataDTO**: Represents client metadata
- **SdkConfigurationDTO**: Represents an SDK configuration
- **CreateResponseDTO**: Represents a create response
- **GpsGeofenceDTO**: Represents a GPS geofence

Each DTO has methods for creating instances from API JSON data and converting instances to API JSON format.

## Error Handling

The Pointr Cloud Commons library uses the `V9ApiError` exception class for API-related errors. You should catch this exception when making API calls:

```python
from pointr_cloud_common.api.v9 import V9ApiService
from pointr_cloud_common.api.v9.base_service import V9ApiError

try:
    sites = api_service.get_sites()
    print(f"Found {len(sites)} sites")
except V9ApiError as e:
    print(f"API error: {str(e)}")
    if e.status_code:
        print(f"Status code: {e.status_code}")
    if e.response_text:
        print(f"Response: {e.response_text}")
```

## Examples

### Site Management

```python
from pointr_cloud_common.api.v9 import V9ApiService
from pointr_cloud_common.dto.v9 import SiteDTO

# Create the API service
config = {
    "api_url": "https://api.example.com",
    "client_identifier": "your-client-id",
    "username": "your-username",
    "password": "your-password"
}
api_service = V9ApiService(config)

# Get all sites
sites = api_service.get_sites()
print(f"Found {len(sites)} sites:")
for site in sites:
    print(f"  - {site.name} (FID: {site.fid})")

# Create a new site
new_site = SiteDTO(
    fid="new-site",
    name="New Test Site",
    typeCode="site-outline",
    extraData={
        "description": "A new test site",
        "address": "123 Test Street, Test City",
        "status": "active"
    }
)

new_site_fid = api_service.create_site(new_site)
print(f"Created new site with FID: {new_site_fid}")

# Get the new site
site = api_service.get_site_by_fid(new_site_fid)
print(f"Retrieved site: {site.name} (FID: {site.fid})")

# Update the site
site.name = "Updated Test Site"
site.extraData["status"] = "inactive"

api_service.update_site(site.fid, site)
print(f"Updated site: {site.name}")

# Update just the extra data
extra_data = {
    "description": "An updated test site",
    "address": "456 Test Avenue, Test City",
    "status": "active"
}

api_service.update_site_extra_data(site.fid, extra_data)
print(f"Updated site extra data")
```

### Building Management

```python
from pointr_cloud_common.api.v9 import V9ApiService
from pointr_cloud_common.dto.v9 import BuildingDTO

# Create the API service
config = {
    "api_url": "https://api.example.com",
    "client_identifier": "your-client-id",
    "username": "your-username",
    "password": "your-password"
}
api_service = V9ApiService(config)

# Get all buildings for a site
site_fid = "site-123"
buildings = api_service.get_buildings(site_fid)
print(f"Found {len(buildings)} buildings:")
for building in buildings:
    print(f"  - {building.name} (FID: {building.fid})")

# Create a new building
new_building = BuildingDTO(
    fid="new-building",
    name="New Test Building",
    typeCode="building-outline",
    sid=site_fid,
    extraData={
        "buildingType": "office",
        "floors": 5,
        "area": 10000
    }
)

new_building_fid = api_service.create_building(site_fid, new_building)
print(f"Created new building with FID: {new_building_fid}")

# Get the new building
building = api_service.get_building_by_fid(site_fid, new_building_fid)
print(f"Retrieved building: {building.name} (FID: {building.fid})")

# Update the building
building.name = "Updated Test Building"
building.extraData["floors"] = 6

api_service.update_building(site_fid, building.fid, building)
print(f"Updated building: {building.name}")

# Update just the extra data
extra_data = {
    "buildingType": "residential",
    "floors": 7,
    "area": 12000
}

api_service.update_building_extra_data(site_fid, building.fid, extra_data)
print(f"Updated building extra data")
```

### Level Management

```python
from pointr_cloud_common.api.v9 import V9ApiService

# Create the API service
config = {
    "api_url": "https://api.example.com",
    "client_identifier": "your-client-id",
    "username": "your-username",
    "password": "your-password"
}
api_service = V9ApiService(config)

# Get all levels for a building
site_fid = "site-123"
building_fid = "building-123"
levels = api_service.get_levels(site_fid, building_fid)
print(f"Found {len(levels)} levels:")
for level in levels:
    print(f"  - {level.name} (FID: {level.fid})")

# Create a new level
new_level = {
    "fid": "new-level",
    "name": "Floor 1",
    "typeCode": "level",
    "floorNumber": 1,
    "extra": {
        "height": 3.5
    }
}

new_level_fid = api_service.create_level(site_fid, building_fid, new_level)
print(f"Created new level with FID: {new_level_fid}")

# Get the new level
level = api_service.get_level_by_id(site_fid, building_fid, new_level_fid)
print(f"Retrieved level: {level.name} (FID: {level.fid})")

# Update the level
updated_level = {
    "fid": level.fid,
    "name": "Updated Floor 1",
    "typeCode": "level",
    "floorNumber": 1,
    "extra": {
        "height": 4.0
    }
}

api_service.update_level(site_fid, building_fid, level.fid, updated_level)
print(f"Updated level: {updated_level['name']}")

# Delete the level
api_service.delete_level(site_fid, building_fid, level.fid)
print(f"Deleted level: {level.fid}")
```

### SDK Configuration Management

```python
from pointr_cloud_common.api.v9 import V9ApiService
from pointr_cloud_common.dto.v9 import SdkConfigurationDTO

# Create the API service
config = {
    "api_url": "https://api.example.com",
    "client_identifier": "your-client-id",
    "username": "your-username",
    "password": "your-password"
}
api_service = V9ApiService(config)

# Get client SDK configurations
client_configs = api_service.get_client_sdk_config()
print(f"Found {len(client_configs)} client SDK configurations:")
for config in client_configs:
    print(f"  - {config.key}: {config.value}")

# Get site SDK configurations
site_fid = "site-123"
site_configs = api_service.get_site_sdk_config(site_fid)
print(f"Found {len(site_configs)} site SDK configurations:")
for config in site_configs:
    print(f"  - {config.key}: {config.value}")

# Get building SDK configurations
building_fid = "building-123"
building_configs = api_service.get_building_sdk_config(site_fid, building_fid)
print(f"Found {len(building_configs)} building SDK configurations:")
for config in building_configs:
    print(f"  - {config.key}: {config.value}")

# Update global SDK configurations
global_configs = [
    SdkConfigurationDTO(key="config1", value="value1"),
    SdkConfigurationDTO(key="config2", value=True),
    SdkConfigurationDTO(key="config3", value={"nestedKey": "nestedValue"})
]

api_service.put_global_sdk_configurations(global_configs)
print(f"Updated global SDK configurations")

# Update site SDK configurations
site_configs = [
    SdkConfigurationDTO(key="config1", value="site-value1", scope="site", scopeId=site_fid),
    SdkConfigurationDTO(key="config2", value=False, scope="site", scopeId=site_fid)
]

api_service.put_site_sdk_configurations(site_fid, site_configs)
print(f"Updated site SDK configurations")

# Update building SDK configurations
building_configs = [
    SdkConfigurationDTO(key="config1", value="building-value1", scope="building", scopeId=building_fid),
    SdkConfigurationDTO(key="config2", value=True, scope="building", scopeId=building_fid)
]

api_service.put_building_sdk_configurations(site_fid, building_fid, building_configs)
print(f"Updated building SDK configurations")
```

### Token Management

For long-running applications, you may want to manage tokens to avoid frequent authentication:

```python
from pointr_cloud_common.api.v9 import V9ApiService
from pointr_cloud_common.utils import get_access_token, refresh_access_token, is_token_valid
import json
import os

# Token file path
TOKEN_FILE = "token.json"

def load_token():
    """Load token from file."""
    if not os.path.exists(TOKEN_FILE):
        return None

    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading token: {str(e)}")
        return None

def save_token(token_data):
    """Save token to file."""
    try:
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f)
    except Exception as e:
        print(f"Error saving token: {str(e)}")

def get_valid_token(client_id, api_url, username, password):
    """Get a valid token, either from file or by authenticating."""
    # Try to load token from file
    token_data = load_token()

    # Check if token is valid
    if token_data and is_token_valid(token_data):
        print("Using existing token")
        return token_data["access_token"]

    # Try to refresh token
    if token_data and "refresh_token" in token_data:
        try:
            print("Refreshing token")
            token_data = refresh_access_token(client_id, api_url, token_data["refresh_token"])
            save_token(token_data)
            return token_data["access_token"]
        except Exception as e:
            print(f"Error refreshing token: {str(e)}")

    # Get new token
    print("Getting new token")
    token_data = get_access_token(client_id, api_url, username, password)
    save_token(token_data)
    return token_data["access_token"]

# Configuration
client_id = "your-client-id"
api_url = "https://api.example.com"
username = "your-username"
password = "your-password"

# Get a valid token
token = get_valid_token(client_id, api_url, username, password)

# Create the API service with the token
config = {
    "api_url": api_url,
    "client_identifier": client_id
}
api_service = V9ApiService(config, token=token)

# Use the API service
client_metadata = api_service.get_client_metadata()
print(f"Client name: {client_metadata.name}")
```

## Best Practices

1. **Error Handling**: Always wrap API calls in try-except blocks to catch `V9ApiError` exceptions.

2. **Logging**: Enable logging to help with debugging. The Pointr Cloud Commons library logs important information at various levels.

3. **Token Management**: For long-running applications, manage tokens to avoid frequent authentication. Use the token management utilities provided by the library.

4. **Resource Cleanup**: Close any resources you open, such as file handles.

5. **Pagination**: When retrieving large lists of items, be aware of pagination limits and handle them appropriately.

6. **Rate Limiting**: Be mindful of API rate limits and implement appropriate backoff strategies if needed.

7. **Environment Separation**: Use different configurations for different environments (development, testing, production).

8. **Security**: Keep your credentials secure and never hardcode them in your application code. Use environment variables or secure configuration files.

9. **Validation**: Validate input data before sending it to the API to avoid unnecessary API calls and errors.

10. **Caching**: Consider implementing caching for frequently accessed data to reduce API calls and improve performance.
