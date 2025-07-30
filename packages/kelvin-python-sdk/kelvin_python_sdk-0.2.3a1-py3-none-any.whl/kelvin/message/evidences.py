from datetime import datetime
from typing import ClassVar, List, Optional

from pydantic import AnyHttpUrl, BaseModel


def to_camel(string: str) -> str:
    s = "".join(word.capitalize() for word in string.split("_"))
    return s[0].lower() + s[1:]


class Evidence(BaseModel):
    model_config = {"extra": "allow"}
    _TYPE: ClassVar[str] = ""


class BaseEvidence(BaseModel):
    type: str
    payload: Evidence


class Markdown(Evidence):
    """
    Evidence representing a block of markdown content.

    Attributes:
        title (Optional[str]): The title of the markdown content, displayed as a heading or label.
        markdown (str): The markdown-formatted text content to be rendered.

    Notes:
        - The `markdown` attribute should contain valid markdown syntax to ensure correct rendering.
    """

    _TYPE = "markdown"

    title: Optional[str] = None
    markdown: str


class IFrame(Evidence):
    """
    Evidence representing embedded iframe content, typically used to display external webpages or media as evidence.

    Attributes:
        title (Optional[str]): The title of the iframe content.
        url (AnyHttpUrl): The URL of the external content to be displayed within the iframe.

    Notes:
        - The `url` must be a valid HTTP or HTTPS URL for secure embedding.
    """

    _TYPE = "iframe"

    title: Optional[str] = None
    url: AnyHttpUrl


class Image(Evidence):
    """
    Evidence representing an image.

    Attributes:
        title (Optional[str]): The title of the image evidence.
        description (Optional[str]): A description or caption for the image, providing additional context.
        url (AnyHttpUrl): The URL of the image source, used for displaying the image.
        timestamp (Optional[datetime]): The timestamp related with the image was created.
    """

    _TYPE = "image"

    title: Optional[str] = None
    description: Optional[str] = None
    url: AnyHttpUrl
    timestamp: Optional[datetime] = None


class Chart(Evidence):
    """
    Evidence representing a generic chart, used as an interface for Highcharts configurations.
    For detailed chart options and configuration, see the [Highcharts API documentation]
    (https://api.highcharts.com/highcharts/).

    Attributes:
        timestamp (Optional[datetime]): The timestamp related with the chart.
        title (Optional[str]): The title displayed on the chart.

    Notes:
        - Extra options beyond defined attributes are allowed and should follow Highcharts API
        specifications to ensure compatibility.
    """

    model_config = {"extra": "allow", "alias_generator": to_camel, "populate_by_name": True}

    _TYPE = "chart"

    timestamp: Optional[datetime] = None
    title: Optional[str] = None


class Series(BaseModel):
    model_config = {"extra": "allow"}

    name: str
    type: Optional[str] = None
    data: list


class BarSeries(Series):
    type: str = "bar"


class LineSeries(Series):
    type: str = "line"


class LineChart(Chart):
    """
    Evidence representing a line chart configuration, extending the `Chart` base class.
    For detailed line chart options and configuration, see the [Highcharts Line Chart API]
    (https://api.highcharts.com/highcharts/series.line).

    Attributes:
        x_axis (dict): Configuration for the x-axis in the line chart, following Highcharts API.
        y_axis (dict): Configuration for the y-axis in the line chart, following Highcharts API.
        series (list): Data series to be displayed in the line chart, following Highcharts API.

    Notes:
        - Extra options beyond defined attributes are allowed and should follow Highcharts API
        specifications to ensure compatibility.
    """

    _TYPE = "line-chart"

    x_axis: dict = {}
    y_axis: dict = {}
    series: List[LineSeries] = []


class BarChart(Chart):
    """
    Evidence representing a bar chart configuration, extending the `Chart` base class.
    For detailed line chart options and configuration, see the [Highcharts Line Chart API]
    (https://api.highcharts.com/highcharts/series.bar).

    Attributes:
        x_axis (dict): Configuration for the x-axis in the line chart, following Highcharts API.
        y_axis (dict): Configuration for the y-axis in the line chart, following Highcharts API.
        series (list): Data series to be displayed in the line chart, following Highcharts API.

    Notes:
        - Extra options beyond defined attributes are allowed and should follow Highcharts API
        specifications to ensure compatibility.
    """

    _TYPE = "bar-chart"

    x_axis: dict = {}
    y_axis: dict = {}
    series: List[BarSeries] = []


class Dynacard(Chart):
    """
    Evidence for Dynacard representation. Defaults xAxis for Position(inch) and yAxis for Load(libs).
    This uses line chart configurations, for more details see the [Highcharts Line Chart API]
    (https://api.highcharts.com/highcharts/series.line).

    Attributes:
        series (list): Data series to be displayed in the line chart, following Highcharts API.

    Notes:
        - Extra options beyond defined attributes are allowed and should follow Highcharts API
        specifications to ensure compatibility.
    """

    _TYPE = "dynacard"

    series: List[Series] = []
