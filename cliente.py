"""
cliente.py
----------
Cliente de chat básico con sockets TCP/IP.
Se conecta al servidor en localhost:5000 y permite enviar múltiples mensajes
hasta que el usuario escribe 'éxito' (con o sin tilde).
"""

import socket


# ──────────────────────────────────────────────
# CONFIGURACIÓN GENERAL
# ──────────────────────────────────────────────
HOST = "localhost"
PORT = 5000

# Palabras clave que finalizan la sesión (toleramos variantes con/sin tilde)
PALABRAS_SALIDA = {"éxito", "exito"}


# ──────────────────────────────────────────────
# FUNCIONES DEL CLIENTE
# ──────────────────────────────────────────────


def conectar_servidor() -> socket.socket:
    """Crea un socket TCP/IP y establece la conexión con el servidor."""
    # Configuración del socket TCP/IP del cliente
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 y TCP

    try:
        cliente.connect((HOST, PORT))
        print(f"[CLIENTE] Conectado al servidor en {HOST}:{PORT}")
        print("[CLIENTE] Escribí tus mensajes. Para terminar, escribí 'éxito'.\n")
    except ConnectionRefusedError:
        raise RuntimeError(
            f"[CLIENTE] No se pudo conectar a {HOST}:{PORT}. "
            "¿El servidor está corriendo?"
        )

    return cliente


def enviar_mensajes(cliente: socket.socket):
    """
    Bucle interactivo: lee mensajes del usuario, los envía al servidor
    y muestra la respuesta recibida. Termina al escribir 'éxito'.
    """
    while True:
        try:
            # Lectura del mensaje por consola
            mensaje = input("Vos: ").strip()

            # Validación: no enviar mensajes vacíos
            if not mensaje:
                print("[CLIENTE] El mensaje no puede estar vacío. Intentá de nuevo.")
                continue

            # Condición de salida
            if mensaje.lower() in PALABRAS_SALIDA:
                print("[CLIENTE] Sesión finalizada. ¡Hasta luego!")
                break

            # Envío del mensaje al servidor (codificado en UTF-8)
            cliente.sendall(mensaje.encode("utf-8"))

            # Espera y recepción de la respuesta del servidor
            respuesta = cliente.recv(1024).decode("utf-8")
            print(f"[SERVIDOR] {respuesta}\n")

        except KeyboardInterrupt:
            print("\n[CLIENTE] Interrumpido por el usuario.")
            break
        except ConnectionResetError:
            print("[CLIENTE] El servidor cerró la conexión inesperadamente.")
            break
        except Exception as e:
            print(f"[CLIENTE] Error inesperado: {e}")
            break


# ──────────────────────────────────────────────
# PUNTO DE ENTRADA
# ──────────────────────────────────────────────


def main():
    """Conecta al servidor y entra al bucle de mensajes."""
    try:
        cliente = conectar_servidor()
        enviar_mensajes(cliente)
    except RuntimeError as e:
        print(e)
    finally:
        cliente.close()


if __name__ == "__main__":
    main()
