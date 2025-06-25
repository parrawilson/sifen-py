import os
import xmlsec
import hmac
import hashlib
from lxml import etree

def generar_dCarQR(xml_root, id_csc, clave_csc):
    ns = {
        "sifen": "http://ekuatia.set.gov.py/sifen/xsd",
        "ds": "http://www.w3.org/2000/09/xmldsig#"
    }

    de = xml_root.find("sifen:DE", namespaces=ns)
    id_de = de.get("Id")
    dFeEmiDE = de.findtext("sifen:gDatGralOpe/sifen:dFeEmiDE", namespaces=ns)
    dRucRec = de.findtext("sifen:gDatGralOpe/sifen:gDatRec/sifen:dRucRec", namespaces=ns)
    dTotGralOpe = de.findtext("sifen:gTotSub/sifen:dTotGralOpe", namespaces=ns)
    dTotIVA = de.findtext("sifen:gTotSub/sifen:dTotIVA", namespaces=ns)
    items = de.findall("sifen:gDtipDE/sifen:gCamItem", namespaces=ns)
    cItems = str(len(items))

    digest_value = xml_root.findtext("ds:Signature/ds:SignedInfo/ds:Reference/ds:DigestValue", namespaces=ns)

    # Armar cadena base
    parametros = {
        "nVersion": "150",
        "Id": id_de,
        "dFeEmiDE": dFeEmiDE,
        "dRucRec": dRucRec,
        "dTotGralOpe": dTotGralOpe,
        "dTotIVA": dTotIVA,
        "cItems": cItems,
        "DigestValue": digest_value,
        "IdCSC": id_csc,
    }

    cadena = "&".join(f"{k}={v}" for k, v in parametros.items())

    # Calcular el hash HMAC-SHA256
    cHashQR = hmac.new(
        clave_csc.encode("utf-8"),
        cadena.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return f"https://ekuatia.set.gov.py/consultas-test/qr?{cadena}&cHashQR={cHashQR}"


def firmar_xml(xml_bytes):
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_bytes, parser)

    ns = {"sifen": "http://ekuatia.set.gov.py/sifen/xsd"}
    de_node = root.find("sifen:DE", namespaces=ns)
    if de_node is None:
        raise Exception("No se encontró el nodo <DE> en el XML")

    de_id = de_node.get("Id")
    if not de_id:
        raise Exception("El nodo <DE> no tiene atributo 'Id'.")

    # Registrar atributo Id como tipo ID
    xmlsec.tree.add_ids(root, ["Id"])

    # Crear nodo <Signature>
    signature_node = xmlsec.template.create(
        root,
        xmlsec.Transform.EXCL_C14N,
        xmlsec.Transform.RSA_SHA256,
        name="Signature"
    )

    # Referencia a <DE>
    ref = xmlsec.template.add_reference(
        signature_node,
        xmlsec.Transform.SHA256,
        uri="#" + de_id
    )
    xmlsec.template.add_transform(ref, xmlsec.Transform.ENVELOPED)
    xmlsec.template.add_transform(ref, xmlsec.Transform.EXCL_C14N)

    key_info = xmlsec.template.ensure_key_info(signature_node)
    xmlsec.template.add_x509_data(key_info)

    # Insertar la firma después de <DE>
    de_node.addnext(signature_node)

    # Rutas a los archivos .pem
    base_path = os.path.join(os.path.dirname(__file__), "cert")
    key_path = os.path.join(base_path, "key.pem")
    cert_path = os.path.join(base_path, "cert.pem")

    key = xmlsec.Key.from_file(key_path, xmlsec.KeyFormat.PEM)
    key.load_cert_from_file(cert_path, xmlsec.KeyFormat.PEM)

    ctx = xmlsec.SignatureContext()
    ctx.key = key
    ctx.sign(signature_node)

    # 🔐 Generar el valor completo de dCarQR
    id_csc = "0001"
    clave_csc = "CLAVE_SECRETA_PROVISTA_POR_LA_SET"
    dcarqr_valor = generar_dCarQR(root, id_csc, clave_csc)

    # Agregar nodo <gCamFuFD> con <dCarQR>
    gcamfufd = etree.Element("{http://ekuatia.set.gov.py/sifen/xsd}gCamFuFD")
    dcarqr = etree.SubElement(gcamfufd, "{http://ekuatia.set.gov.py/sifen/xsd}dCarQR")
    dcarqr.text = dcarqr_valor
    signature_node.addnext(gcamfufd)

    return etree.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True)







