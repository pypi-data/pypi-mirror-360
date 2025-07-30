CATEGORIES = [
    {
        "name": "Deformation Data",
        "code": "1",
        "types": [
            {"code": "1", "name": "Angle"},
            {"code": "2", "name": "EDM"},
            {"code": "3", "name": "GPS"},
            {"code": "4", "name": "GPS Vector"},
            {"code": "5", "name": "Levelling"},
            {"code": "6", "name": "Insar"},
            {"code": "7", "name": "Strain"},
            {"code": "8", "name": "Electronic Tilt"},
            {"code": "9", "name": "Tilt Vector"},
        ],
    },
    {
        "name": "Fields Data",
        "code": "2",
        "types": [
            {"code": "1", "name": "Magnetic Fields"},
            {"code": "2", "name": "Gravity Fields"},
            {"code": "3", "name": "Electric Fields"},
            {"code": "4", "name": "Magnetic Vector"},
        ],
    },
    {
        "name": "Gas Data",
        "code": "3",
        "types": [
            {"code": "1", "name": "Sample Gas"},
            {"code": "2", "name": "Soil Efflux"},
            {"code": "3", "name": "Plume from Ground based station"},
            {"code": "4", "name": "Plume From Satellite/Airplane"},
        ],
    },
    {
        "name": "Hydrologic Sample Data",
        "code": "4",
        "types": [
            {"code": "1", "name": "Hydrology"},
        ],
    },
    {
        "name": "Meteo Data",
        "code": "5",
        "types": [
            {"code": "1", "name": "Meteo"},
        ],
    },
    {
        "name": "Seismic Data",
        "code": "6",
        "types": [
            {"code": "1", "name": "Seismic Event From Network"},
            {"code": "2", "name": "Seismic Event From Single Station"},
            {"code": "3", "name": "Seismic Tremor"},
            {"code": "4", "name": "Seismic Intensity"},
            {"code": "5", "name": "Seismic Interval"},
            {"code": "6", "name": "RSAM"},
            {"code": "7", "name": "SSAM"},
        ],
    },
    {
        "name": "Thermal Data",
        "code": "7",
        "types": [
            {"code": "1", "name": "Thermal from Ground based station"},
            {"code": "2", "name": "Thermal From Satellite/Airplane"},
        ],
    },
]

CORRECTED = {
    "Angle": "Angle",
    "EDM": "EDM",
    "GPS": "GPS",
    "GPV": "GPS Vector",
    "InSAR": "Insar",
    "Plume from Satellite/Airplane": "Plume From Satellite/Airplane",
    "Soil efflux": "Soil Efflux",
    "Thermal from Satellite/Airplane": "Thermal From Satellite/Airplane",
    "directly sampled gas": "Sample Gas",
    "hydrology": "Hydrology",
    "leveling": "Levelling",
    "magnetic field": "Magnetic Field",
    "magnetic gravity": "Gravity Fields",
    "meteorologic": "Meteo",
    "plume": "Plume from Ground based station",
    "rsam": "RSAM",
    "seismic event": "Seismic Event From Network",
    "seismic interval": "Seismic Interval",
    "single station event": "Seismic Event From Single Station",
    "strain": "Strain",
    "thermal": "Thermal from Ground based station",
    "tilt": "Tilt Vector",
    "volcanic tremor": "Seismic Tremor",
}
