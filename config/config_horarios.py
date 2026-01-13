# config/config_horarios.py

from datetime import time
from typing import Dict, Any

HORARIOS: Dict[str, Dict[str, time]] = {
    "ENTRADA_M": {
        "inicio_marcacion": time(7, 0),
        "entrada": time(7, 30),
        "a_tiempo": time(7, 40), # 10 min de tolerancia
        "tarde": time(8, 30)
    },
    "SALIDA_M": {
        "inicio_marcacion": time(12, 20),
        "hora_salida": time(12, 30),
        "limite_temprano": time(14, 0)
    },
    "ENTRADA_T": {
        "inicio_marcacion": time(14, 0),
        "entrada": time(14, 30),
        "a_tiempo": time(14, 40), # 10 min de tolerancia
        "tarde": time(15, 30)
    },
    "SALIDA_T": {
        "inicio_marcacion": time(17, 20),
        "hora_salida": time(17, 30),
        "limite_temprano": time(19, 0)
    }
}
