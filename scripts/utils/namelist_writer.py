"""
Utilitário: Geração de namelist no formato do LorenzCycleToolkit (LEC)
Formato esperado (ver ../LorenzCycleToolkit/inputs/namelist_*):
    ;standard_name;Variable;Units
    Air Temperature;air_temperature;<var>;<units>
    Geopotential;geopotential;<var>;<units>            (m**2/s**2)
      OU
    Geopotential Height;geopotential_height;<var>;<units>  (m)
    Omega Velocity;omega;<var>;<units>
    Eastward Wind Component;eastward_wind;<var>;<units>
    Northward Wind Component;northward_wind;<var>;<units>
    Longitude;;<var>
    Latitude;;<var>
    Time;;<var>
    Vertical Level;;<var>

O LorenzCycleToolkit (src/utils/box_data.py, src/frameworks/lec_moving_framework.py)
aceita ambas as variantes de geopotencial e converte automaticamente altura
geopotencial (m) para geopotencial (m**2/s**2) quando o rótulo usado é
"Geopotential Height".
"""

from pathlib import Path

LEC_INPUTS_DIR = Path("../LorenzCycleToolkit/inputs")

REQUIRED_KEYS = [
    "temperature_var", "temperature_units",
    "omega_var", "omega_units",
    "u_var", "u_units",
    "v_var", "v_units",
    "lon_var", "lat_var", "time_var", "level_var",
]


def write_lec_namelist(model_name: str, mapping: dict, geopotential_kind: str = "geopotential",
                        output_dir: Path = LEC_INPUTS_DIR) -> Path:
    """
    Escreve um namelist compatível com o LorenzCycleToolkit em
    <output_dir>/namelist_<model_name>.

    mapping deve conter: temperature_var/units, omega_var/units, u_var/units,
    v_var/units, lon_var, lat_var, time_var, level_var, e
    geopotential_var/units (chave do geopotencial, ver geopotential_kind).

    geopotential_kind: "geopotential" (m**2/s**2, padrão) ou
    "geopotential_height" (m, ex. variável 'ght' do WRF).
    """
    if geopotential_kind not in ("geopotential", "geopotential_height"):
        raise ValueError("geopotential_kind deve ser 'geopotential' ou 'geopotential_height'")

    required = REQUIRED_KEYS + ["geopotential_var", "geopotential_units"]
    missing = [k for k in required if k not in mapping]
    if missing:
        raise KeyError(f"Faltam chaves no mapping para gerar o namelist: {missing}")

    if geopotential_kind == "geopotential":
        geopt_label, geopt_standard = "Geopotential", "geopotential"
    else:
        geopt_label, geopt_standard = "Geopotential Height", "geopotential_height"

    rows = [
        ("Air Temperature", "air_temperature", mapping["temperature_var"], mapping["temperature_units"]),
        (geopt_label, geopt_standard, mapping["geopotential_var"], mapping["geopotential_units"]),
        ("Omega Velocity", "omega", mapping["omega_var"], mapping["omega_units"]),
        ("Eastward Wind Component", "eastward_wind", mapping["u_var"], mapping["u_units"]),
        ("Northward Wind Component", "northward_wind", mapping["v_var"], mapping["v_units"]),
        ("Longitude", None, mapping["lon_var"], None),
        ("Latitude", None, mapping["lat_var"], None),
        ("Time", None, mapping["time_var"], None),
        ("Vertical Level", None, mapping["level_var"], None),
    ]

    lines = [";standard_name;Variable;Units"]
    for label, standard_name, var, unit in rows:
        if standard_name is None:
            lines.append(f"{label};;{var}")
        else:
            lines.append(f"{label};{standard_name};{var};{unit}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"namelist_{model_name}"
    output_file.write_text("\n".join(lines) + "\n")
    return output_file
