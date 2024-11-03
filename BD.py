import pyodbc as po
import tkinter as tk
from tkinter import Menu
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime


def conexion():
    try:
        conexion = po.connect(
            "DRIVER={Oracle ODBC Driver};"
            "DBQ=;"
            "UID=;"
            "PWD=;"
        )
        print("Conexión establecida con éxito.")
        return conexion
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return None

# Función para crear las tablas y agregar 10 tuplas predefinidas
def crear_tablas_y_datos(cursor):
    try:


        #cursor = conexion().cursor()

        # Eliminar tablas si existen
        cursor.execute("DROP TABLE DetallePedido CASCADE CONSTRAINTS")
        cursor.execute("DROP TABLE Pedido CASCADE CONSTRAINTS")
        cursor.execute("DROP TABLE Stock CASCADE CONSTRAINTS")

        cursor.execute("""
            CREATE TABLE Stock (
                Cproducto VARCHAR2(10) PRIMARY KEY,
                Cantidad NUMBER
            )
        """)
        cursor.execute("""
            CREATE TABLE Pedido (
                Cpedido NUMBER PRIMARY KEY,
                Ccliente VARCHAR2(50),
                Fecha_Pedido VARCHAR2(10)
            )
        """)
        cursor.execute("""
            CREATE TABLE DetallePedido (
                Cpedido NUMBER,
                Cproducto VARCHAR2(10),
                Cantidad NUMBER,
                PRIMARY KEY (Cpedido, Cproducto),
                FOREIGN KEY (Cpedido) REFERENCES Pedido(Cpedido),
                FOREIGN KEY (Cproducto) REFERENCES Stock(Cproducto)
            )
        """)
        
        # Inserción de 10 tuplas predefinidas
        datos = [
            ('Producto A', 100),
            ('Producto B', 50),
            ('Producto C', 75),
            ('Producto D', 120),
            ('Producto E', 30),
            ('Producto F', 60),
            ('Producto G', 200),
            ('Producto H', 80),
            ('Producto I', 150),
            ('Producto J', 90)
        ]
        cursor.executemany("INSERT INTO Stock (Cproducto, Cantidad) VALUES (?, ?)", datos)
        cursor.execute("COMMIT")
        messagebox.showinfo("Éxito", "Tablas creadas e insertadas 10 tuplas en Stock.")
    except po.Error as e:
        messagebox.showerror("Error", f"No se pudo crear la tabla: {e}")


