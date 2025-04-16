# Componentes Accesibles TRIVO-AI

Este directorio contiene componentes reutilizables y accesibles para usar en toda la aplicación TRIVO-AI.

## Componentes Disponibles

### Modales Accesibles

Archivo: `accessible_modal.html`

Este archivo contiene macros para crear:
- Modales estándar
- Diálogos de confirmación
- Alertas
- Paginación

## Guías de Accesibilidad

### 1. Navegación con Teclado

Asegúrese de que todos los elementos interactivos sean accesibles por teclado:
- Los enlaces y botones deben ser enfocables con `Tab`
- El enfoque debe ser visible (no ocultar el contorno en `:focus`)
- Use `tabindex="0"` sólo cuando sea necesario agregar enfoque a elementos no estándar
- Nunca use valores positivos para `tabindex` (altera el orden natural)

### 2. Uso de ARIA

- Use atributos ARIA de manera adecuada:
  - `aria-label`: Para proporcionar un nombre a elementos sin texto visible
  - `aria-labelledby`: Para hacer referencia a otro elemento como etiqueta
  - `aria-describedby`: Para hacer referencia a elementos que proporcionan descripción adicional
  - `aria-hidden="true"`: Para ocultar elementos decorativos de lectores de pantalla
  - `aria-current="page"`: Para indicar la página actual en la navegación

### 3. Texto Alternativo para Imágenes

- Todas las imágenes informativas deben tener texto alternativo (`alt`)
- Las imágenes decorativas deben tener `alt=""` (vacío) y posiblemente `aria-hidden="true"`
- Si una imagen contiene texto, ese texto debe estar incluido en el atributo `alt`

### 4. Formularios Accesibles

- Cada campo de formulario debe tener una etiqueta asociada con `<label>`
- Los campos obligatorios deben indicarse tanto visual como semánticamente (por ejemplo, `aria-required="true"`)
- Los grupos de campos relacionados deben envolverse con `<fieldset>` y `<legend>`
- Los mensajes de error deben estar asociados a los campos a través de `aria-describedby`

### 5. Contraste y Tipografía

- Asegúrese de que el texto tenga suficiente contraste con el fondo (relación mínima de 4.5:1)
- Use tamaños de fuente legibles (mínimo 16px para texto principal)
- Evite el texto justificado que puede dificultar la lectura para personas con dislexia

### 6. Modales y Diálogos

Use los componentes de macro proporcionados en `accessible_modal.html` que incluyen:
- Enfoque adecuado y trampa de foco (el foco no sale del modal cuando está abierto)
- Atributos ARIA apropiados: `role="dialog"`, `aria-modal="true"`, etc.
- Capacidad para cerrar con la tecla Escape
- Título descriptivo que se anuncia al abrir el modal

### 7. Alertas y Notificaciones

Use las macros de alerta en `accessible_modal.html` que incluyen:
- `role="alert"` para anuncio inmediato a lectores de pantalla
- Iconos de estado accesibles (con `aria-hidden="true"`)
- Contraste adecuado según el tipo de alerta

### Recursos Adicionales

- [WCAG 2.1 (Web Content Accessibility Guidelines)](https://www.w3.org/TR/WCAG21/)
- [Inclusive Components](https://inclusive-components.design/)
- [Recursos de Accesibilidad de MDN](https://developer.mozilla.org/es/docs/Web/Accessibility)
- [Web AIM - Web Accessibility in Mind](https://webaim.org/)

## Uso de Componentes

### Modal Estándar

```jinja
{% from "components/accessible_modal.html" import modal %}

{% call modal("myModal", "Título del Modal", size="lg") %}
    <div class="modal-body">
        Contenido del modal
    </div>
    <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
        <button type="button" class="btn btn-primary">Guardar</button>
    </div>
{% endcall %}
```

### Diálogo de Confirmación

```jinja
{% from "components/accessible_modal.html" import confirm_dialog %}

{% call confirm_dialog("deleteModal", "Confirmar eliminación", "¿Estás seguro de que deseas eliminar este elemento?", 
                       confirm_text="Eliminar", confirm_class="btn-danger") %}
    <form id="deleteModal-form" action="/delete" method="post">
        <input type="hidden" name="id" value="123">
    </form>
{% endcall %}
```

### Alerta

```jinja
{% from "components/accessible_modal.html" import alert %}

{% call alert("success", dismissible=true) %}
    Operación completada con éxito
{% endcall %}
```

### Paginación

```jinja
{% from "components/accessible_modal.html" import pagination %}

{{ pagination(current_page, total_pages, base_url) }}
``` 