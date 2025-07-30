
# CAMS NCP Client

## Description

CAMS NCP Client is a Python package for interfacing with the CAMS NCP API.
With the CAMS NCP Client, you can manage measurements, forecasts, models, and file uploads/downloads related to CAMS (Copernicus Atmosphere Monitoring Service) data.


## Installation with pip

To install the package, you can use the following command:

```bash
pip install cams-ncp-client 
```

## Building from Source

Clone the repository:

```bash
git clone https://git.vito.be/scm/marvin-atmosys/cams_ncp_client.git
cd cams-ncp-client
```

Create the Python environment:

```bash
conda env create --prefix ./.venv --file conda_env.yml
conda activate ./.venv
```

Install the package:

```bash
poetry install
poetry install -E "full"
```


## Usage

The CamsNcpApiClient requires a base API URL to function. You can instantiate it as follows:

```python
from cams_ncp_client import CamsNcpApiClient

client = CamsNcpApiClient(base_url="https://193.190.137.75/api")
```

### Data retrieval

The CAMS NCP Client provides a consistent interface across different entity types (e.g., forecasts, observations, models, quantities, etc.) using a dual-method pattern for data retrieval:

**find_xxx() Methods**

These methods are API query functions that return results in paged Pydantic-typed objects (wrapped in a TableData[...] structure). They typically support:

Pagination (limit, offset)
Sorting (order_by)
Filtering using optional query parameters, such as:

 - station_name
 - quantity_name

 - start_time/end_time
 - model_name

 - aggregation, etc.

**Example find_forecasts():**

```python
from datetime import datetime
from cams_ncp_client import CamsNcpApiClient

client = CamsNcpApiClient(base_url="https://193.190.137.75/api") 
result = client.forecast.find_forecasts(
    quantity_name="NO2",
    station_name="42N016",
    model_name="CAMS",
    base_time_start=datetime(2024, 1, 1),
    limit=100,
    offset=0
)
```

This returns a _TableData[ForecastHourly]_ object containing structured hourly forecast results.

Pagination gives fine control for handling large datasets.

**find_xxx_df() Methods**

These are wrapper methods that call the corresponding _find_xxx()_ method repeatedly across pages, aggregate the results,
and return the data as a Pandas DataFrame.

They are ideal for:

- Data analysis
- Visualization
- Exporting to CSV/Excel
- Integration with scientific workflows

**Example find_observations_df():**

```python
from datetime import datetime
from cams_ncp_client import CamsNcpApiClient

client = CamsNcpApiClient(base_url="https://193.190.137.75/api") 

df = client.observation.find_observations_df(
    station_name="42N016",
    quantity_name="PM10",
    start_time=datetime(2023, 1, 1),
    end_time=datetime(2023, 6, 1)
)
```

Internally calls find_observations() over multiple pages and returns a flat pandas.DataFrame.

| Feature          | `find_xxx()`                    | `find_xxx_df()`                       |
| ---------------- | ------------------------------- | ------------------------------------- |
| Returns          | `TableData[PydanticModel]`      | `pandas.DataFrame`                    |
| Paged API Access | Yes (manual `limit` + `offset`) | Yes (auto-pagination via `max_pages`) |
| Type Safety      | Strongly typed via Pydantic     | Standard DataFrame schema             |
| Use Case         | Low-level control, validation   | Analysis, plotting, quick insights    |


### Data Upload

The CAMS NCP Client also supports data submission to the API via various _create_xxx()_ methods.
These methods are used to upload new data entries such as forecasts, observations, models, stations, ...

**Uploading Forecasts example:**

To upload a list of hourly forecast records, use the ForecastClient.create_forecasts() method.
The method expects a list of ForecastHourly objects that match the API schema.

```python
from cams_ncp_client.client import CamsNcpApiClient
from cams_ncp_client.schemas.common import ForecastHourly
from datetime import datetime

client = CamsNcpApiClient(base_url="https://193.190.137.75/api")

forecast_data = [
    ForecastHourly(
        station_name="42N016",
        quantity_name="PM10",
        model_name="CAMS",
        base_time=datetime(2024, 5, 10, 0, 0),
        forecast_time=datetime(2024, 5, 11, 12, 0),
        value=15.3
    ),
    ForecastHourly(
        station_name="42N016",
        quantity_name="PM10",
        model_name="CAMS",
        base_time=datetime(2024, 5, 10, 0, 0),
        forecast_time=datetime(2024, 5, 11, 13, 0),
        value=16.7
    )
]

created_forecasts = client.forecast.create_forecasts(forecast_data)
print(f"Uploaded: {created_forecasts}.")

```

### Full API 

The full API documentation is available at [http://docs.marvin.vito.local/map/cams-ncp-client/](http://docs.marvin.vito.local/map/cams-ncp-client/).

## Contributing

If you want to contribute to this project, please follow the standard contributing guidelines and push your changes to a new branch in
https://git.vito.be/projects/MARVIN-ATMOSYS/repos/cams_ncp_client/browse

## Testing

This client code is automatically tested in the CAMS NCP API repository.
cfr: https://git.vito.be/projects/MARVIN-ATMOSYS/repos/ncp_be_cams_api/browse/test

## CI/CD

The CI/CD pipeline is fully automated using Jenkins. Pipeline details are defined in the `Jenkinsfile` located in the repository root.



### Updating the Package Version

To update the package version:

1. Tag the code with the new version number in the format `major.minor.fix`.
2. Push the tagged code to the appropriate branch.

### Pipeline Automation

The Jenkins pipeline is set up to automatically build and publish the Master branche to the PyPI server.

The Development and Master branches are automatically build and published to the Vito Artifactory (https://repo.vito.be/artifactory/api/pypi/marvin-projects-pypi-local).


## Contact

For questions or issues, please reach out to the project maintainers:

- **Roeland Maes**: [roeland.maes@vito.be](mailto:roeland.maes@vito.be)


## License

This project is licensed under the MIT License. See the `LICENSE.md` file for details.
