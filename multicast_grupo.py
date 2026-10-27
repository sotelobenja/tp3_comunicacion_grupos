import socket
import json
import sys
import uuid
from datetime import datetime

# Configuración de la comunicación multicast
GRUPO_MULTICAST = "239.10.10.10"
PUERTO_MULTICAST = 5007

# Puerto utilizado por el coordinador para recibir mensajes externos
PUERTO_COORDINADOR = 5008

# Dirección IP de escucha
HOST = "0.0.0.0"


# FUNCIÓN PARA CREAR Y ENVIAR MENSAJES MULTICAST

def enviar_multicast(mensaje):
    """
    Envía un mensaje a todos los equipos suscriptos
    al grupo multicast en un único datagrama UDP.
    """

    datos = json.dumps(mensaje).encode("utf-8")

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM,
        socket.IPPROTO_UDP
    ) as socket_envio:
        # El mensaje no sale de la red local mediante este socket.
        socket_envio.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_MULTICAST_TTL,
            1
        )
        socket_envio.sendto(
            datos,
            (GRUPO_MULTICAST, PUERTO_MULTICAST)
        )


# EJERCICIO B: NODOS QUE PERTENECEN AL GRUPO MULTICAST

def iniciar_nodo(nombre_nodo):
    """
    Inicia un nodo que se suscribe al grupo multicast
    y recibe los mensajes enviados al grupo.
    """

    socket_recepcion = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM,
        socket.IPPROTO_UDP
    )

    # Permite compartir el puerto entre los receptores multicast.
    socket_recepcion.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    # En Windows puede ser necesario configurar SO_REUSEADDR
    # en todos los equipos que comparten el puerto.
    socket_recepcion.bind(("", PUERTO_MULTICAST))

    # Suscripción al grupo multicast.
    direccion_grupo = socket.inet_aton(GRUPO_MULTICAST)
    interfaz = socket.inet_aton("0.0.0.0")

    socket_recepcion.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_ADD_MEMBERSHIP,
        direccion_grupo + interfaz
    )

    print(f"\n[{nombre_nodo}] Nodo iniciado.")
    print(f"[{nombre_nodo}] Grupo: {GRUPO_MULTICAST}")
    print(f"[{nombre_nodo}] Puerto: {PUERTO_MULTICAST}")
    print("[{}] Esperando mensajes...\n".format(nombre_nodo))

    mensajes_recibidos = set()

    try:
        while True:
            datos, direccion = socket_recepcion.recvfrom(65535)

            try:
                mensaje = json.loads(datos.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                print("Se recibió un mensaje con formato inválido.")
                continue

            if not isinstance(mensaje, dict):
                print("Se recibió un mensaje con formato inválido.")
                continue

            identificador = mensaje.get("id")

            # Control básico de mensajes duplicados.
            if identificador is not None and not isinstance(identificador, str):
                print("Se recibió un mensaje con identificador inválido.")
                continue

            if identificador in mensajes_recibidos:
                continue

            if identificador is not None:
                mensajes_recibidos.add(identificador)

            secuencia = mensaje.get("secuencia", "N/A")
            emisor = mensaje.get("emisor", "Desconocido")
            contenido = mensaje.get("contenido", "")

            print(f"\n[{nombre_nodo}] Mensaje recibido")
            print(f"Secuencia: {secuencia}")
            print(f"Emisor: {emisor}")
            print(f"Contenido: {contenido}")
            print(f"Origen de red: {direccion[0]}:{direccion[1]}")

    except KeyboardInterrupt:
        print(f"\n[{nombre_nodo}] Nodo detenido.")

    finally:
        socket_recepcion.close()


# EJERCICIOS A Y C: COORDINADOR CENTRAL

def iniciar_coordinador():
    """
    Recibe mensajes de equipos externos y los distribuye
    al grupo multicast, asignándoles números de secuencia.
    """

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    ) as socket_coordinador:
        socket_coordinador.bind((HOST, PUERTO_COORDINADOR))
        secuencia = 0

        print("\n[COORDINADOR] Servidor iniciado.")
        print(f"[COORDINADOR] Puerto de recepción: {PUERTO_COORDINADOR}")
        print(f"[COORDINADOR] Grupo multicast: {GRUPO_MULTICAST}")
        print("[COORDINADOR] Esperando mensajes externos...\n")

        try:
            while True:
                datos, direccion = socket_coordinador.recvfrom(65535)

                try:
                    mensaje_externo = json.loads(datos.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    print("[COORDINADOR] Mensaje externo inválido.")
                    continue

                if not isinstance(mensaje_externo, dict):
                    print("[COORDINADOR] Mensaje externo inválido.")
                    continue

                secuencia += 1

                # El coordinador serializa los mensajes externos en el
                # orden en que los recibe antes de distribuirlos al grupo.
                mensaje_grupo = {
                    "id": str(uuid.uuid4()),
                    "secuencia": secuencia,
                    "emisor": mensaje_externo.get(
                        "emisor",
                        f"Equipo externo {direccion[0]}"
                    ),
                    "contenido": mensaje_externo.get(
                        "contenido",
                        ""
                    ),
                    "fecha": datetime.now().isoformat(timespec="seconds")
                }

                print("\n[COORDINADOR] Mensaje externo recibido.")
                print(f"Origen: {direccion[0]}:{direccion[1]}")
                print(f"Secuencia asignada: {secuencia}")
                print(f"Contenido: {mensaje_grupo['contenido']}")

                # Un datagrama UDP corresponde a un mensaje completo.
                enviar_multicast(mensaje_grupo)

                print("[COORDINADOR] Mensaje enviado al grupo multicast.")

        except KeyboardInterrupt:
            print("\n[COORDINADOR] Servidor detenido.")


# EJERCICIO C: EQUIPO EXTERNO AL GRUPO

def iniciar_externo(ip_coordinador):
    """
    Permite que una computadora que no pertenece al grupo
    envíe mensajes al coordinador central.
    """

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    ) as socket_externo:
        print("\n[EQUIPO EXTERNO] Conectado al programa.")
        print(f"[EQUIPO EXTERNO] Coordinador: {ip_coordinador}")
        print("Escribí un mensaje y presioná Enter.")
        print("Escribí 'salir' para finalizar.\n")

        try:
            while True:
                contenido = input("Mensaje: ")

                if contenido.lower() == "salir":
                    break

                mensaje = {
                    "emisor": "Equipo externo",
                    "contenido": contenido
                }

                datos = json.dumps(mensaje).encode("utf-8")

                # La solicitud completa se envía en un único datagrama.
                socket_externo.sendto(
                    datos,
                    (ip_coordinador, PUERTO_COORDINADOR)
                )

                print("[EQUIPO EXTERNO] Mensaje enviado al coordinador.")

        except KeyboardInterrupt:
            print("\n[EQUIPO EXTERNO] Programa detenido.")


