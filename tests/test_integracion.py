# tests/test_sifen_integration.py
import os
from datetime import date, datetime
from decimal import Decimal
from sifen.models.factura import Factura, ItemFactura, Cuota
from sifen.models.emisor import Emisor
from sifen.models.receptor import Receptor
from sifen.models.datos_transporte import DatosTransporte
from sifen.models.vehiculo_transporte import VehiculoTransporte
from sifen.models.punto_transporte import PuntoTransporte
from sifen.models.transportista import Transportista
from sifen.models.datos_supermercado import DatosSupermercado
from sifen.models.datos_energia import DatosEnergia
from sifen.models.PolizaSeguro import PolizaSeguro
from sifen.models.DatosSeguros import DatosSeguros
from sifen.core.builders.xml_builder import XMLBuilder
from sifen.core.signers.signer import firmar_xml
from sifen.core.validators.validator import validar_xml

def generar_y_validar_factura():
    try:
        # 1. Configuración inicial
        os.makedirs('output', exist_ok=True)

        # 2. Crear datos de ejemplo
        emisor = Emisor(
            ruc="80012345",
            dv="1",
            nombre="TECNOLOGIA PY SA",
            nombre_fantasia="COMPUMUNDO",
            direccion="Tte. Fariña e/Rojas Silva",
            num_casa="456",
            c_departamento="2",
            c_distrito="7",
            c_ciudad="1046",
            telefono="0975-257-307",
            email="ventas@tecnologia.py",
            c_actividad_economica="69201",
            c_tipo_regimen="1",
            c_tipo_contibuyente="2",
            sucursal="CASA MATRIZ",
            direccion_comp1="yamil armele y curupayty",
            direccion_comp2="pte franco y tte fariña",
            tipo_doc_responsable_DE="2",
            num_doc_responsable_DE="5886702",
            nombre_responsable_DE="Wilson Javier parra villa",
            cargo_responsable_DE="Cajero",
            is_sector_energia=False,
            is_sector_seguros=False,
            is_sector_supermercado=False,
            is_sector_transporte=False
        )

        transportista = Transportista(
            naturaleza="1",
            nombre="TRANSPORTES DEL PARAGUAY S.A.",
            ruc="80054321",
            dv="3",
            chofer_identificacion="1234567",
            chofer_nombre="Carlos Giménez",
            domicilio_fiscal="Av. Mcal. López 2345",
            nacionalidad="PRY"
        )

        vehiculo = VehiculoTransporte(
            tipo_vehiculo="Camión",
            marca="Volvo",
            tipo_identificacion=1,
            numero_identificacion="CHS-123456",
            matricula="ABC123"
        )

        punto_salida = PuntoTransporte(
            direccion="Av. República 123",
            numero_casa="456",
            departamento="1",
            ciudad="1"
        )

        punto_llegada = PuntoTransporte(
            direccion="Av. Pinedo",
            numero_casa="456",
            departamento="2",
            ciudad="3"
        )

        datos_transporte = DatosTransporte(
            tipo_transporte="1",
            modalidad_transporte="1",
            responsable_flete="1",
            condiciones_negocio="CFR",
            numero_manifiesto="MAN-2023-001",
            numero_despacho_importacion="nodesp1111111111",
            fecha_inicio_transporte="2023-05-31",
            fecha_fin_transporte="2023-07-12",
            pais_destino="DZA",
            punto_salida=punto_salida,
            punto_llegada=punto_llegada,
            vehiculos=[vehiculo],
            transportista=transportista
        )

        datos_supermercado = DatosSupermercado(
            nombre_cajero="Juan Pérez",
            efectivo=1500000,
            vuelto=2500,
            donacion=10000,
            descripcion_donacion="Donación voluntaria"
        )

        receptor = Receptor(
            ruc="1234567",
            dv="2",
            nombre="CLIENTE EJEMPLO",
            direccion="Calle Django 456",
            pais="PRY",
            c_departamento="1",
            c_distrito="1",
            c_ciudad="1",
            telefono="(032)222210",
            celular="(0975)257-307",
            tipo_contribuyente="1",
            codigo_cliente="COD0102",
            nat_receptor="1",
            tipo_doc_sin_ruc="5",
            nombre_fantasia="Nombre de fantasia recep",
            email="wilsonccont@gmail.com"
        )

        datos_energia = DatosEnergia(
            numero_medidor="MED123456789",
            codigo_actividad=1,
            codigo_categoria="RES",
            lectura_anterior=1250,
            lectura_actual=1350,
            consumo_kwh=100
        )

        items = [
            ItemFactura(
                codigo="PROD-001",
                descripcion="Laptop Premium",
                cantidad=Decimal(2),
                precio_unitario=Decimal(7500000),
                tasa_iva=Decimal(10),
                codigo_producto="1234567890123",
                codigo_unidad_medida_comercial="UNI",
                numero_serie="SN-2023-01",
                liq_IVA=Decimal(round(15000000/11, 0))
            ),
            ItemFactura(
                codigo="PROD-002",
                descripcion="Teclado inalámbrico",
                cantidad=Decimal(5),
                precio_unitario=Decimal(150000),
                tasa_iva=Decimal(10),
                codigo_producto="9876543210987",
                codigo_unidad_medida_comercial="UNI",
                liq_IVA=Decimal(round(15000000/11, 0))
            )
        ]

        poliza1 = PolizaSeguro(
            numero_poliza="POL-2023-001",
            unidad_vigencia="MESES",
            vigencia="12",
            numero_poliza_completo="POLIZA-COMPLETA-2023-001",
            fecha_inicio_vigencia=datetime(2022, 1, 1).strftime("%Y-%m-%d"),
            fecha_fin_vigencia=datetime(2023, 1, 1).strftime("%Y-%m-%d"),
            codigo_interno="SEG-INT-001"
        )

        datos_seguros = DatosSeguros(
            codigo_empresa="ASEG123",
            polizas=[poliza1]
        )

        # 3. Construir factura
        factura = Factura(
            datos_energia=datos_energia,
            datos_seguros=datos_seguros,
            datos_supermercado=datos_supermercado,
            datos_transporte=datos_transporte,
            emisor=emisor,
            receptor=receptor,
            items=items,
            timbrado="12345678",
            serie_timbrado="CD",
            inicio_vig_timbrado=datetime(2025, 1, 1).strftime("%Y-%m-%d"),
            numero_factura="001-002-0000005",
            tipo_operacion="2",
            tipo_emision="1",
            condicion_venta="2",
            tipo_credito="1",
            tipo_impuesto_afectado="5",
            moneda="PYG",
            plazo_credito="30 días",
            cuotas=[
                Cuota(numero=1, monto=Decimal("500000"), moneda="PYG", fecha_vencimiento=date(2025, 6, 1)),
                Cuota(numero=2, monto=Decimal("500000"), moneda="PYG", fecha_vencimiento=date(2025, 7, 1))
            ],
            orden_compra="OC 001",
            orden_venta="OV 001",
            num_asiento="123",
            unidad_medida_total_vol="110",
            total_vol_merc="2000",
            unidad_medida_total_peso="99",
            total_peso_merc="1500",
            id_carga="1",
            condicion_tipo_cambio="1",
            tipo_cambio_base="7850.36",
            condicion_anticipo="1"
        )

        # 4. Generar XML
        print("Generando XML...")
        xml_builder = XMLBuilder()
        xml = xml_builder.build(factura)
        
        with open('output/factura_sin_firma.xml', 'wb') as f:
            f.write(xml)
        print("XML generado guardado en output/factura_sin_firma.xml")

        # 5. Firmar XML
        print("\nFirmando XML...")
        xml_firmado = firmar_xml(xml)
        
        with open('output/factura_firmada.xml', 'wb') as f:
            f.write(xml_firmado)
        print("XML firmado guardado en output/factura_firmada.xml")

        # 6. Validar contra XSD
        print("\nValidando contra XSD...")
        es_valido, mensaje = validar_xml(xml_firmado)
        
        if es_valido:
            print("✅ El XML es válido según el esquema SIFEN")
            print("\n🎉 ¡Prueba exitosa! Revisa los archivos generados en la carpeta 'output'")
        else:
            print(f"❌ Error de validación: {mensaje}")

    except Exception as e:
        print(f"\n🔥 Error durante el proceso: {str(e)}")
        raise

if __name__ == "__main__":
    generar_y_validar_factura()