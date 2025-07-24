from decimal import Decimal
from lxml import etree
from datetime import datetime, date
from sifen.models.factura import Factura
from sifen.utils import constants
import logging

class XMLBuilder:
    NSMAP = {
        None: "http://ekuatia.set.gov.py/sifen/xsd",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "ds": "http://www.w3.org/2000/09/xmldsig#"
    }

    @staticmethod
    def _normalize_date(fecha):
        """Normaliza diferentes formatos de fecha a objeto date"""
        if isinstance(fecha, datetime):
            return fecha.date()
        elif isinstance(fecha, date):
            return fecha
        elif isinstance(fecha, str):
            try:
                # Intentar parsear como datetime primero
                dt = datetime.strptime(fecha, '%Y-%m-%dT%H:%M:%S')
                return dt.date()
            except ValueError:
                try:
                    # Intentar parsear como date
                    dt = datetime.strptime(fecha, '%Y-%m-%d')
                    return dt.date()
                except ValueError as e:
                    logging.error(f"Formato de fecha no reconocido: {fecha}")
                    raise ValueError(f"Formato de fecha no reconocido: {fecha}") from e
        else:
            raise TypeError(f"Tipo de fecha no soportado: {type(fecha)}")
    
    @staticmethod
    def _agregar_transportista(parent_node, transportista):
        """Agrega los datos del transportista al XML"""
        g_cam_trans = etree.SubElement(parent_node, "gCamTrans")
        
        # Datos básicos del transportista
        etree.SubElement(g_cam_trans, "iNatTrans").text = transportista.naturaleza  # 1=Persona Jurídica, 2=Persona Física
        etree.SubElement(g_cam_trans, "dNomTrans").text = transportista.nombre[:120]
        
        # Datos RUC si es persona jurídica
        if transportista.naturaleza == "1":
            etree.SubElement(g_cam_trans, "dRucTrans").text = transportista.ruc
            etree.SubElement(g_cam_trans, "dDVTrans").text = transportista.dv
        
        # Datos de identificación para persona física
        if transportista.naturaleza == "2":
            etree.SubElement(g_cam_trans, "iTipIDTrans").text = transportista.tipo_identificacion
            etree.SubElement(g_cam_trans, "dDTipIDTrans").text = constants.TIPO_DOC_IDENTIDAD(transportista.tipo_identificacion,"")
            etree.SubElement(g_cam_trans, "dNumIDTrans").text = transportista.numero_identificacion
            if transportista.nacionalidad:
                etree.SubElement(g_cam_trans, "cNacTrans").text = transportista.nacionalidad
                etree.SubElement(g_cam_trans, "dDesNacTrans").text = constants.PAISES.get(transportista.nacionalidad, "")

        # Datos del conductor
        etree.SubElement(g_cam_trans, "dNumIDChof").text = transportista.chofer_identificacion
        etree.SubElement(g_cam_trans, "dNomChof").text = transportista.chofer_nombre[:120]
        
        # Datos adicionales
        if transportista.domicilio_fiscal:
            etree.SubElement(g_cam_trans, "dDomFisc").text = transportista.domicilio_fiscal[:150]
        
        


    @staticmethod
    def _agregar_punto_transporte(parent, tag_name, punto):
        """Agrega punto de salida o llegada"""
        punto_node = etree.SubElement(parent, tag_name)
        etree.SubElement(punto_node, "dDirLocSal").text = punto.direccion[:150]
        etree.SubElement(punto_node, "dNumCasSal").text = punto.numero_casa[:10]
        etree.SubElement(punto_node, "cDepSal").text = punto.departamento
        etree.SubElement(punto_node, "dDesDepSal").text = constants.DEPARTAMENTOS_PARAGUAY.get(punto.departamento, "")
        if punto.distrito:
            etree.SubElement(punto_node, "cDisSal").text = punto.distrito
            etree.SubElement(punto_node, "dDesDisSal").text = constants.DISTRITOS_PARAGUAY.get(punto.distrito, "")
        etree.SubElement(punto_node, "cCiuSal").text = punto.ciudad
        etree.SubElement(punto_node, "dDesCiuSal").text = constants.CIUDADES_PARAGUAY.get(punto.ciudad, "")
        if punto.telefono:
            etree.SubElement(punto_node, "dTelSal").text = punto.telefono[:20]
    @staticmethod
    def _agregar_punto_transporte_entrega(parent, tag_name, punto):
        """Agrega punto de salida o llegada"""
        punto_node = etree.SubElement(parent, tag_name)
        etree.SubElement(punto_node, "dDirLocEnt").text = punto.direccion[:150]
        etree.SubElement(punto_node, "dNumCasEnt").text = punto.numero_casa[:10]
        etree.SubElement(punto_node, "cDepEnt").text = punto.departamento
        etree.SubElement(punto_node, "dDesDepEnt").text = constants.DEPARTAMENTOS_PARAGUAY.get(punto.departamento, "")
        if punto.distrito:
            etree.SubElement(punto_node, "cDisEnt").text = punto.distrito
            etree.SubElement(punto_node, "dDesDisEnt").text = constants.DISTRITOS_PARAGUAY.get(punto.distrito, "")
        etree.SubElement(punto_node, "cCiuEnt").text = punto.ciudad
        etree.SubElement(punto_node, "dDesCiuEnt").text = constants.CIUDADES_PARAGUAY.get(punto.ciudad, "")
        if punto.telefono:
            etree.SubElement(punto_node, "dTelEnt").text = punto.telefono[:20]
    @staticmethod
    def _agregar_vehiculo(parent, vehiculo):
        """Agrega datos de un vehículo"""
        g_veh = etree.SubElement(parent, "gVehTras")
        etree.SubElement(g_veh, "dTiVehTras").text = vehiculo.tipo_vehiculo[:10]
        etree.SubElement(g_veh, "dMarVeh").text = vehiculo.marca[:10]
        etree.SubElement(g_veh, "dTipIdenVeh").text = str(vehiculo.tipo_identificacion)
        if vehiculo.numero_identificacion:
            etree.SubElement(g_veh, "dNroIDVeh").text = vehiculo.numero_identificacion[:20]
        if vehiculo.matricula:
            etree.SubElement(g_veh, "dNroMatVeh").text = vehiculo.matricula[:6]
        if vehiculo.numero_vuelo:
            etree.SubElement(g_veh, "dNroVuelo").text = vehiculo.numero_vuelo[:6]

    @staticmethod
    def _formatear_decimal(value, decimal_places):
                """Formatea valores decimales según requerimientos SIFEN"""
                if value is None:
                    return None
                return f"{Decimal(value).quantize(Decimal('0.' + '0'*decimal_places))}"

    @staticmethod
    def build(factura: Factura) -> bytes:
        """
        Genera el XML de la factura en formato SIFEN (Paraguay) completo.
        
        Args:
            factura (Factura): Objeto Factura con los datos a serializar.
            
        Returns:
            bytes: XML generado en formato UTF-8 con todos los campos requeridos.
        """
        factura.validar()
        
        # Crear elemento raíz
        root = etree.Element("rDE", nsmap=XMLBuilder.NSMAP)
        etree.SubElement(root, "dVerFor").text = "150"
        
        # Elemento DE (Documento Electrónico)
        de = etree.SubElement(root, "DE")
        
        # 1. Campos básicos del DE
        etree.SubElement(de, "dDVId").text = "1"
        etree.SubElement(de, "dFecFirma").text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        etree.SubElement(de, "dSisFact").text = "1"
        
        # 2. Grupo gOpeDE (Operación del DE)
        g_ope_de = etree.SubElement(de, "gOpeDE")
        etree.SubElement(g_ope_de, "iTipEmi").text = factura.tipo_emision
        etree.SubElement(g_ope_de, "dDesTipEmi").text = constants.TIPO_EMISION.get(factura.tipo_emision, "Normal")
        etree.SubElement(g_ope_de, "dCodSeg").text = factura.codigo_seguridad
        etree.SubElement(g_ope_de, "dInfoEmi").text = factura.emisor.info_emisor 
        etree.SubElement(g_ope_de, "dInfoFisc").text = factura.emisor.info_fiscal 
        
        # 3. Grupo gTimb (Timbrado)
        g_timb = etree.SubElement(de, "gTimb")
        etree.SubElement(g_timb, "iTiDE").text = factura.tipo_factura
        etree.SubElement(g_timb, "dDesTiDE").text = constants.TIPOS_DOCUMENTO.get(factura.tipo_factura, "Factura electrónica")
        etree.SubElement(g_timb, "dNumTim").text = factura.timbrado.zfill(8)
        etree.SubElement(g_timb, "dEst").text = factura.numero_factura.split("-")[0]
        etree.SubElement(g_timb, "dPunExp").text = factura.numero_factura.split("-")[1]
        etree.SubElement(g_timb, "dNumDoc").text = factura.numero_factura.split("-")[2]
        etree.SubElement(g_timb, "dSerieNum").text = factura.serie_timbrado
        etree.SubElement(g_timb, "dFeIniT").text = factura.inicio_vig_timbrado
        
        # 4. Grupo gDatGralOpe (Datos generales de la operación)
        g_dat_gral_ope = etree.SubElement(de, "gDatGralOpe")
        etree.SubElement(g_dat_gral_ope, "dFeEmiDE").text = factura.fecha_emision.strftime("%Y-%m-%dT%H:%M:%S")
        
        # 4.1 Grupo gOpeCom (Operación comercial)
        g_ope_com = etree.SubElement(g_dat_gral_ope, "gOpeCom")
        etree.SubElement(g_ope_com, "iTipTra").text = factura.tipo_operacion
        etree.SubElement(g_ope_com, "dDesTipTra").text = constants.TIPOS_TRANSACCION.get(factura.tipo_operacion, "Venta de mercadería")
        etree.SubElement(g_ope_com, "iTImp").text = factura.tipo_impuesto_afectado
        etree.SubElement(g_ope_com, "dDesTImp").text = constants.TIPOS_IMPUESTOS_AFECTADOS.get(factura.tipo_impuesto_afectado, "IVA")
        etree.SubElement(g_ope_com, "cMoneOpe").text = factura.moneda
        etree.SubElement(g_ope_com, "dDesMoneOpe").text = constants.MONEDAS.get(factura.moneda, "Guaraníes")

        if (factura.moneda != "PYG"):
            etree.SubElement(g_ope_com, "dCondTiCam").text = factura.condicion_tipo_cambio   # condicion tipo de cambio
            etree.SubElement(g_ope_com, "dTiCam").text = factura.tipo_cambio_base

        etree.SubElement(g_ope_com, "iCondAnt").text = factura.condicion_anticipo
        etree.SubElement(g_ope_com, "dDesCondAnt").text = constants.CONDICION_ANTICIPO.get(factura.condicion_anticipo, "")
        

        # 4.2 Grupo gEmis (Emisor)
        g_emis = etree.SubElement(g_dat_gral_ope, "gEmis")
        etree.SubElement(g_emis, "dRucEm").text = factura.emisor.ruc
        etree.SubElement(g_emis, "dDVEmi").text = factura.emisor.dv
        etree.SubElement(g_emis, "iTipCont").text = factura.emisor.c_tipo_contibuyente
        etree.SubElement(g_emis, "cTipReg").text = factura.emisor.c_tipo_regimen
        etree.SubElement(g_emis, "dNomEmi").text = factura.emisor.nombre
        etree.SubElement(g_emis, "dNomFanEmi").text = factura.emisor.nombre_fantasia
        etree.SubElement(g_emis, "dDirEmi").text = factura.emisor.direccion
        etree.SubElement(g_emis, "dNumCas").text = factura.emisor.num_casa

        if factura.emisor.direccion_comp1 and factura.emisor.direccion_comp2:
            etree.SubElement(g_emis, "dCompDir1").text = factura.emisor.direccion_comp1
            etree.SubElement(g_emis, "dCompDir2").text = factura.emisor.direccion_comp2

        etree.SubElement(g_emis, "cDepEmi").text = factura.emisor.c_departamento
        etree.SubElement(g_emis, "dDesDepEmi").text = constants.DEPARTAMENTOS_PARAGUAY.get(factura.emisor.c_departamento, "")
        etree.SubElement(g_emis, "cDisEmi").text = factura.emisor.c_distrito
        etree.SubElement(g_emis, "dDesDisEmi").text = constants.DISTRITOS_PARAGUAY.get(factura.emisor.c_distrito, "")
        etree.SubElement(g_emis, "cCiuEmi").text = factura.emisor.c_ciudad
        etree.SubElement(g_emis, "dDesCiuEmi").text = constants.CIUDADES_PARAGUAY.get(factura.emisor.c_ciudad, "")
        etree.SubElement(g_emis, "dTelEmi").text = factura.emisor.telefono
        etree.SubElement(g_emis, "dEmailE").text = factura.emisor.email
        etree.SubElement(g_emis, "dDenSuc").text = factura.emisor.sucursal
        
        # Actividad económica

        for itemAct in factura.emisor.c_actividad_economica:
            g_act_eco = etree.SubElement(g_emis, "gActEco")
            etree.SubElement(g_act_eco, "cActEco").text = itemAct.codigo
            etree.SubElement(g_act_eco, "dDesActEco").text = constants.ACTIVIDADES_ECONOMICAS.get(itemAct.codigo, "")
        
        #Responsable de la generación del DE
        g_resp_emi_de = etree.SubElement(g_emis, "gRespDE")
        etree.SubElement(g_resp_emi_de,"iTipIDRespDE").text= factura.emisor.tipo_doc_responsable_DE or "1"
        etree.SubElement(g_resp_emi_de,"dDTipIDRespDE").text= constants.TIPO_DOC_RESP_EMI_DE.get(factura.emisor.tipo_doc_responsable_DE,"Cédula paraguaya")
        etree.SubElement(g_resp_emi_de,"dNumIDRespDE").text= factura.emisor.num_doc_responsable_DE
        etree.SubElement(g_resp_emi_de,"dNomRespDE").text= factura.emisor.nombre_responsable_DE
        etree.SubElement(g_resp_emi_de,"dCarRespDE").text= factura.emisor.cargo_responsable_DE


        # 4.3 Grupo gDatRec (Receptor)
        g_dat_rec = etree.SubElement(g_dat_gral_ope, "gDatRec")
        etree.SubElement(g_dat_rec, "iNatRec").text = factura.receptor.nat_receptor
        etree.SubElement(g_dat_rec, "iTiOpe").text = factura.tipo_operacion or "1"
        etree.SubElement(g_dat_rec, "cPaisRec").text = factura.receptor.pais or "PRY"
        etree.SubElement(g_dat_rec, "dDesPaisRe").text = constants.PAISES.get(factura.receptor.pais, "Paraguay")
        
        if factura.receptor.nat_receptor == "1":  # Solo si es contribuyente
            etree.SubElement(g_dat_rec, "iTiContRec").text = factura.receptor.tipo_contribuyente
            etree.SubElement(g_dat_rec, "dRucRec").text = factura.receptor.ruc
            etree.SubElement(g_dat_rec, "dDVRec").text = factura.receptor.dv
        else:
            etree.SubElement(g_dat_rec, "iTipIDRec").text = factura.receptor.tipo_doc_sin_ruc or "5"
            etree.SubElement(g_dat_rec, "dDTipIDRec").text = constants.TIPO_DOC_RECEPT_SIN_RUC.get(factura.receptor.tipo_doc_sin_ruc,"Innominado")
        

        
        etree.SubElement(g_dat_rec, "dNomRec").text = factura.receptor.nombre
        if  len(factura.receptor.nombre_fantasia) >3:
            etree.SubElement(g_dat_rec, "dNomFanRec").text = factura.receptor.nombre_fantasia

        etree.SubElement(g_dat_rec, "dDirRec").text = factura.receptor.direccion
        etree.SubElement(g_dat_rec, "dNumCasRec").text = factura.receptor.num_casa
        etree.SubElement(g_dat_rec, "cDepRec").text = factura.receptor.c_departamento
        etree.SubElement(g_dat_rec, "dDesDepRec").text = constants.DEPARTAMENTOS_PARAGUAY.get(factura.receptor.c_departamento, "")
        etree.SubElement(g_dat_rec, "cDisRec").text = factura.receptor.c_distrito
        etree.SubElement(g_dat_rec, "dDesDisRec").text = constants.DISTRITOS_PARAGUAY.get(factura.receptor.c_distrito, "")
        etree.SubElement(g_dat_rec, "cCiuRec").text = factura.receptor.c_ciudad
        etree.SubElement(g_dat_rec, "dDesCiuRec").text = constants.CIUDADES_PARAGUAY.get(factura.receptor.c_ciudad, "")
        
        if len(factura.receptor.celular) > 6:
            etree.SubElement(g_dat_rec, "dTelRec").text = factura.receptor.telefono or ""
        if len(factura.receptor.celular) > 9:
            etree.SubElement(g_dat_rec, "dCelRec").text = factura.receptor.celular or ""
           
        if factura.receptor.email:
            email_validado = factura.receptor.validar_email(factura.receptor.email)
            etree.SubElement(g_dat_rec, "dEmailRec").text = email_validado
        
        if factura.receptor.codigo_cliente:
            etree.SubElement(g_dat_rec, "dCodCliente").text = factura.receptor.codigo_cliente
        
        # 5. Grupo gDtipDE (Detalles específicos del DE)
        g_dtip_de = etree.SubElement(de, "gDtipDE")
        
        # 5.1 Grupo gCamFE (Campos específicos de factura)
        g_cam_fe = etree.SubElement(g_dtip_de, "gCamFE")
        etree.SubElement(g_cam_fe, "iIndPres").text = factura.indicador_presencia
        etree.SubElement(g_cam_fe, "dDesIndPres").text = constants.INDICADORES_PRESENCIA.get(factura.indicador_presencia, "Operación presencial")
        
        # 5.2 Grupo gCamCond (Condiciones de la operación)
        g_cam_cond = etree.SubElement(g_dtip_de, "gCamCond")
        etree.SubElement(g_cam_cond, "iCondOpe").text = factura.condicion_venta
        etree.SubElement(g_cam_cond, "dDCondOpe").text = constants.CONDICIONES_VENTA.get(factura.condicion_venta, "Contado")
        
        if factura.condicion_venta == "2":  # Crédito
            g_pag_cred = etree.SubElement(g_cam_cond, "gPagCred")
            
            # --- iCondCred + dDCondCred (validados) ---
            tipo_credito = factura.tipo_credito if factura.tipo_credito in ("1", "2") else "1"
            etree.SubElement(g_pag_cred, "iCondCred").text = tipo_credito
            etree.SubElement(g_pag_cred, "dDCondCred").text = constants.TIPOS_CREDITO.get(factura.tipo_credito, "Cuota")

            # --- dPlazoCre (solo si es crédito a plazo) ---
            if tipo_credito == "1":
                plazo = str(factura.plazo_credito or "30")
                if len(plazo) > 15:  # Aseguramos cumplir con maxLength=15
                    plazo = plazo[:15]
                if len(plazo)<2: # agregar un 0 por delante si solo tiene un caracter
                    plazo = "0" + plazo
                etree.SubElement(g_pag_cred, "dPlazoCre").text = plazo
            
            # --- dCuotas (solo si es crédito en cuotas) ---
            if tipo_credito == "2" and factura.cuotas:
                num_cuotas = len(factura.cuotas)
                if num_cuotas > 999:
                    logging.warning(f"Se excede el máximo de cuotas permitidas (999). Se truncará a 999.")
                    num_cuotas = 999
                etree.SubElement(g_pag_cred, "dCuotas").text = str(num_cuotas)
            
            # --- dMonEnt (monto de entrada opcional) ---
            if hasattr(factura, 'monto_entrega') and factura.monto_entrega is not None:
                try:
                    monto = round(float(factura.monto_entrega), 4)
                    if 0 <= monto <= 999999999999999.9999:
                        formatted_monto = "{0:.4f}".format(monto).rstrip('0').rstrip('.') if '.' in "{0:.4f}".format(monto) else "{0:.4f}".format(monto)
                        etree.SubElement(g_pag_cred, "dMonEnt").text = formatted_monto
                except (ValueError, TypeError):
                    pass  # Ignorar valores inválidos
            
            # --- gCuotas (solo si es crédito en cuotas) ---
            if tipo_credito == "2" and factura.cuotas:
                for cuota in factura.cuotas:
                    g_cuota = etree.SubElement(g_pag_cred, "gCuotas")
                    etree.SubElement(g_cuota, "cMoneCuo").text = cuota.moneda or "PYG"
                    etree.SubElement(g_cuota, "dDMoneCuo").text = constants.MONEDAS.get(cuota.moneda, "Guaraníes")
                    
                    try:
                        monto_cuota = cuota.monto.quantize(Decimal('0.0001'))
                        if not (Decimal('0') <= monto_cuota <= Decimal('999999999999999.9999')):
                            raise ValueError("Monto fuera de rango permitido")
                        
                        formatted_cuota = "{0:.4f}".format(float(monto_cuota)).replace(".0000", "") \
                            if monto_cuota == monto_cuota.to_integral() \
                            else "{0:.4f}".format(float(monto_cuota)).rstrip('0').rstrip('.')
                        etree.SubElement(g_cuota, "dMonCuota").text = formatted_cuota
                    except (ValueError, TypeError, AttributeError) as e:
                        logging.warning(f"Error en monto de cuota: {str(e)}")
                        etree.SubElement(g_cuota, "dMonCuota").text = "0.0000"

                    if cuota.fecha_vencimiento is not None:
                        try:
                            fecha_normalizada = XMLBuilder._normalize_date(cuota.fecha_vencimiento)
                            etree.SubElement(g_cuota, "dVencCuo").text = fecha_normalizada.strftime('%Y-%m-%d')
                        except (ValueError, TypeError) as e:
                            logging.warning(f"Fecha inválida en cuota: {str(e)}")

        # 5.3 Items (gCamItem) - Versión final corregida
        for item in factura.items:
            g_cam_item = etree.SubElement(g_dtip_de, "gCamItem")
            
            # Información básica del item según secuencia XSD
            etree.SubElement(g_cam_item, "dCodInt").text = item.codigo
            
            # Elementos opcionales según XSD
            if hasattr(item, 'codigo_partida_arancelaria') and item.codigo_partida_arancelaria:
                # Extraer solo los primeros 4 dígitos numéricos
                partida_limpia = ''.join(filter(str.isdigit, item.codigo_partida_arancelaria))[:4]
                if len(partida_limpia) == 4:
                    etree.SubElement(g_cam_item, "dParAranc").text = partida_limpia
                else:
                    logging.warning(f"Partida arancelaria inválida: {item.codigo_partida_arancelaria}")


            if hasattr(item, 'codigo_nandina') and item.codigo_nandina:
                # Eliminar todos los caracteres no numéricos
                ncm_limpio = ''.join(filter(str.isdigit, item.codigo_nandina))
                # Asegurar que tenga entre 6 y 8 dígitos
                if 6 <= len(ncm_limpio) <= 8:
                    etree.SubElement(g_cam_item, "dNCM").text = ncm_limpio
                else:
                    logging.warning(f"Código NCM inválido: {item.codigo_nandina} (debe tener 6-8 dígitos)")
            

            # Códigos GTIN
            if hasattr(item, 'codigo_producto') and item.codigo_producto:
                etree.SubElement(g_cam_item, "dGtin").text = item.codigo_producto
            if hasattr(item, 'codigo_paquete') and item.codigo_paquete:
                etree.SubElement(g_cam_item, "dGtinPq").text = item.codigo_paquete
            
            # Descripción del producto/servicio (obligatorio)
            etree.SubElement(g_cam_item, "dDesProSer").text = item.descripcion 
            
            # Unidades de medida (obligatorias)
            etree.SubElement(g_cam_item, "cUniMed").text = item.unidad_medida
            etree.SubElement(g_cam_item, "dDesUniMed").text = constants.UNIDADES_MEDIDA.get(item.unidad_medida, "Unidad")
            
            # Cantidad (obligatorio)
            etree.SubElement(g_cam_item, "dCantProSer").text = str(item.cantidad)
            
            # Información de origen (opcional)
            if hasattr(item, 'pais_origen') and item.pais_origen:
                etree.SubElement(g_cam_item, "cPaisOrig").text = item.pais_origen
                nombre_pais = getattr(item, 'nombre_pais_origen', None) or constants.PAISES.get(item.pais_origen, "")
                etree.SubElement(g_cam_item, "dDesPaisOrig").text = nombre_pais
            
            # Información adicional del item (opcional)
            if hasattr(item, 'informacion_adicional') and item.informacion_adicional:
                etree.SubElement(g_cam_item, "dInfItem").text = item.informacion_adicional[:500]
            
            # Valor del ítem
            g_valor_item = etree.SubElement(g_cam_item, "gValorItem")
            etree.SubElement(g_valor_item, "dPUniProSer").text = str(item.precio_unitario)
            etree.SubElement(g_valor_item, "dTotBruOpeItem").text = str(item.calcular_subtotal())
            
            # Valor resta (descuentos)
            g_valor_resta = etree.SubElement(g_valor_item, "gValorRestaItem")
            etree.SubElement(g_valor_resta, "dDescItem").text = str(item.descuento or 0)
            etree.SubElement(g_valor_resta, "dPorcDesIt").text = str(item.porcentaje_descuento or 0)
            etree.SubElement(g_valor_resta, "dDescGloItem").text = str(item.descuento_global_Item or 0)
            etree.SubElement(g_valor_resta, "dTotOpeItem").text = str(item.total)
            
            # IVA
            g_cam_iva = etree.SubElement(g_cam_item, "gCamIVA")
            etree.SubElement(g_cam_iva, "iAfecIVA").text = item.afectacion_iva or "1"
            etree.SubElement(g_cam_iva, "dDesAfecIVA").text = constants.AFECTACIONES_IVA.get(item.afectacion_iva, "Gravado")
            etree.SubElement(g_cam_iva, "dPropIVA").text = str(item.proporcion_iva or 100)
            etree.SubElement(g_cam_iva, "dTasaIVA").text = str(item.tasa_iva or 10)
            etree.SubElement(g_cam_iva, "dBasGravIVA").text = str(item.base_imponible or 0)
            etree.SubElement(g_cam_iva, "dLiqIVAItem").text = str(item.liq_IVA or 0)
            
            # Información de serie/lote/fecha vencimiento - Versión final corregida
            if (hasattr(item, 'numero_serie') and item.numero_serie or 
                hasattr(item, 'numero_lote') and item.numero_lote or 
                hasattr(item, 'fecha_vencimiento') and item.fecha_vencimiento):
                g_ras_merc = etree.SubElement(g_cam_item, "gRasMerc")
                
                # Usar dNSerie en lugar de dSerieItem
                if hasattr(item, 'numero_serie') and item.numero_serie:
                    etree.SubElement(g_ras_merc, "dNSerie").text = item.numero_serie
                
                # Usar dNumLote en lugar de dLoteItem
                if hasattr(item, 'numero_lote') and item.numero_lote:
                    etree.SubElement(g_ras_merc, "dNumLote").text = item.numero_lote
                
                # Usar dVencMerc para fecha de vencimiento
                if hasattr(item, 'fecha_vencimiento') and item.fecha_vencimiento:
                    try:
                        fecha_normalizada = XMLBuilder._normalize_date(item.fecha_vencimiento)
                        etree.SubElement(g_ras_merc, "dVencMerc").text = fecha_normalizada.strftime('%Y-%m-%d')
                    except (ValueError, TypeError) as e:
                        logging.warning(f"Fecha de vencimiento inválida en ítem {item.codigo}: {str(e)}")
        

        #Agrega campos especificos: grupo se serctor energía
        if (
            factura.emisor.is_sector_energia 
            or factura.emisor.is_sector_seguros
            or factura.emisor.is_sector_supermercado
            ):
            g_campos_espec= etree.SubElement(g_dtip_de,"gCamEsp")


            if factura.datos_energia and factura.emisor.is_sector_energia:
                """Agrega el grupo gGrupEner al XML"""
                g_grup_ener = etree.SubElement(g_campos_espec, "gGrupEner")
                
                if factura.datos_energia.numero_medidor:
                    etree.SubElement(g_grup_ener, "dNroMed").text = factura.datos_energia.numero_medidor[:50]
                
                if factura.datos_energia.codigo_actividad is not None:
                    etree.SubElement(g_grup_ener, "dActiv").text = str(factura.datos_energia.codigo_actividad)
                
                if factura.datos_energia.codigo_categoria:
                    etree.SubElement(g_grup_ener, "dCateg").text = factura.datos_energia.codigo_categoria[:3]
                
                if factura.datos_energia.lectura_anterior is not None:
                    etree.SubElement(g_grup_ener, "dLecAnt").text = str(factura.datos_energia.lectura_anterior)
                
                if factura.datos_energia.lectura_actual is not None:
                    etree.SubElement(g_grup_ener, "dLecAct").text = str(factura.datos_energia.lectura_actual)
                
                if factura.datos_energia.consumo_kwh is not None:
                    etree.SubElement(g_grup_ener, "dConKwh").text = str(factura.datos_energia.consumo_kwh)

            #Agrega campos especificos: grupo se serctor seguros
            if factura.datos_seguros and factura.emisor.is_sector_seguros:
                g_grup_seg = etree.SubElement(g_campos_espec, "gGrupSeg")
            
                # Código de empresa
                etree.SubElement(g_grup_seg, "dCodEmpSeg").text = factura.datos_seguros.codigo_empresa[:20]
                
                # Pólizas (pueden ser múltiples)
                for poliza in factura.datos_seguros.polizas:
                    g_poliza = etree.SubElement(g_grup_seg, "gGrupPolSeg")
                    etree.SubElement(g_poliza, "dPoliza").text = poliza.numero_poliza[:25]
                    etree.SubElement(g_poliza, "dUnidVig").text = poliza.unidad_vigencia[:15]
                    etree.SubElement(g_poliza, "dVigencia").text = poliza.vigencia[:10]
                    
                    if poliza.numero_poliza_completo:
                        etree.SubElement(g_poliza, "dNumPoliza").text = poliza.numero_poliza_completo[:25]
                    
                    if poliza.fecha_inicio_vigencia:
                        fecha_normalizada_ivseguro = XMLBuilder._normalize_date(poliza.fecha_inicio_vigencia)
                        etree.SubElement(g_poliza, "dFecIniVig").text = fecha_normalizada_ivseguro.strftime("%Y-%m-%dT%H:%M:%S")
                
                    if poliza.fecha_fin_vigencia:
                        fecha_normalizada_fvseguro = XMLBuilder._normalize_date(poliza.fecha_fin_vigencia)
                        etree.SubElement(g_poliza, "dFecFinVig").text = fecha_normalizada_fvseguro.strftime("%Y-%m-%dT%H:%M:%S")
                    
                    if poliza.codigo_interno:
                        etree.SubElement(g_poliza, "dCodInt").text = poliza.codigo_interno[:20]


            #Agrega campos especificos: grupo sector supermercados
            if factura.datos_supermercado and factura.emisor.is_sector_supermercado:

                """Agrega el grupo gGrupSup al XML"""
                g_grup_sup = etree.SubElement(g_campos_espec, "gGrupSup")
                
                if factura.datos_supermercado.nombre_cajero:
                    etree.SubElement(g_grup_sup, "dNomCaj").text = factura.datos_supermercado.nombre_cajero[:20]
                
                if factura.datos_supermercado.efectivo is not None:
                    etree.SubElement(g_grup_sup, "dEfectivo").text = XMLBuilder._formatear_decimal(factura.datos_supermercado.efectivo, 4)
                
                if factura.datos_supermercado.vuelto is not None:
                    etree.SubElement(g_grup_sup, "dVuelto").text = XMLBuilder._formatear_decimal(factura.datos_supermercado.vuelto, 6)
                
                if factura.datos_supermercado.donacion is not None:
                    etree.SubElement(g_grup_sup, "dDonac").text = XMLBuilder._formatear_decimal(factura.datos_supermercado.donacion, 6)
                
                if factura.datos_supermercado.descripcion_donacion:
                    etree.SubElement(g_grup_sup, "dDesDonac").text = factura.datos_supermercado.descripcion_donacion[:20]
            


         #Agrega grupo sector transport
        if (factura.emisor.is_sector_transporte 
            and factura.datos_transporte
            and factura.datos_transporte.tipo_transporte
            and factura.datos_transporte.modalidad_transporte
            and factura.datos_transporte.responsable_flete):
            g_transp= etree.SubElement(g_dtip_de,"gTransp")
            # Datos básicos
            etree.SubElement(g_transp, "iTipTrans").text = factura.datos_transporte.tipo_transporte
            etree.SubElement(g_transp, "dDesTipTrans").text = constants.TIPO_TRANSPORTE.get(factura.datos_transporte.tipo_transporte,"")
            etree.SubElement(g_transp, "iModTrans").text = factura.datos_transporte.modalidad_transporte
            etree.SubElement(g_transp, "dDesModTrans").text = constants.MODALIDADES_TRANSPORTE.get(factura.datos_transporte.modalidad_transporte,"")
            etree.SubElement(g_transp, "iRespFlete").text = factura.datos_transporte.responsable_flete
            
            if factura.datos_transporte.condiciones_negocio:
                etree.SubElement(g_transp, "cCondNeg").text = factura.datos_transporte.condiciones_negocio
            if factura.datos_transporte.numero_manifiesto:
                etree.SubElement(g_transp, "dNuManif").text = factura.datos_transporte.numero_manifiesto[:15]
            if factura.datos_transporte.numero_despacho_importacion:
                etree.SubElement(g_transp, "dNuDespImp").text = factura.datos_transporte.numero_despacho_importacion
            
            if factura.datos_transporte.fecha_inicio_transporte:
                etree.SubElement(g_transp, "dIniTras").text = factura.datos_transporte.fecha_inicio_transporte
            
            if factura.datos_transporte.fecha_fin_transporte:
                etree.SubElement(g_transp, "dFinTras").text = factura.datos_transporte.fecha_fin_transporte
            
            if factura.datos_transporte.pais_destino:
                etree.SubElement(g_transp, "cPaisDest").text = factura.datos_transporte.pais_destino
                etree.SubElement(g_transp, "dDesPaisDest").text = constants.PAISES.get(factura.datos_transporte.pais_destino,"")   
            
            # Puntos de salida y llegada
            if factura.datos_transporte.punto_salida:
                XMLBuilder._agregar_punto_transporte(g_transp, "gCamSal", factura.datos_transporte.punto_salida)
            
            if factura.datos_transporte.punto_llegada:
                XMLBuilder._agregar_punto_transporte_entrega(g_transp, "gCamEnt", factura.datos_transporte.punto_llegada)
            
            # Vehículos (hasta 4 según XSD)
            for vehiculo in factura.datos_transporte.vehiculos[:4]:
                XMLBuilder._agregar_vehiculo(g_transp, vehiculo)
            
            # Transportista
            if factura.datos_transporte.transportista:
                XMLBuilder._agregar_transportista(g_transp, factura.datos_transporte.transportista)

            

            










        # 6. Grupo gTotSub (Totales)
        g_tot_sub = etree.SubElement(de, "gTotSub")
        totales = factura.calcular_totales()

        # Totales generales
        etree.SubElement(g_tot_sub, "dSubExe").text = "0"
        etree.SubElement(g_tot_sub, "dSubExo").text = "0"
        etree.SubElement(g_tot_sub, "dSub5").text = "0"
        etree.SubElement(g_tot_sub, "dSub10").text = str(totales["subtotal"])
        etree.SubElement(g_tot_sub, "dTotOpe").text = str(totales["subtotal"])
        etree.SubElement(g_tot_sub, "dTotDesc").text = str(totales.get("total_descuentos", 0))
        etree.SubElement(g_tot_sub, "dTotDescGlotem").text = str(totales.get("total_descuentos_globales", 0))
        etree.SubElement(g_tot_sub, "dTotAntItem").text = "0"
        etree.SubElement(g_tot_sub, "dTotAnt").text = "0"
        etree.SubElement(g_tot_sub, "dPorcDescTotal").text = "0"
        etree.SubElement(g_tot_sub, "dDescTotal").text = "0"
        etree.SubElement(g_tot_sub, "dAnticipo").text = "0"
        etree.SubElement(g_tot_sub, "dRedon").text = "0"
        etree.SubElement(g_tot_sub, "dTotGralOpe").text = str(totales["total"])
        etree.SubElement(g_tot_sub, "dIVA5").text = "0"
        etree.SubElement(g_tot_sub, "dIVA10").text = str(totales["iva"])
        etree.SubElement(g_tot_sub, "dTotIVA").text = str(totales["iva"])
        etree.SubElement(g_tot_sub, "dBaseGrav5").text = "0"
        etree.SubElement(g_tot_sub, "dBaseGrav10").text = str(totales["subtotal"])
        etree.SubElement(g_tot_sub, "dTBasGraIVA").text = str(totales["subtotal"])
        
        #Campos generales de la carga
        if (
            factura.orden_compra != "" 
            and factura.orden_venta != "" 
            and factura.num_asiento != ""
            and factura.unidad_medida_total_vol != ""
            and factura.total_vol_merc != ""
            and factura.unidad_medida_total_peso != ""
            and factura.total_peso_merc != ""
            and factura.id_carga != ""
            ) :
            g_campos_gen = etree.SubElement(de, "gCamGen")
            etree.SubElement(g_campos_gen,"dOrdCompra").text= factura.orden_compra
            etree.SubElement(g_campos_gen,"dOrdVta").text= factura.orden_venta
            etree.SubElement(g_campos_gen,"dAsiento").text= factura.num_asiento
            g_carg_trans= etree.SubElement(g_campos_gen,"gCamCarg")
            etree.SubElement(g_carg_trans,"cUniMedTotVol").text=factura.unidad_medida_total_vol
            etree.SubElement(g_carg_trans,"dDesUniMedTotVol").text= constants.UNIDADES_MEDIDA.get(factura.unidad_medida_total_vol, "M3")
            etree.SubElement(g_carg_trans,"dTotVolMerc").text= factura.total_vol_merc
            etree.SubElement(g_carg_trans,"cUniMedTotPes").text= factura.unidad_medida_total_peso
            etree.SubElement(g_carg_trans,"dDesUniMedTotPes").text= constants.UNIDADES_MEDIDA.get(factura.unidad_medida_total_peso, "TN")
            etree.SubElement(g_carg_trans,"dTotPesMerc").text= factura.total_peso_merc
            etree.SubElement(g_carg_trans,"iCarCarga").text= factura.id_carga
            etree.SubElement(g_carg_trans,"dDesCarCarga").text= constants.ID_CARGA.get(factura.id_carga,"Mercaderías con cadena de frío")
        
        

        # 7. Generar ID del DE
        def generar_id_de(de_node, secuencia="00000001"):
            """
            Genera el ID único del documento electrónico según formato SIFEN.
            
            Formato: TTTT-RRRRRRRRD-TT-EEE-PPP-NNNNNNN-AAAAMMDD-SSSSSSSSSSS
            """
            iTipEmi = de_node.findtext(".//iTipEmi")
            dRucEm = de_node.findtext(".//dRucEm").zfill(8)
            dDVEmi = de_node.findtext(".//dDVEmi")
            iTiDE = de_node.findtext(".//iTiDE").zfill(2)
            dEst = de_node.findtext(".//dEst").zfill(3)
            dPunExp = de_node.findtext(".//dPunExp").zfill(3)
            dNumDoc = de_node.findtext(".//dNumDoc").zfill(7)
            dFeEmiDE = de_node.findtext(".//dFeEmiDE")[:10].replace("-", "")
            return (
                iTipEmi + dRucEm + dDVEmi + iTiDE +
                dEst + dPunExp + dNumDoc + dFeEmiDE + secuencia.zfill(11)
            )

        # Asignar ID generado al elemento DE
        id_generado = generar_id_de(de)
        de.set("Id", id_generado)

        # Convertir el árbol XML a bytes con codificación UTF-8
        return etree.tostring(
            root,
            pretty_print=True,
            encoding="utf-8",
            xml_declaration=True,
            standalone=True
        )
    






