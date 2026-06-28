import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "clave_secreta_para_sesiones_digitalpro"

# Contraseña para entrar a tu panel de administración
ADMIN_PASSWORD = "digitalpro2030"

def conectar_db():
    conexion = sqlite3.connect("digitalpro.db")
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_db():
    """Crea la base de datos interna y añade los datos de fábrica si está vacía"""
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # 1. Tabla de Banners
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS banners (
            id INTEGER PRIMARY KEY,
            url_imagen TEXT, titulo TEXT, subtitulo TEXT
        )
    """)
    
    # 2. Tabla de Productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT, precio TEXT, categoria TEXT, descripcion TEXT, imagen TEXT
        )
    """)
    
    # 3. Tabla de Servicios Gratuitos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicios_gratuitos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT, descripcion TEXT
        )
    """)
    
    # 4. NUEVA: Tabla de Servicios Técnicos Especializados (Comerciales)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicios_tecnicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT, descripcion TEXT, icono TEXT
        )
    """)
    
    # Cargar datos iniciales por defecto solo si la base de datos es nueva
    cursor.execute("SELECT COUNT(*) FROM banners")
    if cursor.fetchone()[0] == 0:
        # Banners iniciales
        cursor.execute("INSERT INTO banners (id, url_imagen, titulo, subtitulo) VALUES (1, ?, ?, ?)",
                       ("https://images.unsplash.com/photo-1588702547919-26089e690ecc?w=1200", "Soporte Especializado", "Mantenimiento preventivo y correctivo de cómputo."))
        cursor.execute("INSERT INTO banners (id, url_imagen, titulo, subtitulo) VALUES (2, ?, ?, ?)",
                       ("https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200", "Equipos de Alta Calidad", "Laptops, impresoras y suministros con garantía."))
        cursor.execute("INSERT INTO banners (id, url_imagen, titulo, subtitulo) VALUES (3, ?, ?, ?)",
                       ("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1200", "Redes y Conectividad", "Instalación de redes Wi-Fi comerciales."))
        
        # Producto inicial
        cursor.execute("INSERT INTO productos (nombre, precio, categoria, descripcion, imagen) VALUES (?, ?, ?, ?, ?)",
                       ("Laptop Core i5 11va Gen", "S/ 2450", "computadora", "8GB RAM, 512GB SSD. Ideal para oficina.", "https://placehold.co/400x300"))
        
        # Regalos comunitarios iniciales
        cursor.execute("INSERT INTO servicios_gratuitos (nombre, descripcion) VALUES (?, ?)",
                       ("Diagnóstico Inicial de Equipos", "Revisamos tu computadora o impresora en nuestro taller sin costo de revisión."))
        cursor.execute("INSERT INTO servicios_gratuitos (nombre, descripcion) VALUES (?, ?)",
                       ("Asesoría de Compra Tecnológica", "Te ayudamos a elegir el equipo ideal según las necesidades de tu empresa o negocio."))
        
        # Servicios comerciales iniciales de tu negocio
        cursor.execute("INSERT INTO servicios_tecnicos (nombre, descripcion, icono) VALUES (?, ?, ?)",
                       ("Mantenimiento de Computadoras y Laptops", "Limpieza física interna, cambio de pasta térmica, eliminación de virus y optimización de sistema operativo para que tu negocio trabaje rápido.", "bi-cpu"))
        cursor.execute("INSERT INTO servicios_tecnicos (nombre, descripcion, icono) VALUES (?, ?, ?)",
                       ("Reparación y Configuración de Impresoras", "Soporte técnico integral para sistemas continuos, desatasco de papel, limpieza de cabezales y reseteo de almohadillas.", "bi-printer"))
        cursor.execute("INSERT INTO servicios_tecnicos (nombre, descripcion, icono) VALUES (?, ?, ?)",
                       ("Instalación de Redes y Conectividad", "Configuración de routers, cableado estructurado y expansión de señal Wi-Fi para asegurar la conexión de tus puntos de venta.", "bi-router"))
        
        conexion.commit()
        
    conexion.close()

inicializar_db()


# ==========================================
#             RUTAS PÚBLICAS
# ==========================================

@app.route('/')
def inicio():
    conexion = conectar_db()
    banners = conexion.execute("SELECT * FROM banners ORDER BY id ASC").fetchall()
    productos = conexion.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    # AHORA LEEMOS LOS SERVICIOS TÉCNICOS DESDE LA BASE DE DATOS
    servicios = conexion.execute("SELECT * FROM servicios_tecnicos ORDER BY id ASC").fetchall()
    conexion.close()
    return render_template('inicio.html', banners=banners, productos=productos, servicios=servicios)

@app.route('/servicios-gratuitos')
def servicios_gratuitos():
    conexion = conectar_db()
    servicios_gratis = conexion.execute("SELECT * FROM servicios_gratuitos ORDER BY id DESC").fetchall()
    conexion.close()
    return render_template('servicios_gratuitos.html', servicios=servicios_gratis)


