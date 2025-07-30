import math
from datetime import datetime, date
from enum import Enum
from typing import Literal, List, Optional, Generic, TypeVar, Sequence, Iterator

from pydantic import BaseModel, field_validator
from pydantic import field_serializer

T = TypeVar("T")


class Aggregation(str, Enum):
    DA = "da"
    M1 = "m1"
    M8 = "m8"


class TableData(BaseModel, Generic[T], Sequence[T]):
    """
    A generic class to represent paginated data from an API response.
    """
    data: List[T]
    offset: int
    limit: int
    total: int

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index: int) -> T:
        return self.data[index]

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)


class Quantity(BaseModel):
    """
    Represents a quantity of a measurement.

    Attributes:
        id: Unique identifier for the quantity.
        name: Unique name of the quantity (e.g. PM10, PM2.5, O3, etc.).
        description: Description of the quantity.
        unit: Unit of measurement (e.g. µg/m³) Only one unit is allowed.
        min_value: Minimum value for the quantity.
        max_value: Maximum value for the quantity.
    """
    id: Optional[int] = None
    name: str  # Unique name of the quantity
    description: str
    unit: str
    min_value: float
    max_value: float

    @field_validator("name")
    @classmethod
    def lowercase_name(cls, v: str) -> str:
        return v.lower().strip()


StationType = Literal["BACKGROUND", "INDUSTRIAL", "TRAFFIC", "UNKNOWN"]
AreaType = Literal["URBAN", "SUBURBAN", "RURAL", "UNKNOWN"]


class MeasuringStation(BaseModel):
    """
    Represents a measuring station.
    """

    id: Optional[int] = None
    name: str  # Unique name of the Station (e.g. local code)
    eoi_code: Optional[str] = None # Unique EOI code of  Station
    description: str
    lat: float
    lon: float
    altitude: Optional[float]
    station_type: StationType = "UNKNOWN"
    area_type: AreaType = "UNKNOWN"
    quantities: List[str] = []

    meta_data: Optional[dict] = None


ModelType = Literal["OVL", "CAMS", "MOS", "ISSEP", "CHIMERE", "DA"]

class ForecastModel(BaseModel):
    """
    Represents a forecast model.
    """

    id: Optional[int] = None
    name: str   # Unique name of the model
    description: str

    model_type: ModelType
    model_subtype: Optional[str] = None  # e.g. RNN (for ModelType OVL), DEHh, EMEP, SILAM or ... (for ModelType CAMS)

    color: str


class ObservationHourly(BaseModel):
    """
    Represents an hourly observation.
    """
    id: Optional[int] = None
    result_time: datetime

    station_name: str
    quantity_name: str

    value: Optional[float]

    meta_data: Optional[dict] = None

    @field_serializer("value")
    def serialize_value(self, value: Optional[float]) -> Optional[float]:
        if value is not None and math.isnan(value):
            return None
        return value


class ObservationAgg(BaseModel):
    """
    Represents a daily aggregated observation.  The API currently only supports daily averages. (da), daily maximum (m1) and daily maximum of the 8-hour moving mean (m8)
    """

    # TODO rename to result_date ?
    result_time: date

    station_name: str
    quantity_name: str

    value: Optional[float]

    aggregation: str

    @field_serializer("value")
    def serialize_value(self, value: Optional[float]) -> Optional[float]:
        if value is not None and math.isnan(value):
            return None
        return value


class ForecastHourly(BaseModel):
    """
    Represents an hourly forecast. (for station, model and quantity)
    """

    id: Optional[int] = None
    base_time: datetime
    forecast_time: datetime

    station_name: str
    quantity_name: str
    model_name: str

    horizon_hours: Optional[int] = None
    horizon_days: Optional[int] = None

    value: Optional[float] = None

    meta_data: Optional[dict] = None

    @field_serializer("value")
    def serialize_value(self, value: Optional[float]) -> Optional[float]:
        if value is not None and math.isnan(value):
            return None
        return value


class ForecastAgg(BaseModel):
    """
    Represents a daily aggregated forecast. The API currently only supports daily averages. (da), daily maximum (m1) and daily maximum of the 8-hour moving mean (m8)
    """
    id: Optional[int] = None
    base_time: datetime
    forecast_time: date

    station_name: str
    quantity_name: str
    model_name: str
    aggregation: str

    horizon_days: Optional[int] = None

    value: Optional[float] = None

    @field_serializer("value")
    def serialize_value(self, value: Optional[float]) -> Optional[float]:
        if value is not None and math.isnan(value):
            return None
        return value
