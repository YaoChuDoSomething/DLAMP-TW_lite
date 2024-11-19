#!/bin/python

import cdsapi
from datetime import timedelta, datetime
from pathlib import Path

##! Time Control Section
lead_time          = timedelta(days=1)
init_dt_utc        = datetime(2022,8,29,0,0,0)
bc_timedelta       = timedelta(hours=1)

##! Diagnostic Parameters
total_bc_frames    = (lead_time // bc_timedelta) + 1

print( lead_time )
print( init_dt_utc )
print( bc_timedelta )
print( total_bc_frames )
print( '==================' )
##! CDS API Request Section (Time Independent Variables)
prod_type          = ["reanalysis"]
vars_sfc           = [
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "2m_temperature",
        "mean_sea_level_pressure",
        "surface_pressure",
        "total_column_water_vapour",
        "total_precipitation",
        "2m_dewpoint_temperature"
        ]
vars_prs           = [
        "u_component_of_wind",
        "v_component_of_wind",
        "temperature",
        "specific_humidity",
        "geopotential",
        "vertical_velocity"
        ]
area               = [ 40, 100, 5, 145 ]
prs_levs           = [
        50, 150, 300, 500, 700, 850, 925, 1000
        ]

##! ====================================================================
def era5_sfc( vars_sfc, yy, mm, dd, HHMM, target ):
    dataset = "reanalysis-era5-single-levels"
    request = {
            "product_type": prod_type,
            "variable": vars_sfc,
            "year": [ yy ],
            "month": [ mm ],
            "day": [ dd ],
            "time": [ HHMM ],
            "area": area,
            "data_format": "netcdf",
            "download_format": "unarchived"
            }
    client = cdsapi.Client()
    client.retrieve(dataset, request, target)
    return()
##! ====================================================================
def era5_prs( vars_prs, levs, yy, mm, dd, HHMM, target ):
    dataset = "reanalysis-era5-pressure-levels"
    request = {
            "product_type": prod_type,
            "variable": vars_prs,
            "pressure_level": levs,
            "year": [ yy ],
            "month": [ mm ],
            "day": [ dd ],
            "time": [ HHMM ],
            "area": area,
            "data_format": "netcdf",
            "download_format": "unarchived"
            }
    client = cdsapi.Client()
    client.retrieve(dataset, request, target)
    return()
##! ====================================================================

for i in range( total_bc_frames ):
    dt_utc         = init_dt_utc + ( bc_timedelta * i )
    yy             = dt_utc.strftime('%Y')
    mm             = dt_utc.strftime('%m')
    dd             = dt_utc.strftime('%d')
    HHMM           = dt_utc.strftime('%H:%M')

    target_dir     = dt_utc.strftime('./data/')
    target_sfc     = dt_utc.strftime('./data/%Y%m%d%H_sfc.nc')
    target_prs     = dt_utc.strftime('./data/%Y%m%d%H_upper.nc')
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    print( dt_utc.strftime('%Y%m%d_%H%M') )
    print( target_sfc )
    era5_sfc( vars_sfc, yy, mm, dd, HHMM, target_sfc )
    print( target_prs )
    era5_prs( vars_prs, prs_levs, yy, mm, dd, HHMM, target_prs )
