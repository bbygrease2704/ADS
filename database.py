import pymysql
from werkzeug.security import generate_password_hash

from config import MYSQL_DATABASE, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USER


def get_connection(database_name=None):
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=database_name or MYSQL_DATABASE,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def create_database_if_not_exists():
    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    connection.close()


def init_database():
    create_database_if_not_exists()
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                nombre VARCHAR(120) NOT NULL,
                rol VARCHAR(50) NOT NULL DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(120) NOT NULL,
                documento VARCHAR(30) NOT NULL UNIQUE,
                telefono VARCHAR(30) DEFAULT NULL,
                email VARCHAR(120) DEFAULT NULL,
                direccion VARCHAR(255) DEFAULT NULL,
                tipo_cliente VARCHAR(40) DEFAULT 'residencial',
                estado VARCHAR(30) DEFAULT 'activo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_cliente_nombre (nombre),
                INDEX idx_cliente_documento (documento),
                INDEX idx_cliente_estado (estado)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS servicios_instalacion (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente_id INT NOT NULL,
                tipo_servicio VARCHAR(120) NOT NULL,
                descripcion TEXT,
                direccion VARCHAR(255) NOT NULL,
                fecha_instalacion DATE NOT NULL,
                costo DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                estado VARCHAR(30) DEFAULT 'pendiente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                INDEX idx_servicio_cliente (cliente_id),
                INDEX idx_servicio_estado (estado)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ventas_gas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente_id INT NOT NULL,
                producto VARCHAR(120) NOT NULL,
                cantidad INT NOT NULL DEFAULT 1,
                total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                metodo_pago VARCHAR(50) DEFAULT 'efectivo',
                fecha_venta DATE NOT NULL,
                estado VARCHAR(30) DEFAULT 'completado',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                INDEX idx_venta_cliente (cliente_id),
                INDEX idx_venta_fecha (fecha_venta)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS casos_atencion (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente_id INT NOT NULL,
                titulo VARCHAR(160) NOT NULL,
                descripcion TEXT NOT NULL,
                prioridad VARCHAR(30) DEFAULT 'media',
                estado VARCHAR(30) DEFAULT 'abierto',
                responsable VARCHAR(120) DEFAULT 'Equipo BUENA VISTA',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                INDEX idx_ticket_cliente (cliente_id),
                INDEX idx_ticket_estado (estado),
                INDEX idx_ticket_prioridad (prioridad)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

        cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
        user_count = cursor.fetchone()['total']
        if user_count == 0:
            admin_password = generate_password_hash('admin123')
            cursor.execute(
                "INSERT INTO usuarios (username, password_hash, nombre, rol) VALUES (%s, %s, %s, %s)",
                ('admin', admin_password, 'Administrador', 'admin')
            )

        cursor.execute("SELECT COUNT(*) AS total FROM clientes")
        client_count = cursor.fetchone()['total']
        if client_count == 0:
            cursor.executemany(
                """
                INSERT INTO clientes (nombre, documento, telefono, email, direccion, tipo_cliente, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    ('Ana Gomez', '12345678', '999111222', 'ana.gomez@email.com', 'Av. Los Olivos 120', 'residencial', 'activo'),
                    ('Luis Ramirez', '87654321', '987654321', 'luis.ramirez@email.com', 'Jr. Las Flores 88', 'comercial', 'activo'),
                    ('María Torres', '45678912', '974123456', 'maria.torres@email.com', 'Calle Sol 45', 'residencial', 'inactivo'),
                    ('Carlos Dávila', '65432198', '965842147', 'carlos.davila@email.com', 'Urbanización San Miguel 301', 'comercial', 'activo'),
                ],
            )

        cursor.execute("SELECT COUNT(*) AS total FROM servicios_instalacion")
        service_count = cursor.fetchone()['total']
        if service_count == 0:
            cursor.executemany(
                """
                INSERT INTO servicios_instalacion (cliente_id, tipo_servicio, descripcion, direccion, fecha_instalacion, costo, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    (1, 'Instalación de gas domiciliario', 'Revisión y conexión de línea de gas para cocina.', 'Av. Los Olivos 120', '2026-09-20', 280.00, 'completado'),
                    (2, 'Cambio de medidor', 'Instalación de medidor nuevo y revisión de presión.', 'Jr. Las Flores 88', '2026-09-22', 420.00, 'pendiente'),
                    (4, 'Reinstalación de gas para negocio', 'Revisión total de distribución y seguridad.', 'Urbanización San Miguel 301', '2026-09-24', 520.00, 'en proceso'),
                ],
            )

        cursor.execute("SELECT COUNT(*) AS total FROM ventas_gas")
        sale_count = cursor.fetchone()['total']
        if sale_count == 0:
            cursor.executemany(
                """
                INSERT INTO ventas_gas (cliente_id, producto, cantidad, total, metodo_pago, fecha_venta, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    (1, 'Cilindro de 10 kg', 2, 120.00, 'efectivo', '2026-09-18', 'completado'),
                    (2, 'Cilindro de 45 kg', 1, 220.00, 'tarjeta', '2026-09-21', 'completado'),
                    (3, 'Cilindro de 10 kg', 3, 180.00, 'yape', '2026-09-23', 'pendiente'),
                ],
            )

        cursor.execute("SELECT COUNT(*) AS total FROM casos_atencion")
        ticket_count = cursor.fetchone()['total']
        if ticket_count == 0:
            cursor.executemany(
                """
                INSERT INTO casos_atencion (cliente_id, titulo, descripcion, prioridad, estado, responsable)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [
                    (1, 'Fuga en conexión de cocina', 'Se reporta olor fuerte en la conexión externa de la cocina.', 'alta', 'abierto', 'Carlos'),
                    (2, 'Solicita revisión de presión', 'Equipo solicita confirmar que la presión sea estable en el servicio comercial.', 'media', 'en proceso', 'Marina'),
                    (4, 'Entrega pendiente de cilindros', 'Cliente reporta que aún no ha recibido la entrega programada.', 'baja', 'abierto', 'Equipo de logística'),
                ],
            )

    connection.close()

    print(f"Base de datos '{MYSQL_DATABASE}' creada y lista para usar.")
