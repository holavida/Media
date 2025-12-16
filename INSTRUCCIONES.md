# Instrucciones Detalladas para Configurar y Usar el Bot de Telegram

## 1. Requisitos Previos

Antes de comenzar, necesitas obtener las siguientes credenciales:

1. **Token del Bot de Telegram**:
   - Habla con [@BotFather](https://t.me/BotFather) en Telegram
   - Crea un nuevo bot con el comando `/newbot`
   - Guarda el token que te proporciona

2. **API ID y API Hash de Telegram**:
   - Ve a [Telegram Apps](https://my.telegram.org/)
   - Inicia sesión con tu número de teléfono
   - Crea una nueva aplicación
   - Obtén tu `api_id` y `api_hash`

3. **Clave de API de TMDB**:
   - Regístrate en [The Movie Database](https://www.themoviedb.org/)
   - Ve a Settings > API
   - Solicita una clave de API

## 2. Configuración de Grupos y Canales

1. **Grupo de Base de Datos**:
   - Crea un grupo privado en Telegram
   - Este será donde subirás los archivos de películas/series
   - Agrega el bot como administrador con permisos para leer y enviar mensajes

2. **Canal Oficial**:
   - Crea un canal público o privado
   - Aquí se publicará automáticamente la ficha de cada contenido
   - Agrega el bot como administrador con permisos para publicar

## 3. Configuración del Bot

1. Copia el archivo `.env.example` a `.env`:
   ```
   cp .env.example .env
   ```

2. Edita el archivo `.env` y completa los valores:
   ```
   # Telegram Bot Configuration
   BOT_TOKEN=tu_token_aqui
   API_ID=tu_api_id_aqui
   API_HASH=tu_api_hash_aqui

   # Admin Configuration (tu ID de Telegram)
   ADMIN_ID=tu_id_de_usuario

   # Group/Channel IDs
   DATABASE_GROUP_ID=id_del_grupo_de_base_de_datos
   OFFICIAL_CHANNEL_ID=id_del_canal_oficial

   # TMDB Configuration
   TMDB_API_KEY=tu_clave_de_api_de_tmdb
   ```

## 4. Obtener los IDs de Grupos/Canales

Para obtener los IDs:

1. Añade el bot [@username_to_id_bot](https://t.me/username_to_id_bot) a tus grupos/canales
2. Envía el comando `/about` en cada uno
3. El bot te responderá con el ID correspondiente

## 5. Instalación y Ejecución

1. Clona el repositorio:
   ```bash
   git clone <url_del_repositorio>
   cd telegram-media-bot
   ```

2. Crea un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecuta el bot:
   ```bash
   python bot.py
   ```

## 6. Uso del Bot

### Para Usuarios Normales:
- `/start` - Mensaje de bienvenida
- `/search <nombre>` - Buscar películas o series
- `/help` - Mostrar ayuda

### Para Administradores:
- Subir archivos al grupo de base de datos
- El bot automáticamente buscará coincidencias en TMDB
- Seleccionar la película/serie correcta de los resultados
- O usar comandos manuales:
  - `/add_movie <tmdb_id>` - Añadir película por ID de TMDB
  - `/add_series <tmdb_id>` - Añadir serie por ID de TMDB
  - `/delete_media <id>` - Eliminar contenido específico
  - `/delete_all confirmar` - Eliminar toda la base de datos
  - `/stats` - Ver estadísticas

## 7. Funcionamiento Detallado

### Añadir Contenido:
1. Sube un archivo (película o episodio) al grupo de base de datos
2. El bot analiza el nombre del archivo y busca automáticamente en TMDB
3. Se muestran las coincidencias encontradas
4. Selecciona la opción correcta o ingresa manualmente el ID de TMDB
5. El bot publica automáticamente la ficha en el canal oficial

### Descargar Contenido:
1. Los usuarios ven las publicaciones en el canal oficial
2. Tocan el botón "📥 Descargar"
3. El bot envía directamente el archivo al usuario

### Gestión de Series:
- Para series, se pueden añadir múltiples episodios
- Cada episodio se asociará a la serie principal
- Al descargar, los usuarios podrán elegir qué episodio quieren

## 8. Solución de Problemas

### Problemas Comunes:

1. **El bot no responde en el grupo**:
   - Verifica que sea administrador
   - Confirma que los permisos sean correctos

2. **No se encuentran resultados en TMDB**:
   - Asegúrate de que el nombre del archivo sea claro
   - Usa el método manual con ID de TMDB

3. **Errores de conexión**:
   - Verifica las credenciales en `.env`
   - Confirma acceso a internet

### Soporte Adicional:
Si tienes problemas específicos, proporciona:
- Capturas de pantalla del error
- Los pasos que seguiste
- El contenido del archivo `.env` (sin las credenciales)