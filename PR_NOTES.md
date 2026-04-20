# Notas para Pull Request

## 🎯 Objetivo del PR

Eliminar lógica de costes implementada en Odoo Studio y migrarla a código mantenible en el módulo `sid_product_cost_category` (nomenclatura `sid_*`).

## 🔍 Qué problema resuelve

Actualmente existían riesgos típicos de Studio:

- Campos `state = manual` no versionados en código.
- Cálculos y dependencias difíciles de auditar.
- Campos monetarios heredados desde Studio con naming inestable.
- Vistas Studio no controladas por Git.
- Campo crítico con nombre opaco: `x_studio_monetary_field_ExXXQ`.

## 🧠 Qué hace este PR

### 1) Introduce módulo de dominio de costes

- Define campos en modelos Python.
- Estandariza naming en `sid_*`.
- Conserva la lógica funcional esperada por negocio.

### 2) Añade migración automática (`pre_init_hook`)

- Renombrado físico de columnas para conservar datos.
- Reescritura de referencias `x_*` en vistas.
- Reescritura conservadora de referencias en vistas sin desactivar Studio automáticamente.
- **No elimina** metadatos `x_*` en instalación: se difiere a una Fase 2 controlada.

### 3) Sustituye vistas por XML versionado

- Se reemplazan vistas de categoría, producto y pedido de venta.
- La funcionalidad queda mantenible y trazable en repositorio.

### 4) Ejecuta normalización (`post_init_hook`)

- Completa moneda faltante en categorías.
- Recalcula costes en productos.
- Sincroniza coste en líneas de venta.

## ⚠️ Riesgos identificados

- Vistas personalizadas adicionales no detectadas.
- Dependencias ocultas a `x_*` fuera del alcance previsto.
- Uso externo en reportes, dominios o automatizaciones.
- Acumulación temporal de metadatos legacy hasta ejecutar la Fase 2.

## 🔧 Qué revisar en código y metadatos

Buscar referencias a:

- `x_coste_ton`
- `x_coste_categoria`
- `x_studio_monetary_field_ExXXQ`

Revisar especialmente:

- `base.automation`
- Dominios en vistas
- Informes QWeb
- Acciones servidor

## 🧪 Plan de validación funcional

1. Categorías muestran costes y moneda correctamente.
2. Productos calculan `sid_cost_category` según peso.
3. Líneas de venta reflejan coste recomendado del producto.
4. No aparecen errores de vistas al abrir formularios.
5. No hay warnings por campos inexistentes en logs.


## 🧭 Qué tocar en cada caso (guía rápida)

### 1) Solo UI (labels/posición/visibilidad)

- **Sí tocar:** XML de vistas (`views/*.xml`).
- **No tocar:** hooks de migración ni modelos Python, salvo necesidad funcional.

### 2) Cambio de fórmula de coste

- **Sí tocar:** `models/product_template.py` (compute), y `models/sale_order_line.py` si afecta el reflejo en venta.
- **Revisar:** dependencia `@api.depends`, almacenado (`store=True`) y recomputación en `post_init_hook`.
- **Documentar:** nueva regla en `README.md`.

### 3) Nuevo campo o rename de campo persistido

- **Sí tocar:** modelo Python + vista XML.
- **Si hay migración legacy:** actualizar `COLUMN_RENAMES` / `FIELD_RENAMES` en `hooks.py`.
- **Checklist PR:** agregar validación de datos antes/después.

### 4) Aparecen más `x_*` en cliente

- **Sí tocar:** `FIELD_RENAMES` y checklist de detección.
- **Validar:** vistas (`ir.ui.view`), automatizaciones (`base.automation`), reportes QWeb, acciones servidor.
- **No hacer de golpe:** limpieza destructiva en el mismo PR de instalación.

### 5) Limpieza destructiva (Fase 2)

- **PR separado obligatorio** con ventana controlada.
- **Incluye:** retirar vistas Studio obsoletas, limpiar metadatos legacy, retirar `x_*` sin uso.
- **Requiere:** backup + rollback + validación funcional completa.

## ✅ Checklist de instalación (muy importante)

### 🟡 Antes de instalar

En Odoo shell (o revisión manual de metadatos):

```python
env["ir.ui.view"].search([("arch_db", "ilike", "x_coste")])
env["ir.ui.view"].search([("arch_db", "ilike", "x_studio")])
env["base.automation"].search([("code", "ilike", "x_coste")])
env["ir.ui.view"].search([("arch_db", "ilike", "x_coste_categoria")])
```

### 🔴 Crítico

Si aparecen referencias fuera de:

- `product.category`
- `product.template`
- `sale.order.line`

👉 **Parar e integrar esos casos en el módulo antes de instalar**.

### 🟢 Instalación

1. Subir módulo.
2. Reiniciar Odoo.
3. Instalar `sid_product_cost_category`.

### 🧪 Después de instalar

1. Validar datos:
   - categorías con coste,
   - productos con coste calculado,
   - líneas de venta coherentes.
2. Revisar logs buscando:
   - `column does not exist`
   - `field x_*`
3. Validar vistas:
   - formulario de producto,
   - formulario de categoría,
   - pedido de venta.

## 🧹 Fase 2 (obligatoria tras estabilizar)

Tras validar en entorno objetivo:

- Eliminar campos `x_*` sobrantes que sigan vivos.
- Desactivar y/o eliminar vistas Studio no utilizadas.
- Completar limpieza de metadata residual (`ir.model.fields`, `ir.model.data`, selecciones).
- Ejecutar una nueva ronda de validación funcional y revisión de logs.

## 🧠 Recomendación final

Este caso no es trivial por el volumen potencial de Studio y personalizaciones heredadas.

👉 Instalar primero en **staging** es obligatorio y la limpieza destructiva debe hacerse solo en una segunda entrega.
