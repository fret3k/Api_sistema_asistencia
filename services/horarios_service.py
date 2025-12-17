from  config.config_horarios import HORARIOS

class HorariosService:

    @staticmethod
    def get_horarios():
        # Convertir time a string para enviar al frontend
        def convertir(h):
            return {
                k: v.strftime("%H:%M") for k, v in h.items()
            }

        return {k: convertir(v) for k, v in HORARIOS.items()}

    @staticmethod
    def update_horarios(data: dict):
        from datetime import time

        for clave, valores in data.items():
            if clave in HORARIOS and isinstance(valores, dict):
                for subclave, valor in valores.items():
                    if valor is not None:
                        if isinstance(valor, time):
                             HORARIOS[clave][subclave] = valor
                        elif isinstance(valor, str):
                             HORARIOS[clave][subclave] = time.fromisoformat(valor)

        return True
