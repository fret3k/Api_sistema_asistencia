# config/config_horarios.py

from datetime import time
from typing import Dict, Any

HORARIOS: Dict[str, Dict[str, time]] = {
    "ENTRADA_M": {
        "inicio_marcacion": time(7, 50),
        "entrada": time(8, 0),
        "a_tiempo": time(8, 15),
        "tarde": time(8, 30)
    },
    "SALIDA_M": {
        "inicio_marcacion": time(12, 0),
        "limite_temprano": time(13, 30)
    },
    "ENTRADA_T": {
        "inicio_marcacion": time(14, 20),
        "entrada": time(14, 30),
        "a_tiempo": time(14, 45),
        "tarde": time(15, 00)
    },
    "SALIDA_T": {
        "inicio_marcacion": time(16, 0),
        "limite_temprano": time(17, 0)
    }
}
