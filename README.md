# Telegram Media Bot

Un bot de Telegram para gestionar películas y series de TV con integración TMDB. El bot puede indexar archivos multimedia, almacenarlos en una base de datos local y permitir a los usuarios buscarlos y descargarlos.

## Características
- Indexa archivos multimedia desde un grupo de Telegram designado
- Almacena la información de los archivos en una base de datos SQLite local
- Integración con la API de TMDB para obtener metadatos de películas y series
- Publica automáticamente en un canal con pósters y descripciones
- Botones inline para descargar contenidos
- Controles de administración completos
- Soporte para series de TV con gestión de episodios
- Procesamiento automático de nombres de archivos
- Búsqueda inteligente en TMDB
- Eliminación segura de contenidos

## Requisitos
- Python 3.7+
- Token de Bot de Telegram (obtener de [@BotFather](https://t.me/BotFather))
- API ID y Hash de Telegram (obtener de [Telegram Apps](https://my.telegram.org/))
- Clave de API de TMDB (obtener de [TMDB](https://www.themoviedb.org/settings/api))

## Instalación en VPS

1. Clona este repositorio:
   ```bash
   git clone https://github.com/holavida/Media.git
   cd Media
   ```

2. Crea un entorno virtual y actívalo:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instala los paquetes requeridos:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura el bot:
   - Copia `.env.example` a `.env`
   - Edita el archivo `.env` con tus credenciales

5. Ejecuta el bot en segundo plano:
   ```bash
   nohup python bot.py &
   ```

## Configuración

Edita el archivo `.env` con tus credenciales:

- `BOT_TOKEN`: Token de tu Bot de Telegram
- `API_ID`: Tu API ID de Telegram
- `API_HASH`: Tu API Hash de Telegram
- `ADMIN_ID`: Tu ID de usuario de Telegram (para comandos de admin)
- `DATABASE_GROUP_ID`: ID del chat del grupo de base de datos
- `OFFICIAL_CHANNEL_ID`: ID del chat del canal oficial
- `TMDB_API_KEY`: Tu clave de API de TMDB

## Configuración de Grupos y Canales de Telegram

1. Crea un grupo privado para tu base de datos de medios
2. Crea un canal público para distribución de contenidos
3. Añade tu bot como administrador a ambos grupos con estos permisos:
   - Para el grupo de base de datos: Leer mensajes, Enviar mensajes, Editar mensajes
   - Para el canal oficial: Enviar mensajes, Editar mensajes

## Uso

### Comandos de Usuario
- `/start` - Iniciar el bot
- `/search <consulta>` - Buscar películas o series
- `/help` - Mostrar mensaje de ayuda

### Comandos de Administrador
- `/add_movie <tmdb_id>` - Añadir una película por ID de TMDB
- `/add_series <tmdb_id>` - Añadir una serie por ID de TMDB
- `/delete_media <media_id>` - Eliminar contenido por ID
- `/delete_all confirmar` - Eliminar toda la base de datos
- `/stats` - Mostrar estadísticas de la base de datos

### Cómo Funciona

1. Sube archivos de medios a tu grupo de base de datos
2. El bot detectará el archivo y buscará automáticamente en TMDB
3. Selecciona la coincidencia correcta o introduce manualmente el ID de TMDB
4. El bot obtendrá los metadatos de TMDB y publicará en tu canal oficial
5. Los usuarios pueden buscar y descargar contenidos usando los botones inline

## Añadir Contenido

1. Sube un archivo de película o serie a tu grupo de base de datos
2. El bot mostrará resultados de búsqueda automatizados de TMDB
3. Selecciona la opción correcta o encuentra el ID de TMDB del contenido:
   - Para películas: Visita https://www.themoviedb.org/movie/[ID]
   - Para series: Visita https://www.themoviedb.org/tv/[ID]
4. Usa el comando de administrador apropiado con el ID

## Comandos Útiles

- Ver procesos del bot: `ps aux | grep bot.py`
- Detener el bot: `pkill -f bot.py`
- Ver logs: `tail -f nohup.out`

## Documentación Adicional

- [Instrucciones Detalladas](INSTRUCCIONES.md) - Guía completa de configuración y uso
- [Funcionalidades Avanzadas](FUNCIONALIDADES.md) - Características adicionales y personalización

## Contribuciones

Siéntete libre de hacer fork de este proyecto y enviar pull requests. Para cambios importantes, por favor abre primero un issue para discutir lo que te gustaría cambiar.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.