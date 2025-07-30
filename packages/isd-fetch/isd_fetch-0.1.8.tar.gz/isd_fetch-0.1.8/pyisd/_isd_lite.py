from concurrent.futures import ThreadPoolExecutor, as_completed
from io import StringIO
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import urlopen

import geopandas as gpd
import pandas as pd
from tqdm.auto import tqdm

from .misc import check_params, daterange, proj, to_crs


class IsdLite:
    """
    A client for accessing NOAA's ISD-Lite (Integrated Surface Data Lite) weather dataset.

    ISD-Lite provides global hourly observations of temperature, dew point, pressure, wind,
    sky coverage, and precipitation from weather stations worldwide. This client handles
    downloading and processing the data, with support for spatial and temporal filtering.

    The data fields available are:
        - temp: Air temperature (Celsius)
        - dewtemp: Dew point temperature (Celsius)
        - pressure: Sea level pressure (hectopascals)
        - winddirection: Wind direction (degrees)
        - windspeed: Wind speed (meters/second)
        - skycoverage: Sky coverage/ceiling (code)
        - precipitation-1h: One-hour precipitation (mm)
        - precipitation-6h: Six-hour precipitation (mm)

    Args:
        crs (int or str, optional): Coordinate reference system for spatial operations.
            Defaults to 4326 (WGS 84).
        verbose (int, optional): Verbosity level for progress reporting.
            0 for silent, 1 for progress bars. Defaults to 0.

    Examples:
        # Initialize the client
        isd = IsdLite()

        # Get data for all US stations for January 2020
        data = isd.get_data(
            start='2020-01-01',
            end='2020-01-31',
            countries='US'
        )

        # Get data within a specific region, organized by weather variable
        texas_data = isd.get_data(
            start='2020-01-01',
            geometry=(-106.6, 25.8, -93.5, 36.5),  # Texas bounding box
            organize_by='field'
        )

        # Use with geopandas for spatial filtering
        import geopandas as gpd
        city = gpd.read_file('city_boundary.geojson')
        city_data = isd.get_data(
            start='2020-01-01',
            geometry=city
        )

        # Access specific weather variables
        temperatures = texas_data['temp']  # When organize_by='field'
        # Or
        station_data = data['724940']  # When organize_by='location'
        station_temp = station_data['temp']
    """

    data_url = "https://www.ncei.noaa.gov/pub/data/noaa/isd-lite/{year}/"
    fields = (
        "temp",
        "dewtemp",
        "pressure",
        "winddirection",
        "windspeed",
        "skycoverage",
        "precipitation-1h",
        "precipitation-6h",
    )
    max_retries = 100

    def __init__(self, crs=4326, verbose=0):
        self.crs = to_crs(crs)
        self._get_raw_metadata()
        self.verbose = verbose

    def _get_raw_metadata(self):
        """Retrieve and process weather station metadata from NOAA sources."""
        for attempt in range(self.max_retries):
            try:
                # Open the URL and read the content using urllib
                with urlopen("https://www.ncei.noaa.gov/pub/data/noaa/isd-history.txt", timeout=2) as response:
                    content = response.read().decode("utf-8")

                # Process the content with pandas
                metadata = (
                    pd.read_fwf(StringIO(content), skiprows=20, header=0, dtype={"USAF": str, "WBAN": str})
                    .dropna(subset=["LAT", "LON"])
                    .query("not (LON == 0 and LAT == 0)")
                )

                metadata["x"], metadata["y"] = proj(metadata["LON"], metadata["LAT"], 4326, self.crs)
                metadata[["BEGIN", "END"]] = metadata[["BEGIN", "END"]].astype(str).apply(pd.to_datetime)

                self.raw_metadata = gpd.GeoDataFrame(
                    metadata.drop(columns=["LON", "LAT"]),
                    geometry=gpd.points_from_xy(metadata.x, metadata.y, crs=self.crs),
                )
                break  # Exit the loop if successful

            except URLError as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Failed to download metadata after {self.max_retries} attempts: {e}")

    def _filter_metadata(self, countries, geometry):
        """
        Internal: filter raw_metadata by country or geometry and return list of (USAF, WBAN) tuples.
        """
        df = self.raw_metadata
        # Apply filters
        if (geometry is None) and (countries is None):
            filt = df
        elif geometry is None:
            if isinstance(countries, str):
                countries = (countries,)
            filt = df[df["CTRY"].isin(countries)]
        else:
            if isinstance(geometry, gpd.base.GeoPandasBase):
                filt = gpd.clip(df, geometry.to_crs(self.crs))
            else:
                filt = gpd.clip(df, geometry)
        # Extract unique station identifier pairs
        pairs = filt.drop_duplicates(subset=["USAF", "WBAN"])[["USAF", "WBAN"]].values
        return [(str(usaf), str(wban)) for usaf, wban in pairs]

    @classmethod
    def _download_read(cls, url):
        time_features = ["year", "month", "day", "hour"]
        df = pd.read_csv(url, sep="\\s+", header=None, na_values=-9999)
        df.columns = time_features + list(cls.fields)
        df[["temp", "dewtemp", "pressure", "windspeed"]] /= 10.0
        df.index = pd.to_datetime(df[time_features])
        df = df.drop(columns=time_features)
        return df

    @classmethod
    def _download_data_id(cls, usaf_id, wban_id, years):
        ret = []
        for year in years:
            try:
                df = cls._download_read(urljoin(cls.data_url.format(year=year), f"{usaf_id}-{wban_id}-{year}.gz"))
                ret.append(df)
            except Exception as _:
                pass

        if ret:
            return pd.concat(ret)
        else:
            return pd.DataFrame()

    def get_data(
        self,
        start,
        end=None,
        station_id=None,
        countries=None,
        geometry=None,
        organize_by="location",
        n_jobs=6,
    ):
        """
        Fetches weather data from the ISD-Lite dataset for the specified time range and location.

        Args:
            start (datetime): The start date for the data retrieval.
            end (datetime, optional): The end date for the data retrieval. If not provided, defaults to the start date.
            station_id (str, optional): A specific weather station ID in the format 'USAF-WBAN' to retrieve data for.
                If provided, overrides any spatial or country filters. If None, data for all stations will
            countries (str or iterable of str, optional): Country code(s) to filter stations by. Must be valid codes from
                the ISD-Lite metadata (found in raw_metadata['CTRY']). Can be either a single country code as string
                or multiple codes as an iterable. If None, stations from all countries will be considered.
            geometry (GeoSeries or tuple, optional): A spatial filter for the stations. Can be either:
                - A GeoSeries or geometry object to filter stations by spatial location
                - A tuple of (xmin, ymin, xmax, ymax) defining a bounding box
                If None, data for all stations will be retrieved. Defaults to None.
            organize_by (str, optional): Determines how the resulting data is organized. Options are:
                - 'location': Organize data by weather station.
                - 'field': Organize data by weather variable.
                Defaults to 'location'.
            n_jobs (int, optional): The number of threads to use for parallel data downloads. Defaults to 6.

        Returns:
            dict: A dictionary containing the weather data. The structure of the dictionary depends on the
            `organize_by` parameter:
                - If 'location': Keys are station IDs, and values are DataFrames with weather data.
                - If 'field': Keys are weather variables, and values are DataFrames with stations as columns.

        Raises:
            ValueError: If `organize_by` is not one of the allowed options.

        Examples:
            # Get data for a single country
            data = isd.get_data(start='2020-01-01', end='2020-12-31', countries='US')

            # Get data for multiple countries
            data = isd.get_data(start='2020-01-01', countries=['US', 'CA', 'MX'])

            # Get data within a bounding box
            data = isd.get_data(start='2020-01-01', geometry=(-100, 30, -90, 40))
        """
        check_params(param=organize_by, params=("field", "location"))
        time = daterange(start, end, freq="h")
        years = time.year.unique()

        # Determine station list: optional single station override
        if station_id is not None:
            try:
                usaf_id, wban_id = station_id.split("-", 1)
            except ValueError:
                raise ValueError("station_id must be in format 'USAF-WBAN'")
            stations = [(usaf_id, wban_id)]
        else:
            stations = self._filter_metadata(countries=countries, geometry=geometry)

        def fetch_data(station):
            usaf_id, wban_id = station
            df = self._download_data_id(usaf_id=usaf_id, wban_id=wban_id, years=years)
            return usaf_id, wban_id, df.reindex(index=time)

        ret = {}
        with ThreadPoolExecutor(max_workers=n_jobs) as executor:
            # Launch fetch tasks for each station tuple
            futures = {executor.submit(fetch_data, station): station for station in stations}

            for future in tqdm(as_completed(futures), total=len(futures), disable=(not self.verbose)):
                usaf_id, wban_id, data = future.result()
                if data.size > 0:
                    ret[f"{usaf_id}-{wban_id}"] = data

        if organize_by == "field":
            ret = {
                field: pd.concat([ret[station_id][field].rename(station_id) for station_id in ret], axis=1)
                for field in self.fields
            }

        return ret