# ==========================================
#         RUTAS DE ADMINISTRACIÓN
# ==========================================

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if 'admin_autenticado' in session:
        return redirect(url_for('admin_panel'))
        
    if request.method == 'POST':
        password_ingresada = request.form.get('password')
        if password_ingresada == ADMIN_PASSWORD:
            session['admin_autenticado'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash("Contraseña incorrecta", "danger")
            
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if 'admin_autenticado' not in session:
        return redirect(url_for('admin_login'))
        
    conexion = conectar_db()
    banners = conexion.execute("SELECT * FROM banners ORDER BY id ASC").fetchall()
    productos = conexion.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    servicios_gratis = conexion.execute("SELECT * FROM servicios_gratuitos ORDER BY id DESC").fetchall()
    servicios_t_especializados = conexion.execute("SELECT * FROM servicios_tecnicos ORDER BY id DESC").fetchall()
    conexion.close()
    return render_template('admin_panel.html', banners=banners, productos=productos, servicios_gratis=servicios_gratis, servicios_tecnicos=servicios_t_especializados)

@app.route('/admin/agregar-producto', methods=['POST'])
def agregar_producto():
    if 'admin_autenticado' not in session: return redirect(url_for('admin_login'))
    
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    categoria = request.form.get('categoria')
    descripcion = request.form.get('descripcion')
    imagen = request.form.get('imagen') or "https://placehold.co/400x300"
    
    conexion = conectar_db()
    conexion.execute("INSERT INTO productos (nombre, precio, categoria, descripcion, imagen) VALUES (?, ?, ?, ?, ?)",
                     (nombre, precio, categoria, descripcion, imagen))
    conexion.commit()
    conexion.close()
    flash("Producto agregado exitosamente", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/eliminar-producto/<int:id>')
def eliminar_producto(id):
    if 'admin_autenticado' not in session: return redirect(url_for('admin_login'))
    
    conexion = conectar_db()
    conexion.execute("DELETE FROM productos WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()
    flash("Producto eliminado correctamente", "warning")
    return redirect(url_for('admin_panel'))

@app.route('/admin/agregar-servicio-gratis', methods=['POST'])
def agregar_servicio_gratis():
    if 'admin_autenticado' not in session: return redirect(url_for('admin_login'))
    
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    
    conexion = conectar_db()
    conexion.execute("INSERT INTO servicios_gratuitos (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
    conexion.commit()
    conexion.close()
    flash("Nuevo servicio gratuito publicado", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/eliminar-servicio-gratis/<int:id>')
def eliminar_servicio_gratis(id):
    if 'admin_autenticado' not in session: return redirect(url_for('admin_login'))
    
    conexion = conectar_db()
    conexion.execute("DELETE FROM servicios_gratuitos WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()
    flash("Servicio gratuito eliminado", "warning")
    return redirect(url_for('admin_panel'))

# --- NUEVA RUTA: AGREGAR SERVICIO TÉCNICO PROFESIONAL ---
@app.route('/admin/agregar-servicio-tecnico', methods=['POST'])
def agregar_servicio_tecnico():
    if 'admin_autenticado' not in session: return redirect(url_for('admin_login'))
    
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    icono = request.form.get('icono') or "bi-tools"
    
    conexion = conectar_db()
    conexion.execute("INSERT INTO servicios_tecnicos (nombre, descripcion, icono) VALUES (?, ?, ?)", (nombre, descripcion, icono))
    conexion.commit()
    conexion.close()
    flash("Servicio Técnico Especializado agregado con éxito", "success")
    return redirect(url_for('admin_panel'))

# --- NUEVA RUTA: ELIMINAR SERVICIO TÉCNICO PROFESIONAL ---
@app.route('/admin/eliminar-servicio-tecnico/<int:id>')
def eliminar_servicio_tecnico(id):
    if 'admin_autenticado' not in session: return redirect(url_for('admin_login'))
    
    conexion = conectar_db()
    conexion.execute("DELETE FROM servicios_tecnicos WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()
    flash("Servicio Técnico retirado de la cartelera", "warning")
    return redirect(url_for('admin_panel'))

@app.route('/admin/actualizar-banner/<int:id>', methods=['POST'])
def actualizar_banner(id):
    if 'admin_autenticado' not in session: return redirect(url_for('admin_login'))
    
    url_imagen = request.form.get('url_imagen')
    titulo = request.form.get('titulo')
    subtitulo = request.form.get('subtitulo')
    
    conexion = conectar_db()
    conexion.execute("UPDATE banners SET url_imagen = ?, titulo = ?, subtitulo = ? WHERE id = ?", 
                     (url_imagen, titulo, subtitulo, id))
    conexion.commit()
    conexion.close()
    flash(f"Banner #{id} actualizado correctamente", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/restaurar-banners')
def restaurar_banners():
    if 'admin_autenticado' not in session: return redirect(url_for('admin_login'))
    
    conexion = conectar_db()
    conexion.execute("DELETE FROM banners")
    conexion.execute("INSERT INTO banners (id, url_imagen, titulo, subtitulo) VALUES (1, ?, ?, ?)",
                     ("https://images.unsplash.com/photo-1588702547919-26089e690ecc?w=1200", "Soporte Especializado", "Mantenimiento preventivo y correctivo de cómputo."))
    conexion.execute("INSERT INTO banners (id, url_imagen, titulo, subtitulo) VALUES (2, ?, ?, ?)",
                     ("https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200", "Equipos de Alta Calidad", "Laptops, impresoras y suministros con garantía."))
    conexion.execute("INSERT INTO banners (id, url_imagen, titulo, subtitulo) VALUES (3, ?, ?, ?)",
                     ("https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1200", "Redes y Conectividad", "Instalación de redes Wi-Fi comerciales."))
    conexion.commit()
    conexion.close()
    flash("Banners restablecidos originalmente", "info")
    return redirect(url_for('admin_panel'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_autenticado', None)
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(debug=True)