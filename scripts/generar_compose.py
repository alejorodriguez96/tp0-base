from typing import TextIO
import sys

NETWORK_NAME = "testing_net"
NETWORK_SUBNET = "172.25.125.0/24"
NETWORK = {
    NETWORK_NAME: {
        "ipam": {
            "driver": "default",
            "config": [
                {
                    "subnet": NETWORK_SUBNET
                }
            ]
        }
    }
}

SERVER_SERVICE = {
    "container_name": "server",
    "image": "server:latest",
    "entrypoint": "python3 /main.py",
    "environment": [
        "PYTHONUNBUFFERED=1",
    ],
    "networks": [
        NETWORK_NAME
    ],
    "volumes": [
        "./server/config.ini:/config.ini",
    ],
}

def generar_client_service(cliente_id: int):
    """Genera la configuración para ejecutar un servicio de cliente.
    
    Args:
        nombre (int): Nombre a asignarle al servicio.

    Returns:
        dict: Configuración del servicio.
    """
    return {
        "container_name": f"client{cliente_id}",
        "image": "client:latest",
        "entrypoint": "/client",
        "environment": [
            f"CLI_ID={cliente_id}",
            "NOMBRE=${NOMBRE}",
            "APELLIDO=${APELLIDO}",
            "DOCUMENTO=${DOCUMENTO}",
            "NACIMIENTO=${NACIMIENTO}",
            "NUMERO=${NUMERO}",
        ],
        "networks": [
            NETWORK_NAME
        ],
        "depends_on": [
            "server"
        ],
        "volumes": [
            "./client/config.yaml:/config.yaml",
            "$./.data/" + f"agency-{cliente_id}.csv:/agency-{cliente_id}.csv",
        ],
    }

def escribir_yaml(compose: dict, file: TextIO, indent: int = 0) -> None:
    """Escribe un archivo YAML con la configuración de un docker-compose.
    
    Args:
        compose (dict): Configuración del docker-compose.
        file (TextIO): Archivo a escribir.
    """
    for key, value in compose.items():
        file.write("  " * indent)
        file.write(f"{key}: ")
        if isinstance(value, dict):
            file.write("\n")
            escribir_yaml(value, file, indent + 1)
        elif isinstance(value, list):
            file.write("\n")
            for item in value:
                file.write("  " * (indent + 1))
                file.write(f"- {item}\n")
        else:
            file.write(f"{value}\n")
        file.write("\n")


def generar_compose(path_archivo: str, clientes: int):
    """
    Genera un archivo docker-compose.yml con la configuración
    para ejecutar un servidor y varios clientes.
    
    Args:
        path_archivo (str): Nombre del archivo a generar.
        clientes (int): Número de clientes a agregar al compose.
    """
    services = {
        "server": SERVER_SERVICE
    }
    for i in range(clientes):
        nombre = f"client{i + 1}"
        services[nombre] = generar_client_service(i + 1)
    compose = {
        "name": "tp0",
        "services": services,
        "networks": NETWORK,
    }
    with open(path_archivo, "w", encoding="utf-8") as f:
        escribir_yaml(compose, f)

if __name__ == "__main__":
    try:
        path = sys.argv[1]
        cantidad = int(sys.argv[2])
        generar_compose(path, cantidad)
    except IndexError:
        print("Uso: python3 generar_compose.py <path al archivo de destino> <cantidad>")
    except ValueError:
        print("La cantidad debe ser un número entero.")
