# 📘 Documentación Técnica - Microservicio Clasificación de Comentarios

## 1. 🎯 Arquitectura

Este proyecto forma parte de una arquitectura basada en microservicios con comunicación RESTful. En el diagrama general del sistema se representa su posición, sin embargo, este documento se enfoca únicamente en el microservicio **Clasificación de Comentarios**.

### Documentación del proyecto
https://drive.google.com/file/d/1N8t7S13OS_vdBOBE9nqIMqN_AeX5BwkB/view?usp=sharing
---

## 2. 🧩 Patrón de diseño

El patrón de diseño utilizado es **MVC** (Modelo - Vista - Controlador). El componente principal que implementa este patrón es `main.py`, el cual expone las APIs para la clasificación de comentarios. Además, se incluye un modelo de base de datos que respalda el procesamiento y almacenamiento de la información.

---

## 3. ⚙️ Instalación y Configuración

### 3.1 Requisitos Previos

- Python 3.9 o superior (**3.10 recomendado**)
- `pip` (gestor de paquetes de Python)
- `virtualenv` (opcional pero recomendado)
- Credenciales de **Firebase Database**

### 3.2 Instalación

```bash
# Clona el repositorio
git clone https://github.com/Kalli21/ClasificadorTexto.git
cd ClasificadorTexto

# (Opcional) Crea y activa un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala las dependencias
pip install -r requirements.txt

# Corre el proyecto
uvicorn main:app --reload