# PROGRAMA PRINCIPAL

def mostrar_ayuda():
    print("""
Sistema de comunicación grupal mediante UDP multicast

Uso:

  En cada una de las tres computadoras del grupo:
    python multicast_grupo.py nodo Nodo1
    python multicast_grupo.py nodo Nodo2
    python multicast_grupo.py nodo Nodo3

  En una computadora (puede ser una de las tres), iniciar el coordinador:
    python multicast_grupo.py coordinador

  En la cuarta computadora, enviar mensajes al coordinador:
    python multicast_grupo.py externo IP_DEL_COORDINADOR

Ejemplos:

  python multicast_grupo.py nodo Nodo1
  python multicast_grupo.py coordinador
  python multicast_grupo.py externo 192.168.1.100

Los tres nodos se unen a la misma dirección de grupo multicast
239.10.10.10:5007. Cada equipo conserva su propia IP de la red.
El coordinador escucha en el puerto UDP 5008. Habilitá esos puertos
en el firewall y conectá los cuatro equipos a una red que permita multicast.

UDP mantiene cada envío como un datagrama (un mensaje no se mezcla con
otro), pero no garantiza entrega ni retransmisión si la red pierde paquetes.
""")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        mostrar_ayuda()
        sys.exit(1)

    modo = sys.argv[1].lower()

    if modo == "nodo":
        nombre = sys.argv[2] if len(sys.argv) > 2 else "Nodo"
        iniciar_nodo(nombre)

    elif modo == "coordinador":
        iniciar_coordinador()

    elif modo == "externo":
        if len(sys.argv) < 3:
            print("Error: indicá la IP del coordinador.")
            mostrar_ayuda()
            sys.exit(1)

        iniciar_externo(sys.argv[2])

    else:
        mostrar_ayuda()