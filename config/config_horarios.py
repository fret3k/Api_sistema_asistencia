# config/config_horarios.py

from datetime import time
from typing import Dict, Any

HORARIOS: Dict[str, Dict[str, time]] = {
    "ENTRADA_M": {
        "a_tiempo": time(8, 15),
        "tarde": time(8, 30)
    },
    "SALIDA_M": {
        "limite_temprano": time(13, 30)
    },
    "ENTRADA_T": {
        "a_tiempo": time(14, 15),
        "tarde": time(14, 30)
    },
    "SALIDA_T": {
        "limite_temprano": time(18, 0)
    }
}
