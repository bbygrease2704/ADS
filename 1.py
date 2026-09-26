from functools import wraps

import pymysql
from flask import Flask, flash, redirect, render_template_string, request, session, url_for
from markupsafe import Markup
from werkzeug.security import check_password_hash, generate_password_hash

DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'mysqlpucp'
DB_NAME = 'buena_vista_gas'

app = Flask(__name__)
app.secret_key = 'buena-vista-gas-secret-key-2026'

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #edf3f8;
            --panel: #ffffff;
            --panel-soft: #f3f7fb;
            --primary: #2f4d73;
            --primary-dark: #1d3557;
            --accent: #5a7db4;
            --text: #1c2530;
            --muted: #67758d;
            --border: #dfe8f2;
            --success: #1d9d6c;
            --warning: #d69d2b;
            --danger: #d94a5c;
            --info: #4a7bd8;
            --shadow: 0 14px 36px rgba(25, 47, 71, 0.09);
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #edf3f8 0%, #ddeaf6 100%);
            color: var(--text);
        }
        a { text-decoration: none; color: var(--primary); }
        h1,h2,h3,p { margin-top: 0; }
        input, select, textarea, button {
            font: inherit;
        }
        .auth-page {
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 24px;
        }
        .auth-card {
            width: min(480px, 100%);
            background: rgba(255,255,255,0.96);
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            border-radius: 24px;
            padding: 32px 28px;
        }
        .auth-brand {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 18px;
        }
        .brand-mark {
            width: 72px;
            height: 72px;
            border-radius: 18px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.8rem;
        }
        .auth-brand h1 {
            margin: 0;
            font-size: 1.9rem;
            letter-spacing: 0.06em;
        }
        .auth-brand span {
            display: block;
            color: var(--muted);
            font-size: 0.9rem;
        }
        .auth-card h2 {
            margin-bottom: 10px;
            font-size: 1.7rem;
        }
        .auth-card p {
            color: var(--muted);
            margin-bottom: 18px;
        }
        .field-label { display: block; margin: 12px 0 8px; font-weight: 600; }
        input, select, textarea {
            width: 100%;
            min-height: 44px;
            padding: 10px 12px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: #fff;
            color: var(--text);
        }
        textarea { min-height: 130px; resize: vertical; }
        .primary-button, .secondary-button, .link-button {
            border: none;
            border-radius: 12px;
            padding: 10px 16px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s ease;
        }
        .primary-button {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
        }
        .secondary-button {
            background: var(--panel-soft);
            color: var(--primary-dark);
            border: 1px solid var(--border);
        }
        .link-button {
            background: transparent;
            color: var(--danger);
            padding: 0;
        }
        .primary-button:hover, .secondary-button:hover { transform: translateY(-1px); }
        .full { width: 100%; margin-top: 18px; }
        .login-footer {
            margin-top: 10px;
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: var(--muted);
            font-size: 0.8rem;
        }
        .app-shell { display: flex; min-height: 100vh; }
        .sidebar {
            width: 260px;
            background: linear-gradient(180deg, #1b2d42 0%, #2f4d73 100%);
            color: white;
            padding: 24px 18px;
        }
        .brand-box {
            display: flex;
            align-items: center;
            gap: 14px;
            border-bottom: 1px solid rgba(255,255,255,0.18);
            padding-bottom: 18px;
            margin-bottom: 26px;
        }
        .brand-box h1 {
            margin: 0;
            font-size: 1.2rem;
            letter-spacing: 0.06em;
        }
        .brand-box small {
            color: rgba(255,255,255,0.72);
        }
        .brand-mark.small {
            width: 48px;
            height: 48px;
            border-radius: 14px;
            background: rgba(255,255,255,0.14);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
        }
        .nav-menu { display: flex; flex-direction: column; gap: 8px; }
        .nav-item {
            display: block;
            padding: 12px 14px;
            color: rgba(255,255,255,0.9);
            border-radius: 10px;
            transition: background 0.2s ease;
        }
        .nav-item:hover { background: rgba(255,255,255,0.08); }
        .nav-item.danger { margin-top: 16px; color: #ffd3d9; }
        .main-content {
            flex: 1;
            padding: 28px 30px 36px;
        }
        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 18px;
            margin-bottom: 24px;
        }
        .eyebrow {
            margin: 0 0 8px;
            color: var(--muted);
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .topbar h2 { margin: 0; font-size: 2rem; }
        .user-pill {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 10px 18px;
            box-shadow: var(--shadow);
            font-weight: 600;
        }
        .user-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--success);
            display: inline-block;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(150px, 1fr));
            gap: 18px;
            margin-bottom: 26px;
        }
        .stat-card, .panel-card {
            background: var(--panel);
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            border-radius: 18px;
            padding: 20px 18px;
        }
        .stat-card span {
            display: block;
            font-size: 0.76rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 10px;
        }
        .stat-card strong { font-size: 2rem; color: var(--primary-dark); }
        .panel-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 22px; }
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }
        .panel-header h3 { margin: 0; font-size: 1.1rem; }
        .text-link { font-weight: 600; }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 12px 10px;
            border-bottom: 1px solid var(--border);
            vertical-align: middle;
        }
        th {
            color: var(--muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .action-links {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        .toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
            flex-wrap: wrap;
            margin-bottom: 22px;
        }
        .filter-form {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }
        .filter-form input, .filter-form select {
            min-width: 180px;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: capitalize;
        }
        .badge-activo, .badge-completado, .badge-cerrado { background: rgba(29,157,108,0.14); color: #0f6d4b; }
        .badge-inactivo, .badge-pendiente, .badge-abierto { background: rgba(214,157,43,0.12); color: #8d5d12; }
        .badge-en\ proceso { background: rgba(74,123,216,0.12); color: #2d5ec5; }
        .badge-priority-alta { background: rgba(217,74,92,0.12); color: #a12637; }
        .badge-priority-media { background: rgba(214,157,43,0.12); color: #8d5d12; }
        .badge-priority-baja { background: rgba(29,157,108,0.12); color: #0f6d4b; }
        .form-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(220px, 1fr));
            gap: 18px;
        }
        .full-width { grid-column: 1 / -1; }
        .form-actions {
            margin-top: 24px;
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }
        .flash-container {
            display: grid;
            gap: 10px;
            margin-bottom: 18px;
        }
        .flash {
            border-radius: 10px;
            padding: 12px 14px;
            font-weight: 500;
        }
        .flash-success { background: rgba(29,157,108,0.12); color: #0f6d4b; border: 1px solid rgba(29,157,108,0.2); }
        .flash-error { background: rgba(217,74,92,0.10); color: #a12637; border: 1px solid rgba(217,74,92,0.2); }
        .detail-card { margin-bottom: 24px; }
        .detail-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 18px;
        }
        .detail-header h3 { margin: 0 0 6px; font-size: 1.6rem; }
        .detail-header p { margin: 0; color: var(--muted); }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(220px, 1fr));
            gap: 18px;
        }
        .list-simple { margin: 0; padding-left: 18px; }
        .list-simple li { padding: 8px 0; }
        @media (max-width: 900px) {
            .app-shell { flex-direction: column; }
            .sidebar { width: 100%; }
            .main-content { padding: 20px 18px 30px; }
            .stats-grid, .panel-grid, .form-grid, .info-grid { grid-template-columns: 1fr; }
            .topbar { align-items: flex-start; flex-direction: column; }
            .toolbar { align-items: flex-start; flex-direction: column; }
            .filter-form { width: 100%; }
        }
    </style>
</head>
<body>
    {% if session.get('user_id') %}
    <div class="app-shell">
        <aside class="sidebar">
            <div class="brand-box">
                <div class="brand-mark small">BV</div>
                <div>
                    <h1>BUENA VISTA</h1>
                    <small>Gas & Servicios</small>
                </div>
            </div>
            <nav class="nav-menu">
                <a href="{{ url_for('dashboard') }}" class="nav-item">Dashboard</a>
                <a href="{{ url_for('clientes') }}" class="nav-item">Clientes</a>
                <a href="{{ url_for('servicios') }}" class="nav-item">Servicios</a>
                <a href="{{ url_for('ventas') }}" class="nav-item">Ventas</a>
                <a href="{{ url_for('tickets') }}" class="nav-item">Casos</a>
                <a href="{{ url_for('logout') }}" class="nav-item danger">Cerrar sesión</a>
            </nav>
        </aside>

        <main class="main-content">
            <header class="topbar">
                <div>
                    <p class="eyebrow">Panel administrativo</p>
                    <h2>{{ page_title }}</h2>
                </div>
                <div class="user-pill">
                    <span class="user-dot"></span>
                    {{ session.get('nombre', 'Usuario') }}
                </div>
            </header>

            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <div class="flash-container">
                        {% for category, message in messages %}
                            <div class="flash flash-{{ category }}">{{ message }}</div>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}

            {{ content }}
        </main>
    </div>
    {% else %}
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-container" style="max-width:560px;margin:18px auto 0;">
                    {% for category, message in messages %}
                        <div class="flash flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        {{ content }}
    {% endif %}
</body>
</html>
"""


def get_connection(database_name=None):
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=database_name or DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def init_db():
    try:
        base_conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
        with base_conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        base_conn.close()

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    nombre VARCHAR(120) NOT NULL,
                    rol VARCHAR(40) NOT NULL DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            cur.execute('''
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
                    INDEX idx_nombre (nombre),
                    INDEX idx_documento (documento),
                    INDEX idx_estado (estado)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS servicios_instalacion (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cliente_id INT NOT NULL,
                    tipo_servicio VARCHAR(150) NOT NULL,
                    descripcion TEXT,
                    direccion VARCHAR(255) NOT NULL,
                    fecha_instalacion DATE NOT NULL,
                    costo DECIMAL(10,2) NOT NULL DEFAULT 0,
                    estado VARCHAR(30) DEFAULT 'pendiente',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS ventas_gas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cliente_id INT NOT NULL,
                    producto VARCHAR(120) NOT NULL,
                    cantidad INT NOT NULL DEFAULT 1,
                    total DECIMAL(10,2) NOT NULL DEFAULT 0,
                    metodo_pago VARCHAR(40) DEFAULT 'efectivo',
                    fecha_venta DATE NOT NULL,
                    estado VARCHAR(30) DEFAULT 'completado',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS casos_atencion (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cliente_id INT NOT NULL,
                    titulo VARCHAR(160) NOT NULL,
                    descripcion TEXT NOT NULL,
                    prioridad VARCHAR(30) DEFAULT 'media',
                    estado VARCHAR(30) DEFAULT 'abierto',
                    responsable VARCHAR(120) DEFAULT 'Equipo BUENA VISTA',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

            cur.execute('SELECT COUNT(*) AS total FROM usuarios')
            if cur.fetchone()['total'] == 0:
                cur.execute(
                    'INSERT INTO usuarios (username, password_hash, nombre, rol) VALUES (%s, %s, %s, %s)',
                    ('admin', generate_password_hash('admin123'), 'Administrador', 'admin')
                )

            cur.execute('SELECT COUNT(*) AS total FROM clientes')
            if cur.fetchone()['total'] == 0:
                cur.executemany(
                    '''
                    INSERT INTO clientes (nombre, documento, telefono, email, direccion, tipo_cliente, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''',
                    [
                        ('Ana Gómez', '12345678', '999111222', 'ana.gomez@email.com', 'Av. Los Olivos 120', 'residencial', 'activo'),
                        ('Luis Ramírez', '87654321', '987654321', 'luis.ramirez@email.com', 'Jr. Las Flores 88', 'comercial', 'activo'),
                        ('María Torres', '45678912', '974123456', 'maria.torres@email.com', 'Calle Sol 45', 'residencial', 'inactivo'),
                        ('Carlos Dávila', '65432198', '965842147', 'carlos.davila@email.com', 'Urbanización San Miguel 301', 'comercial', 'activo'),
                    ],
                )

            cur.execute('SELECT COUNT(*) AS total FROM servicios_instalacion')
            if cur.fetchone()['total'] == 0:
                cur.executemany(
                    '''
                    INSERT INTO servicios_instalacion (cliente_id, tipo_servicio, descripcion, direccion, fecha_instalacion, costo, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''',
                    [
                        (1, 'Instalación de gas domiciliario', 'Conexión segura para cocina y calentador', 'Av. Los Olivos 120', '2026-09-20', 280.00, 'completado'),
                        (2, 'Cambio de medidor', 'Reemplazo de medidor y revisión de presión', 'Jr. Las Flores 88', '2026-09-22', 420.00, 'pendiente'),
                        (4, 'Instalación comercial', 'Servicio para negocio con línea nueva', 'Urbanización San Miguel 301', '2026-09-24', 520.00, 'en proceso'),
                    ],
                )

            cur.execute('SELECT COUNT(*) AS total FROM ventas_gas')
            if cur.fetchone()['total'] == 0:
                cur.executemany(
                    '''
                    INSERT INTO ventas_gas (cliente_id, producto, cantidad, total, metodo_pago, fecha_venta, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''',
                    [
                        (1, 'Cilindro 10 kg', 2, 120.00, 'efectivo', '2026-09-18', 'completado'),
                        (2, 'Cilindro 45 kg', 1, 220.00, 'tarjeta', '2026-09-21', 'completado'),
                        (3, 'Cilindro 10 kg', 3, 180.00, 'yape', '2026-09-23', 'pendiente'),
                    ],
                )

            cur.execute('SELECT COUNT(*) AS total FROM casos_atencion')
            if cur.fetchone()['total'] == 0:
                cur.executemany(
                    '''
                    INSERT INTO casos_atencion (cliente_id, titulo, descripcion, prioridad, estado, responsable)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ''',
                    [
                        (1, 'Fuga en conexión de cocina', 'Se reporta olor fuerte en la conexión exterior de la cocina.', 'alta', 'abierto', 'Carlos'),
                        (2, 'Solicita revisión de presión', 'Equipo solicita revisar la presión del servicio comercial.', 'media', 'en proceso', 'Marina'),
                        (4, 'Entrega pendiente de cilindros', 'Cliente reporta entrega aún no realizada del pedido programado.', 'baja', 'abierto', 'Logística'),
                    ],
                )
        conn.close()
        print(f"Base de datos '{DB_NAME}' creada correctamente.")
    except Exception as exc:
        print('ERROR DE CONEXIÓN MYSQL:', exc)
        raise


def execute_query(sql, params=()):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params)
    conn.close()


def fetch_all(sql, params=()):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        result = cur.fetchall()
    conn.close()
    return result


def fetch_one(sql, params=()):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        result = cur.fetchone()
    conn.close()
    return result


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper


def course_html(title, page_title, content_html):
    return render_template_string(BASE_LAYOUT, title=title, page_title=page_title, content=Markup(content_html))


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        if not username or not password:
            flash('Ingrese usuario y contraseña.', 'error')
        else:
            user = fetch_one('SELECT * FROM usuarios WHERE username = %s', (username,))
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['nombre'] = user['nombre']
                flash('Bienvenido a BUENA VISTA GAS.', 'success')
                return redirect(url_for('dashboard'))
            flash('Credenciales inválidas.', 'error')

    login_html = '''
        <div class="auth-page">
            <div class="auth-card">
                <div class="auth-brand">
                    <div class="brand-mark">BV</div>
                    <div>
                        <h1>BUENA VISTA</h1>
                        <span>Gas & Servicios</span>
                    </div>
                </div>
                <h2>Iniciar sesión</h2>
                <p>Accede al sistema administrativo de clientes, ventas y soporte.</p>
                <form method="POST">
                    <label class="field-label" for="username">Usuario</label>
                    <input type="text" id="username" name="username" placeholder="admin" required>
                    <label class="field-label" for="password">Contraseña</label>
                    <input type="password" id="password" name="password" placeholder="••••••••" required>
                    <button type="submit" class="primary-button full">Entrar al sistema</button>
                </form>
                <div class="login-footer">
                    <small>Usuario demo: admin</small>
                    <small>Contraseña: admin123</small>
                </div>
            </div>
        </div>
    '''
    return course_html('Login | BUENA VISTA GAS', 'Iniciar sesión', login_html)


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'clientes': fetch_one('SELECT COUNT(*) AS total FROM clientes')['total'],
        'servicios': fetch_one('SELECT COUNT(*) AS total FROM servicios_instalacion')['total'],
        'ventas': fetch_one('SELECT COUNT(*) AS total FROM ventas_gas')['total'],
        'casos': fetch_one('SELECT COUNT(*) AS total FROM casos_atencion')['total'],
    }
    clientes = fetch_all('SELECT * FROM clientes ORDER BY created_at DESC LIMIT 5')
    tickets_abiertos = fetch_all('''
        SELECT t.*, c.nombre AS cliente_nombre
        FROM casos_atencion t
        JOIN clientes c ON c.id = t.cliente_id
        WHERE t.estado != %s
        ORDER BY t.created_at DESC
        LIMIT 5
    ''', ('cerrado',))

    content = f'''
        <div class="stats-grid">
            <div class="stat-card"><span>Clientes</span><strong>{stats['clientes']}</strong></div>
            <div class="stat-card"><span>Servicios</span><strong>{stats['servicios']}</strong></div>
            <div class="stat-card"><span>Ventas</span><strong>{stats['ventas']}</strong></div>
            <div class="stat-card"><span>Casos</span><strong>{stats['casos']}</strong></div>
        </div>
        <div class="panel-grid">
            <section class="panel-card wide">
                <div class="panel-header">
                    <h3>Clientes recientes</h3>
                    <a href="{url_for('clientes')}" class="text-link">Ver todos</a>
                </div>
                <table>
                    <thead><tr><th>Nombre</th><th>Documento</th><th>Teléfono</th><th>Estado</th></tr></thead>
                    <tbody>
                        {''.join(f'<tr><td>{c["nombre"]}</td><td>{c["documento"]}</td><td>{c["telefono"] or "-"}</td><td><span class="badge badge-{c["estado"]}">{c["estado"]}</span></td></tr>' for c in clientes) or '<tr><td colspan="4">No hay clientes registrados.</td></tr>'}
                    </tbody>
                </table>
            </section>
            <section class="panel-card">
                <div class="panel-header">
                    <h3>Casos abiertos</h3>
                    <a href="{url_for('tickets')}" class="text-link">Ver todos</a>
                </div>
                <div>
                    {''.join(f'<div style="background:#f3f7fb;border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin-bottom:12px;"><strong>{t["titulo"]}</strong><div style="color:var(--muted);margin-top:6px;">{t["cliente_nombre"]} · {t["prioridad"]}</div></div>' for t in tickets_abiertos) or '<p>No hay casos abiertos.</p>'}
                </div>
            </section>
        </div>
    '''
    return course_html('Dashboard | BUENA VISTA GAS', 'Dashboard', content)


@app.route('/clientes', methods=['GET'])
@login_required
def clientes():
    q = (request.args.get('q') or '').strip()
    estado = (request.args.get('estado') or '').strip()
    sql = 'SELECT * FROM clientes WHERE 1=1'
    params = []
    if q:
        sql += ' AND (nombre LIKE %s OR documento LIKE %s OR telefono LIKE %s OR email LIKE %s)'
        pattern = f'%{q}%'
        params.extend([pattern, pattern, pattern, pattern])
    if estado:
        sql += ' AND estado = %s'
        params.append(estado)
    sql += ' ORDER BY created_at DESC'
    rows = fetch_all(sql, tuple(params))

    table_rows = ''.join(
        f'''<tr>
            <td>{c['nombre']}</td>
            <td>{c['documento']}</td>
            <td>{c['telefono'] or '-'}</td>
            <td>{c['email'] or '-'}</td>
            <td>{c['tipo_cliente']}</td>
            <td><span class="badge badge-{c['estado']}">{c['estado']}</span></td>
            <td class="action-links">
                <a href="{url_for('cliente_detalle', cliente_id=c['id'])}">Ver</a>
                <a href="{url_for('cliente_editar', cliente_id=c['id'])}">Editar</a>
                <form method="POST" action="{url_for('cliente_eliminar', cliente_id=c['id'])}" onsubmit="return confirm('¿Eliminar cliente?');" style="display:inline;">
                    <button type="submit" class="link-button">Eliminar</button>
                </form>
            </td>
        </tr>''' for c in rows
    ) or '<tr><td colspan="7">No se encontraron clientes.</td></tr>'

    content = f'''
        <div class="toolbar">
            <form method="GET" class="filter-form">
                <input type="text" name="q" value="{q}" placeholder="Buscar por nombre, documento o email">
                <select name="estado">
                    <option value="">Todos los estados</option>
                    <option value="activo" {'selected' if estado == 'activo' else ''}>Activo</option>
                    <option value="inactivo" {'selected' if estado == 'inactivo' else ''}>Inactivo</option>
                </select>
                <button type="submit" class="primary-button">Filtrar</button>
            </form>
            <a href="{url_for('cliente_nuevo')}" class="primary-button">+ Nuevo cliente</a>
        </div>
        <section class="panel-card">
            <table>
                <thead><tr><th>Nombre</th><th>Documento</th><th>Teléfono</th><th>Email</th><th>Tipo</th><th>Estado</th><th>Acciones</th></tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        </section>
    '''
    return course_html('Clientes | BUENA VISTA GAS', 'Clientes', content)


@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def cliente_nuevo():
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        documento = (request.form.get('documento') or '').strip()
        telefono = (request.form.get('telefono') or '').strip()
        email = (request.form.get('email') or '').strip()
        direccion = (request.form.get('direccion') or '').strip()
        tipo_cliente = request.form.get('tipo_cliente') or 'residencial'
        estado = request.form.get('estado') or 'activo'
        if not nombre or not documento:
            flash('Nombre y documento son obligatorios.', 'error')
        else:
            execute_query(
                'INSERT INTO clientes (nombre, documento, telefono, email, direccion, tipo_cliente, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (nombre, documento, telefono, email, direccion, tipo_cliente, estado),
            )
            flash('Cliente registrado correctamente.', 'success')
            return redirect(url_for('clientes'))
    content = '''
        <section class="panel-card form-card">
            <form method="POST">
                <div class="form-grid">
                    <div><label>Nombre</label><input type="text" name="nombre" required></div>
                    <div><label>Documento</label><input type="text" name="documento" required></div>
                    <div><label>Teléfono</label><input type="text" name="telefono"></div>
                    <div><label>Email</label><input type="email" name="email"></div>
                    <div class="full-width"><label>Dirección</label><input type="text" name="direccion"></div>
                    <div><label>Tipo de cliente</label><select name="tipo_cliente"><option value="residencial">Residencial</option><option value="comercial">Comercial</option><option value="industrial">Industrial</option></select></div>
                    <div><label>Estado</label><select name="estado"><option value="activo">Activo</option><option value="inactivo">Inactivo</option></select></div>
                </div>
                <div class="form-actions">
                    <a href="/clientes" class="secondary-button">Cancelar</a>
                    <button type="submit" class="primary-button">Guardar</button>
                </div>
            </form>
        </section>
    '''
    return course_html('Nuevo cliente | BUENA VISTA GAS', 'Nuevo cliente', content)


@app.route('/clientes/<int:cliente_id>', methods=['GET'])
@login_required
def cliente_detalle(cliente_id):
    cliente = fetch_one('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
    if not cliente:
        flash('Cliente no encontrado.', 'error')
        return redirect(url_for('clientes'))
    servicios = fetch_all('SELECT * FROM servicios_instalacion WHERE cliente_id = %s ORDER BY fecha_instalacion DESC', (cliente_id,))
    ventas = fetch_all('SELECT * FROM ventas_gas WHERE cliente_id = %s ORDER BY fecha_venta DESC', (cliente_id,))
    tickets = fetch_all('SELECT * FROM casos_atencion WHERE cliente_id = %s ORDER BY created_at DESC', (cliente_id,))

    servicios_html = ''.join(f'<li>{s["tipo_servicio"]} - {s["estado"]} - S/. {s["costo"]}</li>' for s in servicios) or '<li>No registra servicios.</li>'
    ventas_html = ''.join(f'<li>{v["producto"]} - {v["cantidad"]} und. - {v["estado"]}</li>' for v in ventas) or '<li>No registra ventas.</li>'
    tickets_html = ''.join(f'<li>{t["titulo"]} - {t["estado"]} - {t["prioridad"]}</li>' for t in tickets) or '<li>No tiene casos activos.</li>'

    content = f'''
        <section class="panel-card detail-card">
            <div class="detail-header">
                <div><h3>{cliente['nombre']}</h3><p>{cliente['documento']} · {cliente['tipo_cliente']}</p></div>
                <a href="{url_for('cliente_editar', cliente_id=cliente['id'])}" class="secondary-button">Editar</a>
            </div>
            <div class="info-grid">
                <div><strong>Teléfono:</strong> {cliente['telefono'] or '-'}</div>
                <div><strong>Email:</strong> {cliente['email'] or '-'}</div>
                <div class="full-width"><strong>Dirección:</strong> {cliente['direccion'] or '-'}</div>
                <div><strong>Estado:</strong> <span class="badge badge-{cliente['estado']}">{cliente['estado']}</span></div>
            </div>
        </section>
        <div class="panel-grid">
            <section class="panel-card"><div class="panel-header"><h3>Servicios</h3></div><ul class="list-simple">{servicios_html}</ul></section>
            <section class="panel-card"><div class="panel-header"><h3>Ventas</h3></div><ul class="list-simple">{ventas_html}</ul></section>
        </div>
        <section class="panel-card"><div class="panel-header"><h3>Casos de atención</h3></div><ul class="list-simple">{tickets_html}</ul></section>
    '''
    return course_html('Detalle cliente | BUENA VISTA GAS', 'Detalle de cliente', content)


@app.route('/clientes/<int:cliente_id>/editar', methods=['GET', 'POST'])
@login_required
def cliente_editar(cliente_id):
    cliente = fetch_one('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
    if not cliente:
        flash('Cliente no encontrado.', 'error')
        return redirect(url_for('clientes'))
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        documento = (request.form.get('documento') or '').strip()
        telefono = (request.form.get('telefono') or '').strip()
        email = (request.form.get('email') or '').strip()
        direccion = (request.form.get('direccion') or '').strip()
        tipo_cliente = request.form.get('tipo_cliente') or 'residencial'
        estado = request.form.get('estado') or 'activo'
        if not nombre or not documento:
            flash('Nombre y documento son obligatorios.', 'error')
        else:
            execute_query(
                'UPDATE clientes SET nombre=%s, documento=%s, telefono=%s, email=%s, direccion=%s, tipo_cliente=%s, estado=%s WHERE id=%s',
                (nombre, documento, telefono, email, direccion, tipo_cliente, estado, cliente_id),
            )
            flash('Cliente actualizado correctamente.', 'success')
            return redirect(url_for('clientes'))
    content = f'''
        <section class="panel-card form-card">
            <form method="POST">
                <div class="form-grid">
                    <div><label>Nombre</label><input type="text" name="nombre" value="{cliente['nombre']}" required></div>
                    <div><label>Documento</label><input type="text" name="documento" value="{cliente['documento']}" required></div>
                    <div><label>Teléfono</label><input type="text" name="telefono" value="{cliente['telefono'] or ''}"></div>
                    <div><label>Email</label><input type="email" name="email" value="{cliente['email'] or ''}"></div>
                    <div class="full-width"><label>Dirección</label><input type="text" name="direccion" value="{cliente['direccion'] or ''}"></div>
                    <div><label>Tipo de cliente</label><select name="tipo_cliente"><option value="residencial" {'selected' if cliente['tipo_cliente']=='residencial' else ''}>Residencial</option><option value="comercial" {'selected' if cliente['tipo_cliente']=='comercial' else ''}>Comercial</option><option value="industrial" {'selected' if cliente['tipo_cliente']=='industrial' else ''}>Industrial</option></select></div>
                    <div><label>Estado</label><select name="estado"><option value="activo" {'selected' if cliente['estado']=='activo' else ''}>Activo</option><option value="inactivo" {'selected' if cliente['estado']=='inactivo' else ''}>Inactivo</option></select></div>
                </div>
                <div class="form-actions">
                    <a href="{url_for('clientes')}" class="secondary-button">Cancelar</a>
                    <button type="submit" class="primary-button">Guardar</button>
                </div>
            </form>
        </section>
    '''
    return course_html('Editar cliente | BUENA VISTA GAS', 'Editar cliente', content)


@app.route('/clientes/<int:cliente_id>/eliminar', methods=['POST'])
@login_required
def cliente_eliminar(cliente_id):
    execute_query('DELETE FROM clientes WHERE id = %s', (cliente_id,))
    flash('Cliente eliminado.', 'success')
    return redirect(url_for('clientes'))


@app.route('/servicios')
@login_required
def servicios():
    q = (request.args.get('q') or '').strip()
    estado = (request.args.get('estado') or '').strip()
    sql = '''SELECT s.*, c.nombre AS cliente_nombre FROM servicios_instalacion s JOIN clientes c ON c.id = s.cliente_id WHERE 1=1'''
    params = []
    if q:
        sql += ' AND (c.nombre LIKE %s OR s.tipo_servicio LIKE %s OR s.direccion LIKE %s)'
        pattern = f'%{q}%'
        params.extend([pattern, pattern, pattern])
    if estado:
        sql += ' AND s.estado = %s'
        params.append(estado)
    sql += ' ORDER BY s.fecha_instalacion DESC'
    rows = fetch_all(sql, tuple(params))

    table_rows = ''.join(
        f'''<tr><td>{r['cliente_nombre']}</td><td>{r['tipo_servicio']}</td><td>{r['fecha_instalacion']}</td><td>S/. {r['costo']}</td><td><span class="badge badge-{r['estado']}">{r['estado']}</span></td><td class="action-links"><a href="{url_for('servicio_detalle', servicio_id=r['id'])}">Ver</a><a href="{url_for('servicio_editar', servicio_id=r['id'])}">Editar</a><form method="POST" action="{url_for('servicio_eliminar', servicio_id=r['id'])}" onsubmit="return confirm('¿Eliminar servicio?');" style="display:inline;"><button type="submit" class="link-button">Eliminar</button></form></td></tr>''' for r in rows
    ) or '<tr><td colspan="6">No hay servicios registrados.</td></tr>'

    content = f'''
        <div class="toolbar">
            <form method="GET" class="filter-form">
                <input type="text" name="q" value="{q}" placeholder="Buscar servicio o cliente">
                <select name="estado">
                    <option value="">Todos</option>
                    <option value="pendiente" {'selected' if estado=='pendiente' else ''}>Pendiente</option>
                    <option value="en proceso" {'selected' if estado=='en proceso' else ''}>En proceso</option>
                    <option value="completado" {'selected' if estado=='completado' else ''}>Completado</option>
                </select>
                <button type="submit" class="primary-button">Filtrar</button>
            </form>
            <a href="{url_for('servicio_nuevo')}" class="primary-button">+ Nuevo servicio</a>
        </div>
        <section class="panel-card">
            <table>
                <thead><tr><th>Cliente</th><th>Tipo</th><th>Fecha</th><th>Costo</th><th>Estado</th><th>Acciones</th></tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        </section>
    '''
    return course_html('Servicios | BUENA VISTA GAS', 'Servicios de instalación', content)


@app.route('/servicios/nuevo', methods=['GET', 'POST'])
@login_required
def servicio_nuevo():
    clientes = fetch_all('SELECT * FROM clientes ORDER BY nombre ASC')
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        tipo_servicio = (request.form.get('tipo_servicio') or '').strip()
        descripcion = (request.form.get('descripcion') or '').strip()
        direccion = (request.form.get('direccion') or '').strip()
        fecha = request.form.get('fecha_instalacion')
        costo = request.form.get('costo') or 0
        estado = request.form.get('estado') or 'pendiente'
        if not cliente_id or not tipo_servicio or not direccion or not fecha:
            flash('Complete los campos obligatorios del servicio.', 'error')
        else:
            execute_query(
                'INSERT INTO servicios_instalacion (cliente_id, tipo_servicio, descripcion, direccion, fecha_instalacion, costo, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (cliente_id, tipo_servicio, descripcion, direccion, fecha, costo, estado),
            )
            flash('Servicio registrado.', 'success')
            return redirect(url_for('servicios'))

    options = ''.join(f'<option value="{c["id"]}">{c["nombre"]}</option>' for c in clientes)
    content = f'''
        <section class="panel-card form-card">
            <form method="POST">
                <div class="form-grid">
                    <div><label>Cliente</label><select name="cliente_id" required><option value="">Seleccionar cliente</option>{options}</select></div>
                    <div><label>Tipo de servicio</label><input type="text" name="tipo_servicio" required></div>
                    <div><label>Fecha de instalación</label><input type="date" name="fecha_instalacion" required></div>
                    <div><label>Costo</label><input type="number" step="0.01" name="costo" value="0"></div>
                    <div class="full-width"><label>Dirección</label><input type="text" name="direccion" required></div>
                    <div class="full-width"><label>Descripción</label><textarea name="descripcion"></textarea></div>
                    <div><label>Estado</label><select name="estado"><option value="pendiente">Pendiente</option><option value="en proceso">En proceso</option><option value="completado">Completado</option></select></div>
                </div>
                <div class="form-actions"><a href="/servicios" class="secondary-button">Cancelar</a><button type="submit" class="primary-button">Guardar</button></div>
            </form>
        </section>
    '''
    return course_html('Nuevo servicio | BUENA VISTA GAS', 'Nuevo servicio', content)


@app.route('/servicios/<int:servicio_id>')
@login_required
def servicio_detalle(servicio_id):
    servicio = fetch_one('''SELECT s.*, c.nombre AS cliente_nombre FROM servicios_instalacion s JOIN clientes c ON c.id = s.cliente_id WHERE s.id = %s''', (servicio_id,))
    if not servicio:
        flash('Servicio no encontrado.', 'error')
        return redirect(url_for('servicios'))
    content = f'''
        <section class="panel-card detail-card">
            <div class="detail-header">
                <div><h3>{servicio['tipo_servicio']}</h3><p>{servicio['cliente_nombre']}</p></div>
                <a href="{url_for('servicio_editar', servicio_id=servicio_id)}" class="secondary-button">Editar</a>
            </div>
            <div class="info-grid">
                <div><strong>Dirección:</strong> {servicio['direccion']}</div>
                <div><strong>Fecha:</strong> {servicio['fecha_instalacion']}</div>
                <div><strong>Costo:</strong> S/. {servicio['costo']}</div>
                <div><strong>Estado:</strong> <span class="badge badge-{servicio['estado']}">{servicio['estado']}</span></div>
                <div class="full-width"><strong>Descripción:</strong> {servicio['descripcion'] or '-'}</div>
            </div>
        </section>
    '''
    return course_html('Detalle servicio | BUENA VISTA GAS', 'Detalle de servicio', content)


@app.route('/servicios/<int:servicio_id>/editar', methods=['GET', 'POST'])
@login_required
def servicio_editar(servicio_id):
    servicio = fetch_one('SELECT * FROM servicios_instalacion WHERE id = %s', (servicio_id,))
    clientes = fetch_all('SELECT * FROM clientes ORDER BY nombre ASC')
    if not servicio:
        flash('Servicio no encontrado.', 'error')
        return redirect(url_for('servicios'))
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        tipo_servicio = (request.form.get('tipo_servicio') or '').strip()
        descripcion = (request.form.get('descripcion') or '').strip()
        direccion = (request.form.get('direccion') or '').strip()
        fecha = request.form.get('fecha_instalacion')
        costo = request.form.get('costo') or 0
        estado = request.form.get('estado') or 'pendiente'
        execute_query(
            'UPDATE servicios_instalacion SET cliente_id=%s, tipo_servicio=%s, descripcion=%s, direccion=%s, fecha_instalacion=%s, costo=%s, estado=%s WHERE id=%s',
            (cliente_id, tipo_servicio, descripcion, direccion, fecha, costo, estado, servicio_id),
        )
        flash('Servicio actualizado.', 'success')
        return redirect(url_for('servicios'))

    options = ''.join(f'<option value="{c["id"]}" {"selected" if c["id"] == servicio["cliente_id"] else ""}>{c["nombre"]}</option>' for c in clientes)
    content = f'''
        <section class="panel-card form-card">
            <form method="POST">
                <div class="form-grid">
                    <div><label>Cliente</label><select name="cliente_id" required>{options}</select></div>
                    <div><label>Tipo de servicio</label><input type="text" name="tipo_servicio" value="{servicio['tipo_servicio']}" required></div>
                    <div><label>Fecha</label><input type="date" name="fecha_instalacion" value="{servicio['fecha_instalacion']}" required></div>
                    <div><label>Costo</label><input type="number" step="0.01" name="costo" value="{servicio['costo']}"></div>
                    <div class="full-width"><label>Dirección</label><input type="text" name="direccion" value="{servicio['direccion']}" required></div>
                    <div class="full-width"><label>Descripción</label><textarea name="descripcion">{servicio['descripcion'] or ''}</textarea></div>
                    <div><label>Estado</label><select name="estado"><option value="pendiente" {'selected' if servicio['estado']=='pendiente' else ''}>Pendiente</option><option value="en proceso" {'selected' if servicio['estado']=='en proceso' else ''}>En proceso</option><option value="completado" {'selected' if servicio['estado']=='completado' else ''}>Completado</option></select></div>
                </div>
                <div class="form-actions"><a href="{url_for('servicios')}" class="secondary-button">Cancelar</a><button type="submit" class="primary-button">Guardar</button></div>
            </form>
        </section>
    '''
    return course_html('Editar servicio | BUENA VISTA GAS', 'Editar servicio', content)


@app.route('/servicios/<int:servicio_id>/eliminar', methods=['POST'])
@login_required
def servicio_eliminar(servicio_id):
    execute_query('DELETE FROM servicios_instalacion WHERE id = %s', (servicio_id,))
    flash('Servicio eliminado.', 'success')
    return redirect(url_for('servicios'))


@app.route('/ventas')
@login_required
def ventas():
    q = (request.args.get('q') or '').strip()
    estado = (request.args.get('estado') or '').strip()
    sql = '''SELECT v.*, c.nombre AS cliente_nombre FROM ventas_gas v JOIN clientes c ON c.id = v.cliente_id WHERE 1=1'''
    params = []
    if q:
        sql += ' AND (c.nombre LIKE %s OR v.producto LIKE %s OR v.metodo_pago LIKE %s)'
        pattern = f'%{q}%'
        params.extend([pattern, pattern, pattern])
    if estado:
        sql += ' AND v.estado = %s'
        params.append(estado)
    sql += ' ORDER BY v.fecha_venta DESC'
    rows = fetch_all(sql, tuple(params))

    table_rows = ''.join(
        f'''<tr><td>{r['cliente_nombre']}</td><td>{r['producto']}</td><td>{r['cantidad']}</td><td>S/. {r['total']}</td><td>{r['fecha_venta']}</td><td><span class="badge badge-{r['estado']}">{r['estado']}</span></td><td class="action-links"><a href="{url_for('venta_detalle', venta_id=r['id'])}">Ver</a><a href="{url_for('venta_editar', venta_id=r['id'])}">Editar</a><form method="POST" action="{url_for('venta_eliminar', venta_id=r['id'])}" onsubmit="return confirm('¿Eliminar venta?');" style="display:inline;"><button type="submit" class="link-button">Eliminar</button></form></td></tr>''' for r in rows
    ) or '<tr><td colspan="7">No hay ventas registradas.</td></tr>'

    content = f'''
        <div class="toolbar">
            <form method="GET" class="filter-form">
                <input type="text" name="q" value="{q}" placeholder="Buscar producto o cliente">
                <select name="estado">
                    <option value="">Todos</option>
                    <option value="completado" {'selected' if estado=='completado' else ''}>Completado</option>
                    <option value="pendiente" {'selected' if estado=='pendiente' else ''}>Pendiente</option>
                </select>
                <button type="submit" class="primary-button">Filtrar</button>
            </form>
            <a href="{url_for('venta_nueva')}" class="primary-button">+ Nueva venta</a>
        </div>
        <section class="panel-card">
            <table>
                <thead><tr><th>Cliente</th><th>Producto</th><th>Cantidad</th><th>Total</th><th>Fecha</th><th>Estado</th><th>Acciones</th></tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        </section>
    '''
    return course_html('Ventas | BUENA VISTA GAS', 'Ventas de gas', content)


@app.route('/ventas/nuevo', methods=['GET', 'POST'])
@login_required
def venta_nueva():
    clientes = fetch_all('SELECT * FROM clientes ORDER BY nombre ASC')
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        producto = (request.form.get('producto') or '').strip()
        cantidad = request.form.get('cantidad') or 1
        total = request.form.get('total') or 0
        metodo_pago = request.form.get('metodo_pago') or 'efectivo'
        fecha = request.form.get('fecha_venta')
        estado = request.form.get('estado') or 'completado'
        if not cliente_id or not producto or not fecha:
            flash('Complete los datos obligatorios para la venta.', 'error')
        else:
            execute_query(
                'INSERT INTO ventas_gas (cliente_id, producto, cantidad, total, metodo_pago, fecha_venta, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (cliente_id, producto, cantidad, total, metodo_pago, fecha, estado),
            )
            flash('Venta registrada correctamente.', 'success')
            return redirect(url_for('ventas'))

    options = ''.join(f'<option value="{c["id"]}">{c["nombre"]}</option>' for c in clientes)
    content = f'''
        <section class="panel-card form-card">
            <form method="POST">
                <div class="form-grid">
                    <div><label>Cliente</label><select name="cliente_id" required><option value="">Seleccionar cliente</option>{options}</select></div>
                    <div><label>Producto</label><input type="text" name="producto" required></div>
                    <div><label>Cantidad</label><input type="number" min="1" name="cantidad" value="1" required></div>
                    <div><label>Total</label><input type="number" step="0.01" name="total" value="0" required></div>
                    <div><label>Método de pago</label><select name="metodo_pago"><option value="efectivo">Efectivo</option><option value="tarjeta">Tarjeta</option><option value="yape">Yape</option></select></div>
                    <div><label>Fecha de venta</label><input type="date" name="fecha_venta" required></div>
                    <div><label>Estado</label><select name="estado"><option value="completado">Completado</option><option value="pendiente">Pendiente</option></select></div>
                </div>
                <div class="form-actions"><a href="/ventas" class="secondary-button">Cancelar</a><button type="submit" class="primary-button">Guardar</button></div>
            </form>
        </section>
    '''
    return course_html('Nueva venta | BUENA VISTA GAS', 'Nueva venta', content)


@app.route('/ventas/<int:venta_id>')
@login_required
def venta_detalle(venta_id):
    venta = fetch_one('''SELECT v.*, c.nombre AS cliente_nombre FROM ventas_gas v JOIN clientes c ON c.id = v.cliente_id WHERE v.id = %s''', (venta_id,))
    if not venta:
        flash('Venta no encontrada.', 'error')
        return redirect(url_for('ventas'))
    content = f'''
        <section class="panel-card detail-card">
            <div class="detail-header">
                <div><h3>{venta['producto']}</h3><p>{venta['cliente_nombre']}</p></div>
                <a href="{url_for('venta_editar', venta_id=venta_id)}" class="secondary-button">Editar</a>
            </div>
            <div class="info-grid">
                <div><strong>Cantidad:</strong> {venta['cantidad']}</div>
                <div><strong>Total:</strong> S/. {venta['total']}</div>
                <div><strong>Fecha:</strong> {venta['fecha_venta']}</div>
                <div><strong>Método:</strong> {venta['metodo_pago']}</div>
                <div><strong>Estado:</strong> <span class="badge badge-{venta['estado']}">{venta['estado']}</span></div>
            </div>
        </section>
    '''
    return course_html('Detalle venta | BUENA VISTA GAS', 'Detalle de venta', content)


@app.route('/ventas/<int:venta_id>/editar', methods=['GET', 'POST'])
@login_required
def venta_editar(venta_id):
    venta = fetch_one('SELECT * FROM ventas_gas WHERE id = %s', (venta_id,))
    clientes = fetch_all('SELECT * FROM clientes ORDER BY nombre ASC')
    if not venta:
        flash('Venta no encontrada.', 'error')
        return redirect(url_for('ventas'))
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        producto = (request.form.get('producto') or '').strip()
        cantidad = request.form.get('cantidad') or 1
        total = request.form.get('total') or 0
        metodo_pago = request.form.get('metodo_pago') or 'efectivo'
        fecha = request.form.get('fecha_venta')
        estado = request.form.get('estado') or 'completado'
        execute_query(
            'UPDATE ventas_gas SET cliente_id=%s, producto=%s, cantidad=%s, total=%s, metodo_pago=%s, fecha_venta=%s, estado=%s WHERE id=%s',
            (cliente_id, producto, cantidad, total, metodo_pago, fecha, estado, venta_id),
        )
        flash('Venta actualizada.', 'success')
        return redirect(url_for('ventas'))

    options = ''.join(f'<option value="{c["id"]}" {"selected" if c["id"] == venta["cliente_id"] else ""}>{c["nombre"]}</option>' for c in clientes)
    content = f'''
        <section class="panel-card form-card">
            <form method="POST">
                <div class="form-grid">
                    <div><label>Cliente</label><select name="cliente_id" required>{options}</select></div>
                    <div><label>Producto</label><input type="text" name="producto" value="{venta['producto']}" required></div>
                    <div><label>Cantidad</label><input type="number" min="1" name="cantidad" value="{venta['cantidad']}" required></div>
                    <div><label>Total</label><input type="number" step="0.01" name="total" value="{venta['total']}" required></div>
                    <div><label>Método de pago</label><select name="metodo_pago"><option value="efectivo" {'selected' if venta['metodo_pago']=='efectivo' else ''}>Efectivo</option><option value="tarjeta" {'selected' if venta['metodo_pago']=='tarjeta' else ''}>Tarjeta</option><option value="yape" {'selected' if venta['metodo_pago']=='yape' else ''}>Yape</option></select></div>
                    <div><label>Fecha</label><input type="date" name="fecha_venta" value="{venta['fecha_venta']}" required></div>
                    <div><label>Estado</label><select name="estado"><option value="completado" {'selected' if venta['estado']=='completado' else ''}>Completado</option><option value="pendiente" {'selected' if venta['estado']=='pendiente' else ''}>Pendiente</option></select></div>
                </div>
                <div class="form-actions"><a href="{url_for('ventas')}" class="secondary-button">Cancelar</a><button type="submit" class="primary-button">Guardar</button></div>
            </form>
        </section>
    '''
    return course_html('Editar venta | BUENA VISTA GAS', 'Editar venta', content)


@app.route('/ventas/<int:venta_id>/eliminar', methods=['POST'])
@login_required
def venta_eliminar(venta_id):
    execute_query('DELETE FROM ventas_gas WHERE id = %s', (venta_id,))
    flash('Venta eliminada.', 'success')
    return redirect(url_for('ventas'))


@app.route('/tickets')
@login_required
def tickets():
    q = (request.args.get('q') or '').strip()
    estado = (request.args.get('estado') or '').strip()
    prioridad = (request.args.get('prioridad') or '').strip()
    sql = '''SELECT t.*, c.nombre AS cliente_nombre FROM casos_atencion t JOIN clientes c ON c.id = t.cliente_id WHERE 1=1'''
    params = []
    if q:
        sql += ' AND (c.nombre LIKE %s OR t.titulo LIKE %s OR t.descripcion LIKE %s)'
        pattern = f'%{q}%'
        params.extend([pattern, pattern, pattern])
    if estado:
        sql += ' AND t.estado = %s'
        params.append(estado)
    if prioridad:
        sql += ' AND t.prioridad = %s'
        params.append(prioridad)
    sql += ' ORDER BY t.created_at DESC'
    rows = fetch_all(sql, tuple(params))

    table_rows = ''.join(
        f'''<tr><td>{r['cliente_nombre']}</td><td>{r['titulo']}</td><td><span class="badge badge-priority-{r['prioridad']}">{r['prioridad']}</span></td><td><span class="badge badge-{r['estado']}">{r['estado']}</span></td><td>{r['responsable']}</td><td class="action-links"><a href="{url_for('ticket_detalle', ticket_id=r['id'])}">Ver</a><a href="{url_for('ticket_editar', ticket_id=r['id'])}">Editar</a><form method="POST" action="{url_for('ticket_eliminar', ticket_id=r['id'])}" onsubmit="return confirm('¿Eliminar caso?');" style="display:inline;"><button type="submit" class="link-button">Eliminar</button></form></td></tr>''' for r in rows
    ) or '<tr><td colspan="6">No hay casos de atención.</td></tr>'

    content = f'''
        <div class="toolbar">
            <form method="GET" class="filter-form">
                <input type="text" name="q" value="{q}" placeholder="Buscar caso o cliente">
                <select name="estado">
                    <option value="">Todos</option>
                    <option value="abierto" {'selected' if estado=='abierto' else ''}>Abierto</option>
                    <option value="en proceso" {'selected' if estado=='en proceso' else ''}>En proceso</option>
                    <option value="cerrado" {'selected' if estado=='cerrado' else ''}>Cerrado</option>
                </select>
                <select name="prioridad">
                    <option value="">Todas</option>
                    <option value="baja" {'selected' if prioridad=='baja' else ''}>Baja</option>
                    <option value="media" {'selected' if prioridad=='media' else ''}>Media</option>
                    <option value="alta" {'selected' if prioridad=='alta' else ''}>Alta</option>
                </select>
                <button type="submit" class="primary-button">Filtrar</button>
            </form>
            <a href="{url_for('ticket_nuevo')}" class="primary-button">+ Nuevo caso</a>
        </div>
        <section class="panel-card">
            <table>
                <thead><tr><th>Cliente</th><th>Título</th><th>Prioridad</th><th>Estado</th><th>Responsable</th><th>Acciones</th></tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        </section>
    '''
    return course_html('Casos de atención | BUENA VISTA GAS', 'Casos de atención', content)


@app.route('/tickets/nuevo', methods=['GET', 'POST'])
@login_required
def ticket_nuevo():
    clientes = fetch_all('SELECT * FROM clientes ORDER BY nombre ASC')
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        titulo = (request.form.get('titulo') or '').strip()
        descripcion = (request.form.get('descripcion') or '').strip()
        prioridad = request.form.get('prioridad') or 'media'
        estado = request.form.get('estado') or 'abierto'
        responsable = (request.form.get('responsable') or 'Equipo BUENA VISTA').strip()
        if not cliente_id or not titulo or not descripcion:
            flash('Debe completar cliente, título y descripción del caso.', 'error')
        else:
            execute_query(
                'INSERT INTO casos_atencion (cliente_id, titulo, descripcion, prioridad, estado, responsable) VALUES (%s, %s, %s, %s, %s, %s)',
                (cliente_id, titulo, descripcion, prioridad, estado, responsable),
            )
            flash('Caso de atención registrado.', 'success')
            return redirect(url_for('tickets'))

    options = ''.join(f'<option value="{c["id"]}">{c["nombre"]}</option>' for c in clientes)
    content = f'''
        <section class="panel-card form-card">
            <form method="POST">
                <div class="form-grid">
                    <div><label>Cliente</label><select name="cliente_id" required><option value="">Seleccionar cliente</option>{options}</select></div>
                    <div><label>Título</label><input type="text" name="titulo" required></div>
                    <div><label>Prioridad</label><select name="prioridad"><option value="baja">Baja</option><option value="media" selected>Media</option><option value="alta">Alta</option></select></div>
                    <div><label>Responsable</label><input type="text" name="responsable" value="Equipo BUENA VISTA"></div>
                    <div class="full-width"><label>Descripción</label><textarea name="descripcion" required></textarea></div>
                    <div><label>Estado</label><select name="estado"><option value="abierto">Abierto</option><option value="en proceso">En proceso</option><option value="cerrado">Cerrado</option></select></div>
                </div>
                <div class="form-actions"><a href="/tickets" class="secondary-button">Cancelar</a><button type="submit" class="primary-button">Guardar</button></div>
            </form>
        </section>
    '''
    return course_html('Nuevo caso | BUENA VISTA GAS', 'Nuevo caso', content)


@app.route('/tickets/<int:ticket_id>')
@login_required
def ticket_detalle(ticket_id):
    ticket = fetch_one('''SELECT t.*, c.nombre AS cliente_nombre FROM casos_atencion t JOIN clientes c ON c.id = t.cliente_id WHERE t.id = %s''', (ticket_id,))
    if not ticket:
        flash('Caso no encontrado.', 'error')
        return redirect(url_for('tickets'))
    content = f'''
        <section class="panel-card detail-card">
            <div class="detail-header">
                <div><h3>{ticket['titulo']}</h3><p>{ticket['cliente_nombre']}</p></div>
                <a href="{url_for('ticket_editar', ticket_id=ticket_id)}" class="secondary-button">Editar</a>
            </div>
            <div class="info-grid">
                <div><strong>Prioridad:</strong> <span class="badge badge-priority-{ticket['prioridad']}">{ticket['prioridad']}</span></div>
                <div><strong>Estado:</strong> <span class="badge badge-{ticket['estado']}">{ticket['estado']}</span></div>
                <div><strong>Responsable:</strong> {ticket['responsable']}</div>
                <div class="full-width"><strong>Descripción:</strong> {ticket['descripcion']}</div>
            </div>
        </section>
    '''
    return course_html('Detalle caso | BUENA VISTA GAS', 'Detalle del caso', content)


@app.route('/tickets/<int:ticket_id>/editar', methods=['GET', 'POST'])
@login_required
def ticket_editar(ticket_id):
    ticket = fetch_one('SELECT * FROM casos_atencion WHERE id = %s', (ticket_id,))
    clientes = fetch_all('SELECT * FROM clientes ORDER BY nombre ASC')
    if not ticket:
        flash('Caso no encontrado.', 'error')
        return redirect(url_for('tickets'))
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        titulo = (request.form.get('titulo') or '').strip()
        descripcion = (request.form.get('descripcion') or '').strip()
        prioridad = request.form.get('prioridad') or 'media'
        estado = request.form.get('estado') or 'abierto'
        responsable = (request.form.get('responsable') or 'Equipo BUENA VISTA').strip()
        execute_query(
            'UPDATE casos_atencion SET cliente_id=%s, titulo=%s, descripcion=%s, prioridad=%s, estado=%s, responsable=%s WHERE id=%s',
            (cliente_id, titulo, descripcion, prioridad, estado, responsable, ticket_id),
        )
        flash('Caso actualizado.', 'success')
        return redirect(url_for('tickets'))

    options = ''.join(f'<option value="{c["id"]}" {"selected" if c["id"] == ticket["cliente_id"] else ""}>{c["nombre"]}</option>' for c in clientes)
    content = f'''
        <section class="panel-card form-card">
            <form method="POST">
                <div class="form-grid">
                    <div><label>Cliente</label><select name="cliente_id" required>{options}</select></div>
                    <div><label>Título</label><input type="text" name="titulo" value="{ticket['titulo']}" required></div>
                    <div><label>Prioridad</label><select name="prioridad"><option value="baja" {'selected' if ticket['prioridad']=='baja' else ''}>Baja</option><option value="media" {'selected' if ticket['prioridad']=='media' else ''}>Media</option><option value="alta" {'selected' if ticket['prioridad']=='alta' else ''}>Alta</option></select></div>
                    <div><label>Responsable</label><input type="text" name="responsable" value="{ticket['responsable'] or 'Equipo BUENA VISTA'}"></div>
                    <div class="full-width"><label>Descripción</label><textarea name="descripcion" required>{ticket['descripcion']}</textarea></div>
                    <div><label>Estado</label><select name="estado"><option value="abierto" {'selected' if ticket['estado']=='abierto' else ''}>Abierto</option><option value="en proceso" {'selected' if ticket['estado']=='en proceso' else ''}>En proceso</option><option value="cerrado" {'selected' if ticket['estado']=='cerrado' else ''}>Cerrado</option></select></div>
                </div>
                <div class="form-actions"><a href="{url_for('tickets')}" class="secondary-button">Cancelar</a><button type="submit" class="primary-button">Guardar</button></div>
            </form>
        </section>
    '''
    return course_html('Editar caso | BUENA VISTA GAS', 'Editar caso', content)


@app.route('/tickets/<int:ticket_id>/eliminar', methods=['POST'])
@login_required
def ticket_eliminar(ticket_id):
    execute_query('DELETE FROM casos_atencion WHERE id = %s', (ticket_id,))
    flash('Caso eliminado.', 'success')
    return redirect(url_for('tickets'))


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
