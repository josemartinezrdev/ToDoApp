# Importaciones necesarias

import json
import tkinter as tk
from tkinter import messagebox
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DB

Base = declarative_base()

# Creacion de la entidad

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    desc = Column(String, nullable=False)
    completada = Column(Boolean, default=False)

# Creacion de la db y la entidad anteriormente establecida

db = create_engine("sqlite:///tasks.db")
Base.metadata.create_all(db) #- Crea todas las tablas

# Creacion de la session para acceder a la db

Session = sessionmaker(bind=db)
session = Session()


# Principal

class ToDoApp:

    def __init__(self, root):

        # Ventana

        self.root = root
        self.root.title("Gestion de Tareas")

        ventana_ancho = 400
        ventana_alto = 580

        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()

        pos_x = (pantalla_ancho // 2) - (ventana_ancho // 2)
        pos_y = (pantalla_alto // 2) - (ventana_alto // 2)

        self.root.geometry(f"{ventana_ancho}x{ventana_alto}+{pos_x}+{pos_y}")

        # Título tarea

        self.title_label = tk.Label(root, text="Título Tarea", font=("Arial", 14))
        self.title_label.pack(pady=6)

        self.title_entry = tk.Entry(root, width=50)
        self.title_entry.pack(pady=6)

        # Descripción tarea

        self.desc_label = tk.Label(root, text="Descripción", font=("Arial", 14))
        self.desc_label.pack(pady=6)

        self.desc_entry = tk.Entry(root, width=50)
        self.desc_entry.pack(pady=6)

        # Añadir tarea a DB

        self.add_button = tk.Button(root, text="Añadir", command=self.addTask)
        self.add_button.pack(pady=6)

        # Lista tareas

        self.task_listbox = tk.Listbox(root, width=50, height=15)   
        self.task_listbox.pack(pady=10)

        # Marcar tarea completada en DB

        self.completed_button = tk.Button(root, text="Completar Tarea", command=self.completarTask)
        self.completed_button.pack(pady=5)

        # Eliminar tarea de DB

        self.delete_button = tk.Button(root, text="Eliminar Tarea", command=self.deleteTask)
        self.delete_button.pack(pady=5)

        # Guardar Lista en JSON

        self.save_button = tk.Button(root, text="Exportar a JSON", command=self.saveTaskJson)
        self.save_button.pack(pady=5)

        # Cargar Lista desde JSON

        self.load_button = tk.Button(root, text="Importar de JSON", command=self.loadTaskJson)
        self.load_button.pack(pady=5)

        # Cargar Lista desde DB

        self.loadTaskDb()


    def loadTaskDb(self):
        self.task_listbox.delete(0, tk.END)
        tasks = session.query(Task).all()
        for task in tasks:
            status = "Completada" if task.completada else "Pendiente"
            self.task_listbox.insert(tk.END,  f"{task.titulo} - {status} - {task.desc}")
        
    def addTask(self):
        titulo = self.title_entry.get()
        desc = self.desc_entry.get()

        if titulo and desc:
            task = Task(titulo=titulo, desc=desc)
            session.add(task)
            session.commit()

            self.loadTaskDb()
            self.title_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Entrada vacía", "Ingrese un titulo y una descripción")

    def completarTask(self):
        selected_task = self.task_listbox.curselection()

        if selected_task:
            task_id = selected_task[0] + 1
            task = session.query(Task).filter(Task.id == task_id).first()
            task.completada = True

            session.commit()
            self.loadTaskDb()
    
    def deleteTask(self):
        selected_task = self.task_listbox.curselection()

        if selected_task:
            task_id = selected_task[0] + 1
            task = session.query(Task).filter(Task.id == task_id).first()
            
            if task:
                session.delete(task)
                session.commit()
                self.loadTaskDb()
            else:
                messagebox.showerror("Tarea no encontrada", "La tarea seleccionada ya no exsiste en la DB")
        else:
            messagebox.showwarning("Sin seleccionar", "Selecciona una tarea para eliminar")
    
    def saveTaskJson(self):
        tasks = session.query(Task).all()
        formatoJson = [{"titulo": task.titulo, "desc": task.desc, "completada": task.completada} for task in tasks]
        with open("tasks_exports.json", "w") as file:
            json.dump(formatoJson, file, indent=4)
        messagebox.showinfo("Éxito", "Tareas guardadas en: tasks_exports.json")

    def loadTaskJson(self):
        try:
            with open("tasks_exports.json", "r") as file:
                tasks_lst = json.load(file)
            for task_data in tasks_lst:
                taskExist = session.query(Task).filter(Task.titulo == task_data["titulo"], Task.desc == task_data["desc"]).first()
                if not taskExist:
                    task = Task(**task_data) #- ** Toma las keys y las pasa como parametros al constructor de Task
                    session.add(task)
            session.commit()
            self.loadTaskDb()
            messagebox.showinfo("Éxito", "Tareas cargadas desde tasks_exports.json")
        except FileNotFoundError:
            messagebox.showerror("Archivo no encontrado", "No se pudo encontrar el archivo tasks_exports.json.")


if __name__ == "__main__":
    root = tk.Tk() #- Creacion de la ventana del ToDoApp.
    app = ToDoApp(root) #- Asociar la instacia de la aplicacion a la ventana.
    root.mainloop() #- Iniciar el bucle de la ventana.