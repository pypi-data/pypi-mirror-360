# Pointr Cloud Commons [![PyPI version](https://badge.fury.io/py/pointr-cloud-common.svg)](https://badge.fury.io/py/pointr-cloud-common) [![Python Versions](https://img.shields.io/pypi/pyversions/pointr-cloud-common.svg)](https://pypi.org/project/pointr-cloud-common/)

A Python package for interacting with Pointr Cloud APIs, providing services for managing sites, buildings, levels, and SDK configurations.

## For Users

If you're looking to use this library, please refer to the [Usage Guide](./USAGE.md) for detailed instructions and examples.

## For Developers

This section is for developers who want to contribute to the Pointr Cloud Commons library.

### Development Setup

1. Clone the repository:

```bash
git clone https://github.com/pointrlabs/ptr-swdel-internal-util-automation
cd PointrCloudCommon
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies using UV:

```bash
uv pip install -e ".[dev]"
```

### Project Structure

```
pointr-cloud-common/
├── src/                 # Source code
│   └── pointr_cloud_common/
│       ├── __init__.py  # Package initialization
│       ├── api/         # API services
│       │   ├── __init__.py
│       │   ├── common/  # Common API functionality
│       │   ├── v8/      # V8 API services
│       │   └── v9/      # V9 API services
│       ├── dto/         # Data Transfer Objects
│       │   ├── __init__.py
│       │   ├── common/  # Common DTOs
│       │   ├── v8/      # V8 DTOs
│       │   └── v9/      # V9 DTOs
│       ├── utils/       # Utility functions
│       │   └── __init__.py
│       └── helpers/     # Helper functions
│           └── __init__.py
├── tests/               # Test suite
│   ├── __init__.py
│   ├── test_dto/       # DTO tests
│   └── test_utils/     # Utility tests
├── pyproject.toml       # Project configuration
├── README.md            # This file
├── USAGE.md             # User guide
└── LICENSE-PROPRIETARY.md # License file
```

### Key Components

#### API Services

The library is organized into several services, each responsible for a specific area of functionality:

- **V9ApiService**: The main service for V9 API that provides access to all other V9 services. It handles authentication and API requests.
- **SiteApiService**: Service for site-related API operations.
- **BuildingApiService**: Service for building-related API operations.
- **LevelApiService**: Service for level-related API operations.
- **ClientApiService**: Service for client-related API operations.
- **SdkApiService**: Service for SDK configuration-related API operations.

#### Data Transfer Objects (DTOs)

DTOs are used to represent data structures:

- **SiteDTO**: Represents a site
- **BuildingDTO**: Represents a building
- **LevelDTO**: Represents a level
- **ClientMetadataDTO**: Represents client metadata
- **SdkConfigurationDTO**: Represents an SDK configuration
- **CreateResponseDTO**: Represents a create response
- **GpsGeofenceDTO**: Represents a GPS geofence

### Testing

The library uses pytest for testing. To run the tests:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=pointr_cloud_common
```

To generate a coverage report:

```bash
pytest --cov=pointr_cloud_common --cov-report=html
```

### Adding New Features

1. **Create a new branch**:

```bash
git checkout -b feature/your-feature-name
```

2. **Implement your changes**:

   - Add new services in the appropriate `api/` directory
   - Add new DTOs in the appropriate `dto/` directory
   - Add utility functions in the `utils/` directory
   - Add helper functions in the `helpers/` directory

3. **Add tests**:

   - Add unit tests in the `tests/` directory
   - Ensure all new code is covered by tests

4. **Update documentation**:

   - Update the user guide in `USAGE.md`

5. **Submit a pull request**:
   - Push your branch to the repository
   - Create a pull request with a clear description of your changes

### Code Style

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. We recommend using tools like `flake8` and `black` to ensure code quality:

```bash
# Check code style
flake8 src tests

# Format code
black src tests
```

### Documentation Guidelines

- Use docstrings for all modules, classes, and functions
- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings
- Keep the user guide up-to-date with any changes
- Add examples for new features

### Release Process

1. **Update version**:

   - Update the version in `pyproject.toml`
   - Update the version in `src/pointr_cloud_common/__init__.py`

2. **Update changelog**:

   - Add a new section to the changelog with the new version
   - List all changes, new features, bug fixes, etc.

3. **Create a release branch**:

```bash
git checkout -b release/vX.Y.Z
```

4. **Build and test the package**:

```bash
python -m build
uv pip install dist/pointr_cloud_common-X.Y.Z-py3-none-any.whl
# Run tests to ensure the package works
```

5. **Submit a pull request**:

   - Push your branch to the repository
   - Create a pull request with a clear description of the release

6. **Deployment**:
   - The package is deployed via a manual workflow in the deployment repository
   - Contact the DevOps team to trigger the deployment workflow after your PR is merged
   - The workflow will handle building, testing, and publishing the package to the internal PyPI server
   - For public releases, additional approval is required

### Continuous Integration

This project uses GitHub Actions for continuous integration. The CI pipeline runs on every pull request and includes:

- Running tests
- Checking code style
- Building the package
- Generating coverage reports

### License

This project is proprietary software and is the intellectual property of Pointr Limited. All rights reserved. This repository is intended for internal development and authorized external distribution only. Do not use, modify, or distribute this software unless you are an employee of Pointr or have received explicit permission to do so.

See [LICENSE-PROPRIETARY.md](./LICENSE-PROPRIETARY.md) for license details.

### Contact

If you have any questions or need help, please contact the maintainers:

- Serhat Gürgenyatağı - [serhat.gurgenyatagi@pointr.tech](mailto:serhat.gurgenyatagi@pointr.tech)
