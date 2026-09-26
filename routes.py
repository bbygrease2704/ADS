from functools import wraps

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database import get_connection


def query_all(sql, params=()):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def query_one(sql, params=()):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()


def execute_query(sql, params=()):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
    connection.close()


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)

    return wrapped


def register_routes(app):
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            if not username or not password:
                flash('Ingrese usuario y contraseña.', 'error')
                return render_template('login.html')

            user = query_one('SELECT * FROM usuarios WHERE username = %s', (username,))
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['nombre'] = user['nombre']
                flash('Bienvenido al sistema BUENA VISTA GAS.', 'success')
                return redirect(url_for('dashboard'))

            flash('Credenciales inválidas. Intente nuevamente.', 'error')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Sesión cerrada correctamente.', 'success')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        stats = {
            'clientes': query_one('SELECT COUNT(*) AS total FROM clientes')['total'],
            'servicios': query_one('SELECT COUNT(*) AS total FROM servicios_instalacion')['total'],
            'ventas': query_one('SELECT COUNT(*) AS total FROM ventas_gas')['total'],
            'casos': query_one('SELECT COUNT(*) AS total FROM casos_atencion')['total'],
        }
        clientes_recientes = query_all(
            'SELECT * FROM clientes ORDER BY created_at DESC LIMIT 5'
        )
        tickets_abiertos = query_all(
            'SELECT c.*, t.* FROM casos_atencion t JOIN clientes c ON c.id = t.cliente_id WHERE t.estado != %s ORDER BY t.created_at DESC LIMIT 5',
            ('cerrado',),
        )
        return render_template('dashboard.html', stats=stats, clientes_recientes=clientes_recientes, tickets_abiertos=tickets_abiertos)

    @app.route('/clientes')
    @login_required
    def clientes():
        q = request.args.get('q', '').strip()
        estado = request.args.get('estado', '').strip()
        sql = 'SELECT * FROM clientes WHERE 1=1'
        params = []
        if q:
            sql += ' AND (nombre LIKE %s OR documento LIKE %s OR telefono LIKE %s OR email LIKE %s)'
            search_param = f'%{q}%'
            params.extend([search_param, search_param, search_param, search_param])
        if estado:
            sql += ' AND estado = %s'
            params.append(estado)
        sql += ' ORDER BY created_at DESC'
        clientes_list = query_all(sql, tuple(params))
        return render_template('clientes.html', clientes=clientes_list, q=q, estado=estado)

    @app.route('/clientes/nuevo', methods=['GET', 'POST'])
    @login_required
    def cliente_nuevo():
        if request.method == 'POST':
            nombre = request.form.get('nombre', '').strip()
            documento = request.form.get('documento', '').strip()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            direccion = request.form.get('direccion', '').strip()
            tipo_cliente = request.form.get('tipo_cliente', 'residencial')
            estado = request.form.get('estado', 'activo')
            if not nombre or not documento:
                flash('Nombre y documento son obligatorios.', 'error')
                return render_template('cliente_form.html', cliente={}, mode='nuevo')
            execute_query(
                'INSERT INTO clientes (nombre, documento, telefono, email, direccion, tipo_cliente, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (nombre, documento, telefono, email, direccion, tipo_cliente, estado),
            )
            flash('Cliente registrado correctamente.', 'success')
            return redirect(url_for('clientes'))
        return render_template('cliente_form.html', cliente={}, mode='nuevo')

    @app.route('/clientes/<int:cliente_id>')
    @login_required
    def cliente_detalle(cliente_id):
        cliente = query_one('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
        if not cliente:
            flash('Cliente no encontrado.', 'error')
            return redirect(url_for('clientes'))
        servicios = query_all('SELECT * FROM servicios_instalacion WHERE cliente_id = %s ORDER BY fecha_instalacion DESC', (cliente_id,))
        ventas = query_all('SELECT * FROM ventas_gas WHERE cliente_id = %s ORDER BY fecha_venta DESC', (cliente_id,))
        tickets = query_all('SELECT * FROM casos_atencion WHERE cliente_id = %s ORDER BY created_at DESC', (cliente_id,))
        return render_template('cliente_detail.html', cliente=cliente, servicios=servicios, ventas=ventas, tickets=tickets)

    @app.route('/clientes/<int:cliente_id>/editar', methods=['GET', 'POST'])
    @login_required
    def cliente_editar(cliente_id):
        cliente = query_one('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
        if not cliente:
            flash('Cliente no encontrado.', 'error')
            return redirect(url_for('clientes'))
        if request.method == 'POST':
            nombre = request.form.get('nombre', '').strip()
            documento = request.form.get('documento', '').strip()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            direccion = request.form.get('direccion', '').strip()
            tipo_cliente = request.form.get('tipo_cliente', 'residencial')
            estado = request.form.get('estado', 'activo')
            if not nombre or not documento:
                flash('Nombre y documento son obligatorios.', 'error')
                return render_template('cliente_form.html', cliente=cliente, mode='editar')
            execute_query(
                'UPDATE clientes SET nombre=%s, documento=%s, telefono=%s, email=%s, direccion=%s, tipo_cliente=%s, estado=%s WHERE id=%s',
                (nombre, documento, telefono, email, direccion, tipo_cliente, estado, cliente_id),
            )
            flash('Cliente actualizado correctamente.', 'success')
            return redirect(url_for('clientes'))
        return render_template('cliente_form.html', cliente=cliente, mode='editar')

    @app.route('/clientes/<int:cliente_id>/eliminar', methods=['POST'])
    @login_required
    def cliente_eliminar(cliente_id):
        execute_query('DELETE FROM clientes WHERE id = %s', (cliente_id,))
        flash('Cliente eliminado.', 'success')
        return redirect(url_for('clientes'))

    @app.route('/servicios')
    @login_required
    def servicios():
        q = request.args.get('q', '').strip()
        estado = request.args.get('estado', '').strip()
        sql = '''SELECT s.*, c.nombre AS cliente_nombre FROM servicios_instalacion s JOIN clientes c ON c.id = s.cliente_id WHERE 1=1'''
        params = []
        if q:
            sql += ' AND (c.nombre LIKE %s OR s.tipo_servicio LIKE %s OR s.direccion LIKE %s)'
            search_param = f'%{q}%'
            params.extend([search_param, search_param, search_param])
        if estado:
            sql += ' AND s.estado = %s'
            params.append(estado)
        sql += ' ORDER BY s.fecha_instalacion DESC'
        servicios_list = query_all(sql, tuple(params))
        return render_template('servicios.html', servicios=servicios_list, q=q, estado=estado)

    @app.route('/servicios/nuevo', methods=['GET', 'POST'])
    @login_required
    def servicio_nuevo():
        clientes = query_all('SELECT * FROM clientes ORDER BY nombre ASC')
        if request.method == 'POST':
            cliente_id = request.form.get('cliente_id')
            tipo_servicio = request.form.get('tipo_servicio', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            direccion = request.form.get('direccion', '').strip()
            fecha_instalacion = request.form.get('fecha_instalacion', '')
            costo = request.form.get('costo', '0')
            estado = request.form.get('estado', 'pendiente')
            if not cliente_id or not tipo_servicio or not direccion or not fecha_instalacion:
                flash('Complete los campos obligatorios del servicio.', 'error')
                return render_template('servicio_form.html', servicio={}, clientes=clientes, mode='nuevo')
            execute_query(
                'INSERT INTO servicios_instalacion (cliente_id, tipo_servicio, descripcion, direccion, fecha_instalacion, costo, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (cliente_id, tipo_servicio, descripcion, direccion, fecha_instalacion, costo, estado),
            )
            flash('Servicio registrado.', 'success')
            return redirect(url_for('servicios'))
        return render_template('servicio_form.html', servicio={}, clientes=clientes, mode='nuevo')

    @app.route('/servicios/<int:servicio_id>')
    @login_required
    def servicio_detalle(servicio_id):
        servicio = query_one('''SELECT s.*, c.nombre AS cliente_nombre FROM servicios_instalacion s JOIN clientes c ON c.id = s.cliente_id WHERE s.id = %s''', (servicio_id,))
        if not servicio:
            flash('Servicio no encontrado.', 'error')
            return redirect(url_for('servicios'))
        return render_template('servicio_detail.html', servicio=servicio)

    @app.route('/servicios/<int:servicio_id>/editar', methods=['GET', 'POST'])
    @login_required
    def servicio_editar(servicio_id):
        clientes = query_all('SELECT * FROM clientes ORDER BY nombre ASC')
        servicio = query_one('SELECT * FROM servicios_instalacion WHERE id = %s', (servicio_id,))
        if not servicio:
            flash('Servicio no encontrado.', 'error')
            return redirect(url_for('servicios'))
        if request.method == 'POST':
            cliente_id = request.form.get('cliente_id')
            tipo_servicio = request.form.get('tipo_servicio', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            direccion = request.form.get('direccion', '').strip()
            fecha_instalacion = request.form.get('fecha_instalacion', '')
            costo = request.form.get('costo', '0')
            estado = request.form.get('estado', 'pendiente')
            execute_query(
                'UPDATE servicios_instalacion SET cliente_id=%s, tipo_servicio=%s, descripcion=%s, direccion=%s, fecha_instalacion=%s, costo=%s, estado=%s WHERE id=%s',
                (cliente_id, tipo_servicio, descripcion, direccion, fecha_instalacion, costo, estado, servicio_id),
            )
            flash('Servicio actualizado.', 'success')
            return redirect(url_for('servicios'))
        return render_template('servicio_form.html', servicio=servicio, clientes=clientes, mode='editar')

    @app.route('/servicios/<int:servicio_id>/eliminar', methods=['POST'])
    @login_required
    def servicio_eliminar(servicio_id):
        execute_query('DELETE FROM servicios_instalacion WHERE id = %s', (servicio_id,))
        flash('Servicio eliminado.', 'success')
        return redirect(url_for('servicios'))

    @app.route('/ventas')
    @login_required
    def ventas():
        q = request.args.get('q', '').strip()
        estado = request.args.get('estado', '').strip()
        sql = '''SELECT v.*, c.nombre AS cliente_nombre FROM ventas_gas v JOIN clientes c ON c.id = v.cliente_id WHERE 1=1'''
        params = []
        if q:
            sql += ' AND (c.nombre LIKE %s OR v.producto LIKE %s OR v.metodo_pago LIKE %s)'
            search_param = f'%{q}%'
            params.extend([search_param, search_param, search_param])
        if estado:
            sql += ' AND v.estado = %s'
            params.append(estado)
        sql += ' ORDER BY v.fecha_venta DESC'
        ventas_list = query_all(sql, tuple(params))
        return render_template('ventas.html', ventas=ventas_list, q=q, estado=estado)

    @app.route('/ventas/nuevo', methods=['GET', 'POST'])
    @login_required
    def venta_nueva():
        clientes = query_all('SELECT * FROM clientes ORDER BY nombre ASC')
        if request.method == 'POST':
            cliente_id = request.form.get('cliente_id')
            producto = request.form.get('producto', '').strip()
            cantidad = request.form.get('cantidad', '1')
            total = request.form.get('total', '0')
            metodo_pago = request.form.get('metodo_pago', 'efectivo')
            fecha_venta = request.form.get('fecha_venta', '')
            estado = request.form.get('estado', 'completado')
            if not cliente_id or not producto or not fecha_venta:
                flash('Complete los datos obligatorios para la venta.', 'error')
                return render_template('venta_form.html', venta={}, clientes=clientes, mode='nuevo')
            execute_query(
                'INSERT INTO ventas_gas (cliente_id, producto, cantidad, total, metodo_pago, fecha_venta, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (cliente_id, producto, cantidad, total, metodo_pago, fecha_venta, estado),
            )
            flash('Venta registrada correctamente.', 'success')
            return redirect(url_for('ventas'))
        return render_template('venta_form.html', venta={}, clientes=clientes, mode='nuevo')

    @app.route('/ventas/<int:venta_id>')
    @login_required
    def venta_detalle(venta_id):
        venta = query_one('''SELECT v.*, c.nombre AS cliente_nombre FROM ventas_gas v JOIN clientes c ON c.id = v.cliente_id WHERE v.id = %s''', (venta_id,))
        if not venta:
            flash('Venta no encontrada.', 'error')
            return redirect(url_for('ventas'))
        return render_template('venta_detail.html', venta=venta)

    @app.route('/ventas/<int:venta_id>/editar', methods=['GET', 'POST'])
    @login_required
    def venta_editar(venta_id):
        clientes = query_all('SELECT * FROM clientes ORDER BY nombre ASC')
        venta = query_one('SELECT * FROM ventas_gas WHERE id = %s', (venta_id,))
        if not venta:
            flash('Venta no encontrada.', 'error')
            return redirect(url_for('ventas'))
        if request.method == 'POST':
            cliente_id = request.form.get('cliente_id')
            producto = request.form.get('producto', '').strip()
            cantidad = request.form.get('cantidad', '1')
            total = request.form.get('total', '0')
            metodo_pago = request.form.get('metodo_pago', 'efectivo')
            fecha_venta = request.form.get('fecha_venta', '')
            estado = request.form.get('estado', 'completado')
            execute_query(
                'UPDATE ventas_gas SET cliente_id=%s, producto=%s, cantidad=%s, total=%s, metodo_pago=%s, fecha_venta=%s, estado=%s WHERE id=%s',
                (cliente_id, producto, cantidad, total, metodo_pago, fecha_venta, estado, venta_id),
            )
            flash('Venta actualizada.', 'success')
            return redirect(url_for('ventas'))
        return render_template('venta_form.html', venta=venta, clientes=clientes, mode='editar')

    @app.route('/ventas/<int:venta_id>/eliminar', methods=['POST'])
    @login_required
    def venta_eliminar(venta_id):
        execute_query('DELETE FROM ventas_gas WHERE id = %s', (venta_id,))
        flash('Venta eliminada.', 'success')
        return redirect(url_for('ventas'))

    @app.route('/tickets')
    @login_required
    def tickets():
        q = request.args.get('q', '').strip()
        estado = request.args.get('estado', '').strip()
        prioridad = request.args.get('prioridad', '').strip()
        sql = '''SELECT t.*, c.nombre AS cliente_nombre FROM casos_atencion t JOIN clientes c ON c.id = t.cliente_id WHERE 1=1'''
        params = []
        if q:
            sql += ' AND (c.nombre LIKE %s OR t.titulo LIKE %s OR t.descripcion LIKE %s)'
            search_param = f'%{q}%'
            params.extend([search_param, search_param, search_param])
        if estado:
            sql += ' AND t.estado = %s'
            params.append(estado)
        if prioridad:
            sql += ' AND t.prioridad = %s'
            params.append(prioridad)
        sql += ' ORDER BY t.created_at DESC'
        tickets_list = query_all(sql, tuple(params))
        return render_template('tickets.html', tickets=tickets_list, q=q, estado=estado, prioridad=prioridad)

    @app.route('/tickets/nuevo', methods=['GET', 'POST'])
    @login_required
    def ticket_nuevo():
        clientes = query_all('SELECT * FROM clientes ORDER BY nombre ASC')
        if request.method == 'POST':
            cliente_id = request.form.get('cliente_id')
            titulo = request.form.get('titulo', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            prioridad = request.form.get('prioridad', 'media')
            estado = request.form.get('estado', 'abierto')
            responsable = request.form.get('responsable', 'Equipo BUENA VISTA')
            if not cliente_id or not titulo or not descripcion:
                flash('Debe completar el cliente, título y descripción del caso.', 'error')
                return render_template('ticket_form.html', ticket={}, clientes=clientes, mode='nuevo')
            execute_query(
                'INSERT INTO casos_atencion (cliente_id, titulo, descripcion, prioridad, estado, responsable) VALUES (%s, %s, %s, %s, %s, %s)',
                (cliente_id, titulo, descripcion, prioridad, estado, responsable),
            )
            flash('Caso de atención registrado.', 'success')
            return redirect(url_for('tickets'))
        return render_template('ticket_form.html', ticket={}, clientes=clientes, mode='nuevo')

    @app.route('/tickets/<int:ticket_id>')
    @login_required
    def ticket_detalle(ticket_id):
        ticket = query_one('''SELECT t.*, c.nombre AS cliente_nombre FROM casos_atencion t JOIN clientes c ON c.id = t.cliente_id WHERE t.id = %s''', (ticket_id,))
        if not ticket:
            flash('Caso no encontrado.', 'error')
            return redirect(url_for('tickets'))
        return render_template('ticket_detail.html', ticket=ticket)

    @app.route('/tickets/<int:ticket_id>/editar', methods=['GET', 'POST'])
    @login_required
    def ticket_editar(ticket_id):
        clientes = query_all('SELECT * FROM clientes ORDER BY nombre ASC')
        ticket = query_one('SELECT * FROM casos_atencion WHERE id = %s', (ticket_id,))
        if not ticket:
            flash('Caso no encontrado.', 'error')
            return redirect(url_for('tickets'))
        if request.method == 'POST':
            cliente_id = request.form.get('cliente_id')
            titulo = request.form.get('titulo', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            prioridad = request.form.get('prioridad', 'media')
            estado = request.form.get('estado', 'abierto')
            responsable = request.form.get('responsable', 'Equipo BUENA VISTA')
            execute_query(
                'UPDATE casos_atencion SET cliente_id=%s, titulo=%s, descripcion=%s, prioridad=%s, estado=%s, responsable=%s WHERE id=%s',
                (cliente_id, titulo, descripcion, prioridad, estado, responsable, ticket_id),
            )
            flash('Caso actualizado.', 'success')
            return redirect(url_for('tickets'))
        return render_template('ticket_form.html', ticket=ticket, clientes=clientes, mode='editar')

    @app.route('/tickets/<int:ticket_id>/eliminar', methods=['POST'])
    @login_required
    def ticket_eliminar(ticket_id):
        execute_query('DELETE FROM casos_atencion WHERE id = %s', (ticket_id,))
        flash('Caso eliminado.', 'success')
        return redirect(url_for('tickets'))
