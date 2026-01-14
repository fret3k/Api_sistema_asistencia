# config/config_horarios.py

from datetime import time
from typing import Dict, Any

HORARIOS: Dict[str, Dict[str, time]] = {
    "ENTRADA_M": {
        "inicio_marcacion": time(7, 0),
        "entrada": time(8, 0),      # 8:00 AM
        "a_tiempo": time(8, 15),    # Tolerancia hasta 8:15
        "tarde": time(8, 30)        # Límite tarde hasta 8:30
    },
    "SALIDA_M": {
        "inicio_marcacion": time(12, 0),
        "a_tiempo": time(13, 30),   # Salida oficial 1:30 PM
        "limite_temprano": time(14, 0)
    },
    "ENTRADA_T": {
        "inicio_marcacion": time(14, 0),
        "entrada": time(14, 30),    # 2:30 PM
        "a_tiempo": time(14, 45),   # Tolerancia hasta 2:45 PM
        "tarde": time(15, 0)        # Límite tarde hasta 3:00 PM
    },
    "SALIDA_T": {
        "inicio_marcacion": time(16, 0),
        "a_tiempo": time(17, 0),    # Salida oficial 5:00 PM
        "limite_temprano": time(23, 59)
    }
}
