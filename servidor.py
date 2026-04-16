import socket
import sqlite3
import threading
from datetime import datetime


# --- Configuración de la Base de Datos ---
def inicializar_db():
    """Crea la base de datos y la tabla si no existen."""
    try:
        conexion = sqlite3.connect("registro_de_chats.db")
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT,
                fecha_envio TEXT,
                ip_cliente TEXT
            )
        """
        )
        conexion.commit()
        return conexion
    except sqlite3.Error as e:
        # Relanzamos la excepción para que quien llame decida cómo manejarla
        raise RuntimeError(f"Error al acceder a la DB: {e}")


def guardar_mensaje(conexion, contenido, ip):
    """Inserta el mensaje recibido en la tabla correspondiente de SQLite"""
    try:
        cursor = conexion.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO mensajes (contenido, fecha_envio, ip_cliente) VALUES (?, ?, ?)",
            (contenido, fecha, ip),
        )
        conexion.commit()
        return fecha
    except sqlite3.Error as e:
        raise RuntimeError(f"Error al guardar mensaje en la DB: {e}")


# --- Configuración del Socket TCP/IP ---
def configurar_servidor():
    """Inicializa el socket y maneja errores de puerto."""
    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 y TCP
        # Permite reutilizar el puerto inmediatamente después de cerrar el script
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind(("localhost", 5000))
        servidor.listen(10)  # 10 conexiones en cola
        print("Servidor escuchando en localhost:5000...")
        return servidor
    except socket.error as e:
        print(f"Error al configurar el socket (Puerto ocupado): {e}")
        exit(1)


def manejar_cliente(cliente_socket, ip_cliente):
    """Atiende a un cliente en su propio hilo, con su propia conexión a la DB."""
    try:
        conexion_db = inicializar_db()
    except RuntimeError as e:
        print(f"[{ip_cliente}] {e}. Cerrando conexión con el cliente.")
        cliente_socket.close()
        return

    try:
        while True:
            data = cliente_socket.recv(1024).decode("utf-8")
            if not data:
                break

            print(f"[{ip_cliente}] Mensaje recibido: {data}")

            try:
                timestamp = guardar_mensaje(conexion_db, data, ip_cliente)
                respuesta = f"Mensaje recibido: {timestamp}"
            except RuntimeError as e:
                print(f"[{ip_cliente}] {e}")
                respuesta = "Error interno: no se pudo guardar el mensaje."

            cliente_socket.send(respuesta.encode("utf-8"))
    finally:
        cliente_socket.close()
        conexion_db.close()
        print(f"[{ip_cliente}] Conexión cerrada")


def ejecutar_servidor():
    try:
        inicializar_db()  # Verificación temprana: falla rápido si la DB no es accesible
    except RuntimeError as e:
        print(e)
        exit(1)

    server_socket = configurar_servidor()

    try:
        while True:
            cliente_socket, direccion = server_socket.accept()
            ip_cliente = direccion[0]
            print(f"Conexión establecida desde {ip_cliente}")

            hilo = threading.Thread(
                target=manejar_cliente, args=(cliente_socket, ip_cliente)
            )
            hilo.daemon = True  # Corre en segundo plano y se cierra automaticamente al apagar el servidor
            hilo.start()
    except KeyboardInterrupt:
        print("\nApagando el servidor...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    ejecutar_servidor()
