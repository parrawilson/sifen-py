import os
from pathlib import Path
from lxml import etree
from typing import Tuple

def validar_xml(xml_bytes: bytes) -> Tuple[bool, str]:
    """
    Valida un XML contra el esquema XSD de SIFEN.
    
    Args:
        xml_bytes: XML a validar en formato bytes
    
    Returns:
        Tuple[bool, str]: (True, None) si es válido, (False, mensaje_error) si no
    """
    try:
        # 1. Configuración de rutas - Más robusto con pathlib
        current_dir = Path(__file__).parent
        schemas_dir = current_dir.parent.parent / 'schemas'  # Sube dos niveles desde validators/
        xsd_path = schemas_dir / 'siRecepDE_v150.xsd'
        
        # Verificar existencia del XSD
        if not xsd_path.exists():
            error_msg = (
                f"Archivo XSD no encontrado en: {xsd_path}\n"
                "Por favor asegúrate de:\n"
                "1. Tener el archivo 'siRecepDE_v150.xsd' en la carpeta 'sifen/schemas/'\n"
                "2. Descargar la versión correcta desde el portal SIFEN"
            )
            return False, error_msg

        # 2. Cargar esquema XSD con manejo explícito de encoding
        try:
            schema_doc = etree.parse(str(xsd_path))
            schema = etree.XMLSchema(schema_doc)
        except etree.XMLSyntaxError as e:
            return False, f"Error en el esquema XSD: {str(e)}"

        # 3. Parsear y validar el XML
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            xml_doc = etree.fromstring(xml_bytes, parser)
            schema.assertValid(xml_doc)
            return True, None
            
        except etree.DocumentInvalid as e:
            # Detalles específicos de errores de validación
            error_lines = []
            for error in e.error_log:
                error_lines.append(
                    f"Línea {error.line}: {error.message} (Nivel: {error.level_name})"
                )
            return False, "Errores de validación:\n" + "\n".join(error_lines)
            
        except etree.XMLSyntaxError as e:
            return False, f"Error de sintaxis en el XML: {str(e)}"

    except Exception as e:
        # Manejo de errores inesperados
        error_msg = (
            f"Error inesperado durante la validación:\n"
            f"Tipo: {type(e).__name__}\n"
            f"Mensaje: {str(e)}"
        )
        return False, error_msg