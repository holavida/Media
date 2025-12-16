# Funcionalidades Adicionales

## Añadir Episodios a una Serie

Para añadir episodios individuales a una serie existente, puedes usar el siguiente proceso:

1. Sube el archivo del episodio al grupo de base de datos
2. El bot reconocerá que es un episodio por el formato (SXXEXX)
3. Se asociará automáticamente a la serie correspondiente en la base de datos
4. Se publicará en el canal oficial con la opción de descarga

## Comandos Especiales para Series

- `/add_season <serie_id> <temporada>` - Añadir una temporada completa
- `/list_episodes <serie_id>` - Listar todos los episodios de una serie
- `/delete_episode <episode_id>` - Eliminar un episodio específico

## Personalización del Bot

Puedes personalizar varios aspectos del bot editando el archivo `config.py`:

1. Mensajes del bot
2. Formato de las fichas
3. Permisos de usuarios
4. Comandos adicionales

## Integración con Otros Servicios

El bot puede extenderse fácilmente para integrarse con:
- Servidores de streaming
- APIs de subtítulos
- Sistemas de notificaciones
- Bases de datos externas

## Seguridad y Privacidad

- Todas las credenciales se almacenan en variables de entorno
- El código no contiene información sensible
- Los archivos se almacenan de forma segura
- Solo los administradores pueden realizar acciones críticas