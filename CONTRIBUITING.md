# Guía de Contribución y Reglas del Proyecto GenAI

¡Bienvenidos al proyecto! [TBD]

Para no romper el código de los demás y cumplir con los requisitos técnicos, todos debemos seguir estas reglas **estrictas**:

## 1. Reglas de Git (Flujo de trabajo)
* **NUNCA** trabajes directamente en `main` ni en `develop`.
* Para empezar tu caso de uso, crea una rama desde `develop`: `git checkout -b feature/nombre-de-tu-caso`.
* Cuando termines o quieras revisión, sube tu rama (`git push origin feature/tu-rama`) y avisa al administrador del proyecto para hacer la integración a `develop`.

## 2. Reglas de Código y Rutas
* **Rutas relativas:** Todas las rutas utilizadas en el código deben ser rutas relativas. (Ej. `../data/raw/csv_files/`). ¡Nadie debe usar `C:/Users/...`!
* **Modularidad:** El notebook debe poder ejecutarse de principio a fin sin intervención manual. Si creas funciones largas de limpieza o modelos, guárdalas en archivos `.py` dentro de la carpeta `src/`.

## 3. Estructura de un Caso de Uso
TBD

## 📝 Tareas Pendientes (¡Elige la tuya!)
Mientras el Caso de Uso 1: TBD

* **Caso de Uso 2:** TBD

## 🔄 Cómo mantener tu rama actualizada con `develop` / `master`

A medida que avanza el proyecto, iremos subiendo scripts útiles (como `tools.py` o herramientas de scraping) a las ramas principales (`develop` o `master`). 

Para poder usar estas nuevas herramientas en tu propia rama **sin perder tu trabajo**, necesitas actualizar tu rama local. Sigue estos 4 sencillos pasos:

### Paso 1: Guarda tu trabajo actual
Antes de traer código de otros, asegúrate de que tu rama está "limpia" (sin archivos modificados sueltos).
```bash
git status
git add .
git commit -m "Guardo mi progreso antes de actualizar la rama"
```

### Paso 2: Descarga las novedades del servidor
Esto actualiza tu rama local con todo lo que ha pasado en el repositorio en la nube (GitHub, GitLab, etc.).
```bash
git fetch origin
```

### Paso 3: Actualiza tu versión local de la rama principal
Muévete a la rama principal y descárgate los últimos cambios.
```bash
git checkout main
git pull origin main
```

### Paso 4: Fusiona las novedades en TU rama
Vuelve a tu rama de trabajo y tráete todo lo nuevo que acaba de llegar a main.
```bash
# Cambia "mi-rama" por el nombre real de tu rama
git checkout mi-rama  
git merge main
```

⚠️ ¡Ayuda, tengo un conflicto de merge!
A veces, Git te avisará de que hay un "Conflicto" en el Paso 4. Esto es normal y solo significa que tú y otro compañero habéis modificado el mismo archivo en la misma línea.

Abre tu editor de código (ej. VS Code). Verás el archivo en rojo.

El editor te mostrará tu código y el código que viene de develop. Haz clic en "Aceptar cambios entrantes", "Aceptar ambos", o edítalo manualmente.

Guarda el archivo.

Dile a Git que el conflicto está resuelto:
```bash
# Cambia "mi-rama" por el nombre real de tu rama
git add nombre_del_archivo_resuelto.py
git commit -m "Resuelvo conflicto tras actualizar con main"
```