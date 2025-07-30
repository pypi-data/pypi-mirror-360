# Paquete de Repositorio de Zibanu para Django - zibanu.django.repository package

Este sistema permite gestionar un repositorio de archivos y generar PDFs a partir de templates HTML, almacenándolos dentro del proyecto de Django y registrando la información sobre cada PDF en la tabla del repositorio, teniendo en cuenta que, se asigna una clave UUID (Universally Unique Identifier) a cada PDF generado con el fin de identificar el archivo en el repositorio.

## zibanu.django.repository.lib.managers package

Este paquete contiene la clase *Administrador de documentos.* 

## zibanu.django.repository.lib.managers.document module
```
class zibanu.django.repository.lib.managers.document.Document()
```

El administrador de documentos es una clase que proporciona métodos para consultar y administrar documentos.

__________________
**Métodos**

```
get_by_uuid(uuid: str)→ models.QuerySet
```
Toma un UUID como entrada y devuelve un conjunto de consultas de documentos que coinciden con el UUID.

- Parámetros:

*uuid:* Cadena de texto con el valor de UUID. 

- Retorna:

*qs:* Queryset con filtro por valor UUID.

__________________
```
get_by_code(code: str)→ models.QuerySet
```

Toma un código como entrada y devuelve un conjunto de consultas de documentos que coinciden con el código.

- Parámetros:

*code:* Cadena de texto con el valor del código.

- Retorna:

*qs:* Queryset con filtro por valor UUID.

## zibanu.django.repository.lib.utils package 

Este paquete contiene la clase *Generador de documentos.*

## zibanu.django.repository.lib.utils.document_generator module

```
class zibanu.django.repository.lib.utils.document_generator.DocumentGenerator(template_prefix: str, custom_dir: str = None)→ None
```

 Clase de Python que genera un nuevo documento PDF a partir de una definición de plantilla de Django.

- Parámetros:

*template_prefix:* Ruta al directorio donde se encuentran las plantillas

*custom_dir:* Directorio personalizado donde se guardarán los documentos PDF generados.
__________________

**Métodos**


```
generate_from_template(template_name: str, context: dict, **kwargs)→ str:
```

Método para generar un documento a partir de una plantilla de django.

- Parámetros:

*template_name:* Nombre de la plantilla para construir el documento pdf.

*context:* Diccionario de contexto para anular el constructor de contexto.

*kwargs:* Diccionario con vars a plantilla como "descripción", "solicitud", "clave" y "usuario". El usuario es obligatorio.

- Retorna:

*hex:* Cadena de texto con UUID hexadecimal del documento generado.

__________________

```
get_file(user, **kwargs)→ str:
```

Obtiene un nombre de la ruta de archivo del filtrado de documentos del usuario (Obligatorio) y los valores de código o UUID.

- Parámetros:

*kwargs:* Diccionario con claves y valores para la construcción de filtros.

- Retorna:

*document:* Objeto de documento que coincide con el filtro.

__________________

```
get_document(**kwargs)→  Document:
```
Obtiene un documento de filtros definidos en **kwargs

- Parámetros:

*kwargs:* Diccionario con claves y valores para la construcción de filtros.

- Retorna:

*document:* Objeto de documento que coincide con el filtro.


## zibanu.django.repository.apps module
```
class zibanu.django.repository.apps.ZbDjangoRepository(app_name, app_module)
```

Clase heredada de django.apps.AppConfig para definir la configuración de la aplicación zibanu.django.repository.
__________________
**Atributos**

Este atributo se establece en 'django.db.models.BigAutoField', que es el campo automático predeterminado para los modelos de Django.

```
default_auto_field = 'django.db.models.BigAutoField'
```
__________________

Este atributo se establece en "zibanu.django.repository", que es el nombre de la aplicación.
```
name = "zibanu.django.repository"
```
__________________

Este atributo se establece en "zb_repository", que es la etiqueta de la aplicación.
```
label = "zb_repository"
```
__________________

**Método**
```
ready()
```
Método de anulación utilizado para el cargador de aplicaciones django después de que la aplicación se haya cargado correctamente.

- Retorna:

Ninguno.

- Ajustes:

ZB_REPOSITORY_DIRECTORY: Nombre del directorio para almacenar los documentos generados en la ruta MEDIA_ROOT. Predeterminado "ZbRepository"

## zibanu.django.repository.models module

Contiene la clase de modelo de la entidad del documento para almacenar y administrar los datos del documento.

La clase Documento tiene los siguientes campos:

- *code:* Un campo char para almacenar el código de validación.
- *uuid:* Un campo UUID para almacenar el UUID del archivo.
- *owner:* Una clave externa al modelo de usuario para almacenar el propietario del documento.
- *generated_at:* Un campo de fecha y hora para almacenar la fecha y la hora en que se generó el documento.
- *descripción:* Un campo char para almacenar una descripción del documento.

La clase también tiene un administrador predeterminado llamado objects.

```
class zibanu.django.repository.models.Document()
```


