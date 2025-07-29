import geopandas as gpd
import pandas as pd

from swmm_api.output_file import OBJECTS


def create_temporal_gis_database(fn, inp, out, kind, label=None, variable=None):
    """
    Create a geopackage file with temporal gis database of output timeseries results.

    Args:
        fn (str or Path): Path to the geopackage file:
        inp (swmm_api.SwmmInput): Input swmm input.
        out (swmm_api.SwmmOutput): Output swmm output.
        kind (str | list): [``'subcatchment'``, ``'node'`, ``'link'``, ``'system'``] (predefined in :obj:`swmm_api.output_file.definitions.OBJECTS`)
        label (str | list | optional): name of the objekts
        variable (str | list | optional): variable names (predefined in :obj:`swmm_api.output_file.definitions.VARIABLES`)

            * subcatchment:
                - ``rainfall`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.RAINFALL`
                - ``snow_depth`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.SNOW_DEPTH`
                - ``evaporation`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.EVAPORATION`
                - ``infiltration`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.INFILTRATION`
                - ``runoff`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.RUNOFF`
                - ``groundwater_outflow`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.GW_OUTFLOW`
                - ``groundwater_elevation`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.GW_ELEVATION`
                - ``soil_moisture`` or :attr:`~swmm_api.output_file.definitions.SUBCATCHMENT_VARIABLES.SOIL_MOISTURE`
            * node:
                - ``depth`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.DEPTH`
                - ``head`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.HEAD`
                - ``volume`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.VOLUME`
                - ``lateral_inflow`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.LATERAL_INFLOW`
                - ``total_inflow`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.TOTAL_INFLOW`
                - ``flooding`` or :attr:`~swmm_api.output_file.definitions.NODE_VARIABLES.FLOODING`
            * link:
                - ``flow`` or :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.FLOW`
                - ``depth`` or :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.DEPTH`
                - ``velocity`` or :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.VELOCITY`
                - ``volume`` or :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.VOLUME`
                - ``capacity`` or :attr:`~swmm_api.output_file.definitions.LINK_VARIABLES.CAPACITY`
            * system:
                - ``air_temperature`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.AIR_TEMPERATURE`
                - ``rainfall`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.RAINFALL`
                - ``snow_depth`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.SNOW_DEPTH`
                - ``infiltration`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.INFILTRATION`
                - ``runoff`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.RUNOFF`
                - ``dry_weather_inflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.DW_INFLOW`
                - ``groundwater_inflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.GW_INFLOW`
                - ``RDII_inflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.RDII_INFLOW`
                - ``direct_inflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.DIRECT_INFLOW`
                - ``lateral_inflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.LATERAL_INFLOW`
                - ``flooding`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.FLOODING`
                - ``outflow`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.OUTFLOW`
                - ``volume`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.VOLUME`
                - ``evaporation`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.EVAPORATION`
                - ``PET`` or :attr:`~swmm_api.output_file.definitions.SYSTEM_VARIABLES.PET`
    """
    df = out.get_part(kind, label, variable)
    if df.columns.nlevels != 1:
        df = df.stack(1).T
    else:
        df = df.T
    if kind == OBJECTS.NODE:
        df['geometry'] = inp.COORDINATES.geo_series
        crs = inp.COORDINATES._crs
    elif kind == OBJECTS.LINK:
        df['geometry'] = inp.VERTICES.geo_series
        crs = inp.VERTICES._crs
    elif kind == OBJECTS.SUBCATCHMENT:
        df['geometry'] = inp.POLYGONS.geo_series
        crs = inp.POLYGONS._crs
    else:
        raise NotImplementedError(kind)
    df.index.name = kind
    if df.columns.nlevels != 1:
        df.columns.names = ['timestamp', 'variables']
    else:
        df.columns.name = 'timestamp'
    df = df.set_index('geometry', append=True)
    df = df.stack(0)
    if isinstance(df, pd.Series) and (isinstance(variable, str) or len(variable) == 1):
        df = df.rename(variable)
    gpd.GeoDataFrame(df.reset_index(), crs=crs).to_file(fn)
