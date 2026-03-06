# Sistema RFID - Interfaz web

Instrucciones rápidas:

- Crear entorno virtual e instalar dependencias:

```powershell
py -3 -m venv venv
& venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Configurar base de datos MySQL (opcional): exportar la variable de entorno `DATABASE_URL` con formato:

```
mysql+pymysql://USER:PASS@HOST:PORT/DBNAME
```

Si no se establece `DATABASE_URL`, la aplicación usa `sqlite:///cards.db` localmente.

- Ejecutar la aplicación:

```powershell
python -m app.main
```

Uso:
- Abra `http://localhost:5000` en su navegador.
- Use "Leer tarjeta" para enviar un UID (esto simula la lectura; para integrar hardware haga POST a `/read_rfid`).
- Use "Configurar tarjeta" para asignar propietario y áreas.
- Los datos se guardan en la base de datos configurada.

Notas específicas para la base de datos llamada `project`:

- Crear la base de datos y un usuario (ejemplo, ajusta `USER` y `PASS`):

```sql
CREATE DATABASE project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'miuser'@'localhost' IDENTIFIED BY 'mipassword';
GRANT ALL PRIVILEGES ON project.* TO 'miuser'@'localhost';
FLUSH PRIVILEGES;
```

- Establecer la variable de entorno `DATABASE_URL` en PowerShell (temporal para la sesión):

```powershell
$env:DATABASE_URL = "mysql+pymysql://miuser:mipassword@localhost:3306/project"
```

- Para establecerla permanentemente en Windows (desde CMD):

```cmd
setx DATABASE_URL "mysql+pymysql://miuser:mipassword@localhost:3306/project"
```

- Alternativamente, en PowerShell para la sesión actual use el comando anterior; para persistir en perfil de PowerShell, añada la línea al archivo de perfil.

Una vez configurada la variable `DATABASE_URL`, inicie la app normalmente y ésta usará la base `project`.
