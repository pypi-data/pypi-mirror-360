# Lunch Money MCP Server

Un servidor MCP (Model Context Protocol) para la [API de Lunch Money](https://lunchmoney.dev), que permite a los asistentes de IA interactuar con tu cuenta de Lunch Money para gestionar transacciones, categorías, presupuestos y más.

## Características

Este servidor MCP proporciona acceso a las siguientes funcionalidades de Lunch Money:

- **Usuario**: Obtener información de la cuenta
- **Categorías**: Crear, leer, actualizar y eliminar categorías
- **Transacciones**: Gestionar transacciones (crear, leer, actualizar, filtrar)
- **Etiquetas**: Obtener todas las etiquetas
- **Activos**: Gestionar cuentas/activos
- **Presupuestos**: Obtener y actualizar presupuestos
- **Elementos recurrentes**: Obtener transacciones recurrentes
- **Cuentas Plaid**: Gestionar cuentas conectadas de Plaid
- **Criptomonedas**: Gestionar activos crypto

## Instalación Super Simple 🚀

### Opción 1: Instalación Automática (Más Fácil)

```bash
python install.py
```

Este script:
- ✅ Instala el paquete automáticamente
- ✅ Te pide tu token de Lunch Money
- ✅ Configura Claude Desktop automáticamente
- ✅ Todo listo para usar

### Opción 2: Instalación Manual

```bash
pip install lunchmoney-mcp
```

Luego añade esta configuración a tu archivo `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lunchmoney": {
      "command": "lunchmoney-mcp",
      "env": {
        "LUNCHMONEY_ACCESS_TOKEN": "tu_token_aqui"
      }
    }
  }
}
```

**¡Eso es todo!** 🎉 Tan simple como Playwright MCP.

### Obtén tu token de acceso:
1. Ve a [https://my.lunchmoney.app/developers](https://my.lunchmoney.app/developers)
2. Crea un nuevo token de acceso
3. Úsalo en la configuración de arriba

## Instalación desde el código fuente

Si prefieres instalar desde el código fuente:

1. **Clona el repositorio:**
   ```bash
   git clone <repository-url>
   cd lunchmoney-mcp
   ```

2. **Instala:**
   ```bash
   pip install -e .
   ```

3. **Configura en Claude Desktop:**
   ```json
   {
     "mcpServers": {
       "lunchmoney": {
         "command": "lunchmoney-mcp",
         "env": {
           "LUNCHMONEY_ACCESS_TOKEN": "tu_token_aqui"
         }
       }
     }
   }
   ```

### Ubicación del archivo de configuración:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Uso

Una vez configurado, puedes usar Claude Desktop para interactuar con tu cuenta de Lunch Money. Aquí algunos ejemplos:

### Ejemplos de uso

1. **Obtener información de usuario:**
   ```
   "Muéstrame la información de mi cuenta de Lunch Money"
   ```

2. **Ver todas las categorías:**
   ```
   "Lista todas mis categorías de Lunch Money"
   ```

3. **Crear una nueva categoría:**
   ```
   "Crea una nueva categoría llamada 'Entretenimiento' en Lunch Money"
   ```

4. **Ver transacciones recientes:**
   ```
   "Muéstrame las transacciones del último mes"
   ```

5. **Crear una transacción:**
   ```
   "Añade una transacción de $50 para 'Supermercado XYZ' en la categoría 'Comida'"
   ```

6. **Ver presupuesto:**
   ```
   "Muéstrame el resumen del presupuesto de este mes"
   ```

## Herramientas disponibles

### Usuario
- `get_user`: Obtener información del usuario y la cuenta

### Categorías
- `get_all_categories`: Obtener todas las categorías
- `get_single_category`: Obtener una categoría específica
- `create_category`: Crear una nueva categoría
- `update_category`: Actualizar una categoría existente
- `delete_category`: Eliminar una categoría

### Transacciones
- `get_all_transactions`: Obtener todas las transacciones (con filtros)
- `get_single_transaction`: Obtener una transacción específica
- `insert_transactions`: Insertar nuevas transacciones
- `update_transaction`: Actualizar una transacción existente

### Etiquetas
- `get_all_tags`: Obtener todas las etiquetas

### Activos
- `get_all_assets`: Obtener todos los activos/cuentas
- `create_asset`: Crear un nuevo activo/cuenta
- `update_asset`: Actualizar un activo existente

### Presupuestos
- `get_budget_summary`: Obtener resumen del presupuesto
- `upsert_budget`: Crear o actualizar datos del presupuesto

### Elementos recurrentes
- `get_recurring_items`: Obtener todos los elementos recurrentes

### Cuentas Plaid
- `get_all_plaid_accounts`: Obtener todas las cuentas Plaid
- `trigger_plaid_fetch`: Activar sincronización con Plaid

### Criptomonedas
- `get_all_crypto`: Obtener todos los activos crypto
- `update_manual_crypto`: Actualizar un activo crypto manual

## Desarrollo

Para contribuir al desarrollo:

1. **Instala las dependencias de desarrollo:**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Ejecuta las pruebas:**
   ```bash
   pytest
   ```

3. **Formatea el código:**
   ```bash
   black lunchmoney_mcp/
   ```

## Seguridad

- Nunca compartas tu token de acceso de Lunch Money
- Guarda tu token en el archivo `.env` y asegúrate de que esté en tu `.gitignore`
- El servidor MCP se ejecuta localmente y no envía datos a servicios externos

## Limitaciones

- La API de Lunch Money está en beta pública, por lo que pueden haber cambios
- Algunas operaciones pueden tener límites de velocidad
- Los cambios realizados a través de la API son irreversibles

## Soporte

Si encuentras problemas:

1. Verifica que tu token de acceso sea válido
2. Consulta la [documentación oficial de Lunch Money](https://lunchmoney.dev)
3. Revisa los logs del servidor MCP para errores específicos

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## Enlaces relacionados

- [Lunch Money](https://lunchmoney.app)
- [Documentación de la API de Lunch Money](https://lunchmoney.dev)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Claude Desktop](https://claude.ai/desktop) 