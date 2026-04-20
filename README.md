# sid_product_cost_category

## Descripción

Módulo base para sustituir la lógica de costes por categoría implementada en Odoo Studio mediante campos `x_*`, migrándola a código estándar versionable bajo nomenclatura `sid_*`.

Este módulo toma el control del flujo funcional:

`product.category` → `product.template` → `sale.order.line`

## Objetivo

Eliminar dependencias de Odoo Studio y consolidar en código mantenible:

- Campos manuales (`x_*`).
- Campos compute no estándar.
- Campos related críticos.
- Vistas Studio no versionadas.

## Arquitectura funcional

### Origen (categoría)

En `product.category`:

- `sid_cost_ton`: coste por tonelada.
- `sid_cost_avg_ton`: coste promedio.
- `sid_currency_id`: moneda de referencia.
- `sid_cost_ref_date`: fecha de referencia de coste.

### Producto

En `product.template`:

- `sid_cost_category`: coste unitario calculado.
- `sid_cost_ton_category`: related a `categ_id.sid_cost_ton`.
- `sid_cost_ref_date`: related a la fecha de referencia de categoría.

Fórmula principal:

```text
sid_cost_category = (categ.sid_cost_ton * weight) / 1000
```

### Venta

En `sale.order.line`:

- `sid_cost_category`: related al coste calculado del producto.

## Migración

### `pre_init_hook`

Antes de instalar el módulo:

- Renombra columnas físicas (sin pérdida de datos):
  - `x_coste_ton` → `sid_cost_ton`
  - `x_avg_ton` → `sid_cost_avg_ton`
  - `x_currency_id` → `sid_currency_id`
  - `x_coste_categoria` → `sid_cost_category`
  - `x_precio_ton_categoria` → `sid_cost_ton_category`
  - `x_studio_monetary_field_ExXXQ` → `sid_cost_category` (en `sale.order.line`)
- Reescribe de forma conservadora referencias `x_*` en vistas para apuntar a nombres `sid_*`.
- **No** elimina campos manuales ni desactiva vistas Studio en esta fase.

### `post_init_hook`

Después de instalar:

- Completa moneda en categorías que no la tengan (`env.company.currency_id`).
- Recalcula costes en `product.template`.
- Sincroniza `sid_cost_category` en líneas de venta con el coste del producto.

## Vistas reemplazadas

El módulo publica vistas versionadas para:

- `product.category` (form y tree).
- `product.template` (form).
- `sale.order` (líneas).

## Dependencias

- `product`
- `sale_management`

## Compatibilidad y alcance

⚠️ Este módulo reduce la dependencia de Studio en el bloque funcional de costes por categoría, con una estrategia de migración **progresiva**.

Recomendación de despliegue:

1. Instalar primero en **staging**.
2. Validar datos y vistas.
3. Planificar limpieza (`x_*` y vistas Studio) en una fase posterior controlada.
4. Pasar a producción con copia de seguridad previa.


## Qué tocar según cada caso

### Caso A: Solo cambiar etiquetas o visibilidad en pantalla

Tocar:

- `views/product_category_views.xml`
- `views/product_template_views.xml`
- `views/sale_order_views.xml`

No tocar:

- `hooks.py`
- Campos Python en `models/*` (salvo que cambie lógica funcional)

### Caso B: Cambiar lógica de cálculo de coste

Tocar:

- `models/product_template.py` (`_compute_sid_cost_category` y dependencias)
- `models/sale_order_line.py` (si cambia cómo se refleja en venta)
- `README.md` (fórmula y comportamiento esperado)

Revisar adicionalmente:

- `post_init_hook` en `hooks.py` si necesitas recomputación extraordinaria tras instalar/actualizar.

### Caso C: Añadir o renombrar campos de datos persistidos

Tocar:

- Modelo correspondiente en `models/*.py`
- `COLUMN_RENAMES` y/o `FIELD_RENAMES` en `hooks.py` (si hay migración desde `x_*` o nombre legacy)
- Vistas XML donde el campo se muestra
- `README.md` y `PR_NOTES.md` para documentar impacto

Importante:

- Si hay cambio de nombre físico de columna, debe resolverse en `pre_init_hook`.
- Mantener enfoque no destructivo en instalación (limpieza destructiva en Fase 2).

### Caso D: Migrar nuevas referencias Studio (`x_*`) detectadas en cliente

Tocar:

- `FIELD_RENAMES` en `hooks.py`
- Validar referencias en vistas/automatizaciones/reportes
- Checklist en `PR_NOTES.md`

Recomendación:

- Incluir una query de detección y una evidencia de validación en el PR.

### Caso E: Limpieza final (Fase 2)

Tocar (en PR separado):

- Desactivación/eliminación de vistas Studio obsoletas
- Limpieza de metadatos `ir.model.fields` legacy
- Eliminación de campos `x_*` que ya no tengan consumidores

Obligatorio:

- Ejecutar esta fase solo tras estabilizar en staging/producción.
- Adjuntar plan de rollback y validación post-limpieza.

## Instalación

Ver checklist completo en `PR_NOTES.md`.

## Estado

- Migra el flujo principal a campos `sid_*` versionados.
- Mantiene temporalmente metadatos Studio para minimizar riesgo en instalación.
- Preparado para una Fase 2 de limpieza controlada.