def mostrar_todas_las_tablas(cursor):
    # Crear la ventana de Tkinter
    ventana = tk.Toplevel()
    ventana.title("Contenido de Tablas")
    ventana.geometry("800x600")

    # Crear un cuadro de texto para mostrar el contenido de todas las tablas
    text_widget = tk.Text(ventana, wrap="none")
    text_widget.pack(expand=True, fill="both")

    # Función auxiliar para insertar el contenido de una tabla en el widget Text
    def mostrar_tabla(nombre_tabla):
        text_widget.insert(tk.END, f"\n--- {nombre_tabla} ---\n")
        try:
            cursor.execute(f"SELECT * FROM {nombre_tabla}")
            filas = cursor.fetchall()
            
            if filas:
                # Obtener nombres de las columnas y añadirlos al cuadro de texto
                columnas = [desc[0] for desc in cursor.description]
                text_widget.insert(tk.END, "\t".join(columnas) + "\n")
                text_widget.insert(tk.END, "-" * 70 + "\n")

                # Insertar cada fila en el cuadro de texto
                for fila in filas:
                    text_widget.insert(tk.END, "\t".join(map(str, fila)) + "\n")
            else:
                text_widget.insert(tk.END, f"La tabla {nombre_tabla} está vacía.\n")
        except po.Error as e:
            text_widget.insert(tk.END, f"Error al mostrar la tabla {nombre_tabla}: {e}\n")

    # Llamar a la función mostrar_tabla para cada tabla
    mostrar_tabla('Stock')
    mostrar_tabla('Pedido')
    mostrar_tabla('DetallePedido')

    # Bloquear edición en el cuadro de texto
    text_widget.config(state="disabled")

    # Agregar scrollbars
    scrollbar_y = tk.Scrollbar(ventana, orient="vertical", command=text_widget.yview)
    scrollbar_y.pack(side="right", fill="y")
    text_widget.config(yscrollcommand=scrollbar_y.set)

    scrollbar_x = tk.Scrollbar(ventana, orient="horizontal", command=text_widget.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    text_widget.config(xscrollcommand=scrollbar_x.set)



# Función para mostrar el contenido de la tabla Stock
def mostrar_tablas(cursor):
    try:

        # Obtener contenido de la tabla Stock
        cursor.execute("SELECT * FROM Stock")
        registros_stock = cursor.fetchall()
        contenido_stock = "Tabla Stock:\nCproducto | Cantidad\n" + "-"*30 + "\n" + "\n".join([f"{row[0]:<10} | {row[1]:>5}" for row in registros_stock])
        
        # Obtener contenido de la tabla Pedido
        cursor.execute("SELECT * FROM Pedido")
        registros_pedido = cursor.fetchall()
        contenido_pedido = "Tabla Pedido:\nCpedido | Ccliente | Fecha_Pedido\n" + "-"*50 + "\n" + "\n".join([f"{row[0]:<7} | {row[1]:<18} | {row[2]}" for row in registros_pedido])
        
        # Obtener contenido de la tabla DetallePedido
        cursor.execute("SELECT * FROM DetallePedido")
        registros_detalle_pedido = cursor.fetchall()
        contenido_detalle_pedido = "Tabla DetallePedido:\nCpedido | Cproducto | Cantidad\n" + "-"*30 + "\n" + "\n".join([f"{row[0]:<7} | {row[1]:<10} | {row[2]:>5}" for row in registros_detalle_pedido])
        
        # Concatenar los contenidos de todas las tablas
        contenido_total = f"{contenido_stock}\n\n{contenido_pedido}\n\n{contenido_detalle_pedido}"
        
        # Mostrar todo en una sola ventana de mensaje
        messagebox.showinfo("Contenido de Todas las Tablas", contenido_total)

    except po.Error as e:
        messagebox.showerror("Error", f"No se pudo mostrar la tabla: {e}")


# Función para salir del programa y cerrar la conexión
def salir(cursor,root):
    if cursor and cursor.connection:
        print("Conexión cerrada con éxito.")
        cursor.connection.close()

    root.destroy()    

def obtener_nuevo_id_pedido(cursor):
    cursor.execute("SELECT MAX(Cpedido) FROM Pedido")
    row = cursor.fetchone()
    return (row[0] + 1) if row[0] is not None else 1

def dar_alta_nuevo_pedido(cursor):
    global CCproducto
    root = tk.Tk()
    id_pedido = obtener_nuevo_id_pedido(cursor)
    
    root.title(f"Nuevo Pedido: {int(id_pedido)}")
    root.geometry("900x800")
    
    # Campos de entrada para el cliente y la fecha del pedido
    tk.Label(root, text="Cliente:").pack()
    entry_cliente = tk.Entry(root)
    entry_cliente.pack(pady=5)
    #aux = [None]
    entry_fecha = datetime.today().strftime("%d/%m/%Y")
    

    # Función para insertar el pedido en la base de datos
    def confirmar_cliente():
        cliente = entry_cliente.get()
        fecha = entry_fecha
        
        if not cliente or not fecha:
            print("Por favor, complete todos los campos.")
            return
        
        try:
            cursor.execute("INSERT INTO Pedido (Cpedido, Ccliente, Fecha_Pedido) VALUES (?, ?, ?)",
                           (id_pedido, cliente, fecha))
            #cursor.execute("COMMIT")  # Confirma la inserción del pedido
            print(f"Pedido {int(id_pedido)} creado con éxito para el cliente {cliente} en la fecha {fecha}.")
            
            # Una vez creado el pedido, habilitamos los botones para agregar/eliminar detalles
            boton1.config(state=tk.NORMAL)
            boton2.config(state=tk.NORMAL)
            boton3.config(state=tk.NORMAL)
            boton4.config(state=tk.NORMAL)
        except po.Error as e:
            print("Error al crear el pedido:", e)
            cursor.connection.rollback()
            root.destroy()
            return

    # Botón para confirmar la creación del pedido
    boton_confirmar = tk.Button(root, text="Confirmar Cliente", command=confirmar_cliente)
    boton_confirmar.pack(pady=10)
    
    # Botones para detalles y finalizar el pedido, inicialmente deshabilitados
    boton1 = tk.Button(root, text="Añadir Detalles de Producto", command=lambda: boton_detalles_producto(cursor, id_pedido, root), state=tk.DISABLED)
    boton2 = tk.Button(root, text="Eliminar Detalles de Producto", command=lambda: boton_eliminar_detalle_producto(cursor, id_pedido), state=tk.DISABLED)
    boton3 = tk.Button(root, text="Cancelar Pedido", command=lambda: boton_cancelar_pedido(cursor, id_pedido, root), state=tk.DISABLED)
    boton4 = tk.Button(root, text="Finalizar Pedido", command=lambda: boton_finalizar_pedido(cursor, id_pedido, root), state=tk.DISABLED)

    boton1.pack(pady=10)
    boton2.pack(pady=10)
    boton3.pack(pady=10)
    boton4.pack(pady=10)
    
    root.mainloop()


CCproducto = None


def boton_detalles_producto(cursor, id_pedido, parent_root):
    try:
        root = tk.Toplevel(parent_root)
        root.title("Detalles de Producto")
        root.geometry("900x800")
        
        label1 = tk.Label(root, text="ID del Producto:")
        label1.pack(pady=5)
        entry1 = tk.Entry(root)
        entry1.pack(pady=5)

        label2 = tk.Label(root, text="Cantidad:")
        label2.pack(pady=5)
        entry2 = tk.Entry(root)
        entry2.pack(pady=5)
        

        boton1 = tk.Button(root, text="Añadir detalles", command=lambda: hay_stock(entry1, entry2, cursor, id_pedido, root))
        boton1.pack(pady=10)

    except po.Error as e:
        print("Error al conectar a la base de datos:", e)

def hay_stock(entry1, entry2, cursor, id_pedido, root):
    try:
        global CCproducto
        CCproducto = entry1.get().strip()
        cantidad_stock = cursor.execute("SELECT Cantidad FROM Stock WHERE Cproducto = ?", (entry1.get(),)).fetchone()
        if cantidad_stock and cantidad_stock[0] >= int(entry2.get()):
            cursor.execute("INSERT INTO DetallePedido (Cpedido, Cproducto, Cantidad) VALUES (?, ?, ?)", (id_pedido, entry1.get(), entry2.get()))
            cursor.execute("UPDATE Stock SET Cantidad = Cantidad - ? WHERE Cproducto = ?", (entry2.get(), entry1.get()))
            print("Detalle de pedido agregado con éxito")
        else:
            print("No hay stock suficiente")
    except po.Error as e:
        cursor.connection.rollback()
        print("Error al procesar la transacción:", e)
    finally:
        mostrar_todas_las_tablas(cursor)
        root.destroy()


def cancelar_pedido_y_restaurar_stock(cursor, pedido_id):
    try:
        # Verificar si existen detalles para el pedido
        query_detalles = "SELECT Cproducto, Cantidad FROM DetallePedido WHERE Cpedido = ?"
        cursor.execute(query_detalles, (pedido_id,))
        detalles = cursor.fetchall()

        # Si hay detalles, restaurar el stock
        if detalles:
            for detalle in detalles:
                producto_id, cantidad = detalle

                # Restaurar el stock de cada producto
                query_actualizar_stock = """
                    UPDATE Stock
                    SET Cantidad = Cantidad + ?
                    WHERE Cproducto = ?
                """
                cursor.execute(query_actualizar_stock, (cantidad, producto_id))

            # Borrar los detalles del pedido
            query_borrar_detalles = "DELETE FROM DetallePedido WHERE Cpedido = ?"
            cursor.execute(query_borrar_detalles, (pedido_id,))

            # Confirmar cambios
            cursor.commit()
            print(f"Pedido {int(pedido_id)} cancelado y stock restaurado.")

        else:
            print(f"No hay detalles para el pedido {int(pedido_id)}; no se requiere restaurar el stock.")

    except po.Error as e:
        print(f"Error al cancelar el pedido y restaurar el stock: {e}")


def borrar_fila(cursor, nombre_tabla, columna_id, valor_id):
    try:
        # Sentencia SQL para eliminar la fila específica
        query = f"DELETE FROM {nombre_tabla} WHERE {columna_id} = ?"
        cursor.execute(query, (valor_id,))
        cursor.commit()  # Asegurarse de que el cambio se guarde en la base de datos
        #print(f"Fila con {columna_id} = {valor_id} eliminada de la tabla {nombre_tabla}.")
    except po.Error as e:
        print(f"Error al eliminar la fila: {e}")

def boton_eliminar_detalle_producto(cursor, id_pedido):
    global CCproducto
    try:
        # Obtener los detalles del pedido antes de eliminar
        cursor.execute("SELECT Cproducto, Cantidad FROM DetallePedido WHERE Cpedido = ?", (id_pedido,))
        detalles = cursor.fetchall()

        # Eliminar los detalles del pedido
        cursor.execute("DELETE FROM DetallePedido WHERE Cpedido = ?", (id_pedido,))

        # Restaurar cantidades en el Stock
        for detalle in detalles:
            cproducto, cantidad = detalle
            cursor.execute("UPDATE Stock SET Cantidad = Cantidad + ? WHERE Cproducto = ?", (cantidad, cproducto))

        # Confirmar cambios
        cursor.connection.commit()
        print("Detalle de pedido eliminado y stock restaurado con éxito.")
        
        # Mostrar todas las tablas
        mostrar_todas_las_tablas(cursor)

    except po.Error as e:
        cursor.connection.rollback()
        print("Error al eliminar el detalle de pedido o al restaurar el stock:", e)




def boton_cancelar_pedido(cursor, id_pedido, root):
    try:
        cursor.connection.rollback()
        borrar_fila(cursor,"Pedido","Cpedido",id_pedido)
        cancelar_pedido_y_restaurar_stock(cursor,id_pedido)
        print("Pedido cancelado con éxito")
    except po.Error as e:
        print("Error al cancelar el pedido:", e)
    finally:
        mostrar_todas_las_tablas(cursor)
        root.destroy()

def boton_finalizar_pedido(cursor, id_pedido, root):        
    try:
        cursor.connection.commit()
        print("Pedido finalizado con éxito")
    except po.Error as e:
        print("Error al finalizar el pedido:", e)
    finally:
        root.destroy()

def borrar_tablas(cursor, root):
    if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas borrar todas las tablas? Esta acción no se puede deshacer."):
        try:
            cursor.execute("DROP TABLE DetallePedido")
            cursor.execute("DROP TABLE Pedido")
            cursor.execute("DROP TABLE Stock")
            cursor.connection.commit()
            print("Tablas borradas con éxito")
            messagebox.showinfo("Éxito", "Tablas borradas con éxito.")
            root.destroy()
        except po.Error as e:
            print("Error al borrar tablas:", e)
            messagebox.showerror("Error", f"No se pudieron borrar las tablas: {e}")


if __name__ == "__main__":
    # Configuración de la ventana principal
    conec = conexion()
    cursor = conec.cursor()
    root = tk.Tk()
    root.title("Gestión de Base de Datos")
    root.geometry("900x800")
    root.config(bg="#f0f0f0")

    # Estilo de los botones
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12), padding=10)
    style.map("TButton", foreground=[("active", "#ffffff")], background=[("active", "#007acc")])

    # Título y botones centrados
    frame = ttk.Frame(root, padding=20, relief="flat")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(frame, text="Gestión de Base de Datos", font=("Arial", 16, "bold")).pack(pady=10)

    ttk.Button(frame, text="Crear Tablas e Insertar Datos", command=lambda: crear_tablas_y_datos(cursor)).pack(pady=5, fill="x")
    ttk.Button(frame, text="Dar de Alta Nuevo Pedido", command=lambda: dar_alta_nuevo_pedido(cursor)).pack(pady=5, fill="x")
    ttk.Button(frame, text="Mostrar Contenido de Tablas", command=lambda: mostrar_tablas(cursor)).pack(pady=5, fill="x")
    ttk.Button(frame, text="Salir", command=lambda: salir(cursor, root)).pack(pady=5, fill="x")

    ##Este boton es para borrar las tablas al comienzo del inicio, sirve para depuracion
    #ttk.Button(frame, text="Borrar Tablas", command=borrar_tablas(conexion().cursor(), root)).pack(pady=5, fill="x")

    # Ejecutar la interfaz
    root.mainloop()
