# 📄 Exam JSON Generator

**Exam JSON Generator** es una herramienta que convierte documentos `.DOCX` en archivos `.JSON`, siempre que sigan una estructura concreta predefinida.

---

## 📐 Formato de entrada

El documento `.docx` debe seguir el formato indicado en:

```
exam_json_generator/ejemplo_formato_valido.docx
```
**poetry run exam_json_generator --show-example**

> ⚠️ Es **muy importante** respetar los:
> - Saltos de línea
> - Espacios
> - Tildes
> - Ubicación exacta de las etiquetas

Una alteración en cualquiera de estos elementos podría provocar una interpretación incorrecta.

---

## 🚀 ¿Cómo se ejecuta?

1. Entra en el entorno Poetry:
```bash
poetry shell
```

2. Ejecuta el generador con:
```bash
poetry run exam_json_generator <carpeta_de_entrada> <carpeta_de_salida>
```

Ejemplo:
```bash
poetry run exam_json_generator exam_json_generator/assets exam_json_generator/output
```

---

## 📂 Estructura esperada

- **Entrada:** debes indicar por argumento la carpeta donde se encuentran los `.docx`.
- **Salida:** debes indicar por argumento la carpeta donde se guardarán los `.json`.

Ambas rutas deben pasarse como argumentos al ejecutar el comando.

---

## ✅ Requisitos

- Archivos de entrada en formato `.docx`
- Python 3.10+
- [Poetry](https://python-poetry.org/docs/) instalado

---

## 🧪 Validación automática

- El programa valida si la carpeta de entrada y salida existen.
- Si la carpeta de salida no existe, se creará automáticamente.

# Pip install

```bash
pip install exam_json_generator
```
