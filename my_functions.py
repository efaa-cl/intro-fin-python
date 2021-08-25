import datetime
import bisect
import numpy as np

import autograd.numpy as agnp
from autograd import grad


def vp_bono(flujos, plazos, tasa):
    """
    Calcula el valor presente de un bono dada una tasa de descuento.
    
    Parameters
    ----------
    
    flujos: List[float]
            Contiene los flujos del bono.
            
    plazos: List[float]
            Contiene los plazos residuales de los flujos expresados en días. Todos los valores deben
            ser estrictamente positivos.
    
    tasa: float
          Tasa de descuento del bono. Debe ser en convención Com Act/365.
          
    Returns
    -------
    
    float
         El valor presente del bono.
    """
    result = 0.0
    for f, p in zip(flujos, plazos):
        result += f * (1 + tasa)**(-p / 365.0)
    return result


def vp_bono_2(flujos, plazos, tasa):
    """
    Calcula el valor presente de un bono dada una tasa de descuento.
    
    Parameters
    ----------
    
    flujos: List[float]
            Contiene los flujos del bono.
            
    plazos: List[float]
            Contiene los plazos residuales de los flujos expresados en días. Pueden venir plazos negativos o 0. Los flujos
            con plazos negativos o 0 no se considerarán en el valor presente.
    
    tasa: float
          Tasa de descuento del bono. Debe ser en convención Com Act/365.
          
    Returns
    -------
    
    float
         El valor presente del bono.
    """
    result = 0.0
    for f, p in zip(flujos, plazos):
        if p > 0:
            result += f * (1 + tasa)**(-p / 365.0)
    return result


def find_le(a, x):
    """
    Find rightmost value in a less than or equal to x.
    
    Esta función está copiada directamente de la documentación de la librería `bisect`.
    """
    i = bisect.bisect_right(a, x)
    if i:
        return a[i-1]
    raise ValueError("x is less than leftmost element in a.")
    
    
def find_gt(a, x):
    """
    Find leftmost value greater than x
    
    Esta función está copiada directamente de la documentación de la librería `bisect`.
    """
    i = bisect_right(a, x)
    if i != len(a):
        return a[i]
    raise ValueError("x is greater than rightmost element in a.")


def valor_presente(fecha_valor, fechas, flujos, tasa):
    """
    Calcula el valor presente de un conjunto de flujos utilizando una única tasa de descuento.
    
    Parameters
    ----------
    
    fecha_valor: datetime.date
        Fecha a la cual se quiere obtener el valor presente.
        
    fechas: List[datetime.date]
        Fechas de pago de los flujos.
        
    flujos: List[float]
        Flujos a traer a valor presente. Deben corresponder a las fechas en el parámetro `fechas`.
        Los flujos cuyas fechas sean iguales o previas a `fecha_valor` no serán incluidos en el cálculo.
        
    tasa: float
        Tasa de descuento a utilizar. Debe estar en convención Com Act/365.
        
    Returns
    -------
    
    Un `float` que corresponde al valor presente de los flujos.
    """
    result = 0.0
    for fec, fl in zip(fechas, flujos):
        p = (fec - fecha_valor).days
        if p > 0:
            result += fl * (1 + tasa)**(-p / 365.0)
    return result


def valor_par(fecha_valor, fechas_iniciales, saldos_insolutos, tera):
    """
    Calcula el valor par en base 100 para un bono de renta fija local.
    
    Parameters
    ----------
    
    fecha_valor: datetime.date
        Fecha a la cual se quiere obtener el valor par.
        
    fechas_iniciales: List[datetime.date]
        Fechas de inicio de devengo de los flujos del bono.
        
    saldos_insolutos: List[float]
        Saldos insolutos de cada cupón del bono.
        
    tera: float
        Tasa efectiva real anual del bono según las convenciones de la Bolsa de Comercio de Santiago.
        
    Returns
    -------
    
    Un `float` que corresponde al valor par del bono.
    """
    fecha = find_le(fechas_iniciales, fecha_valor)
    i = fechas_iniciales.index(fecha)
    saldo = saldos_insolutos[i]
    d = (fecha_valor - fecha).days
    return saldo * (1 + tera)**(d / 365.0)


def valorizador_rf(fecha_valor, nemotecnico, tir, monto, bonos, tablas_desarrollo, ufs):
    """
    Valoriza un instrumento de renta fija local a una fecha, a partir de su nemotécnico y la tir de mercado.
    
    Arguments
    ---------
    
    nemotecnico: str
        Es un nemotécnico válido de renta fija local.
        
    fecha_valor: datetime.date
        Fecha a la cual se requiere el cálculo.
        
    tir: float
        Tir de mercado del bono.
        
    monto: float
        Monto total del bono.
        
    bonos: pandas.DataFrame
        Contiene la información de cabecera de los bonos. En particular tiene las columnas `nemotecnico`,
        `tasa_descuento` que representa la TERA del bono y `fecha_emision`.
        
    tablas_desarrollo: pandas.DataFrame
        Contiene las columnas `nemotecnico`, `interes`, `amortizacion` y `fecha_vcto_cupon`.
        
    Returns
    -------
    
    El precio, el valor par, el valor presente, el valor de pago, la duración y la convexidad del bono.
    
    """
    # Busca las características del bono
    caracteristicas = bonos[bonos.nemotecnico == nemotecnico]
    
    # Busca la tabla de desarrollo
    tabla = tablas_desarrollo[tablas_desarrollo.nemotecnico == nemotecnico]

    
    # Establece el valor de la TERA,
    tera = round(caracteristicas['tasa_descuento'].iloc[0] / 100.0, 6)
    
    # la fecha de inicio del primer cupón,
    primera_fecha = caracteristicas['fecha_emision'].iloc[0]
    primera_fecha = datetime.datetime.strptime(str(primera_fecha)[0:10], "%Y-%m-%d").date()
    
    # las fechas de pago de cupón
    fechas_pago = tabla['fecha_vcto_cupon'].values
    fechas_pago = [datetime.datetime.strptime(f, "%Y-%m-%d").date() for f in fechas_pago]
    
    # y los cupones.
    flujos = (tabla['interes'] + tabla['amortizacion']).values
    
    # Se calcula el valor presente
    vpresente = valor_presente(fecha_valor, fechas_pago, flujos, tir)
    
    # Se calcula la duración.
    dvdtir = grad(valor_presente, 3)
    dur = -(1 + tir) * dvdtir(fecha_valor, fechas_pago, flujos, tir) / vpresente
    
    # Se calcula la convexidad
    d2dvdtir2 = grad(dvdtir, 3)
    conv = d2dvdtir2(fecha_valor, fechas_pago, flujos, tir)
    conv /= vpresente 
    
    # Se establecen las fechas de inicio de los cupones.
    np.insert(fechas_pago, 0, [primera_fecha])
    
    # Se establecen los saldos insolutos
    saldos_insolutos = list(tabla['saldo_insoluto'])
    
    # Se calcula el valor par.
    vpar = valor_par(fecha_valor, fechas_pago, saldos_insolutos, tera)
    
    # Se calcula el precio a 4 decimales
    precio = round(vpresente / vpar, 6)
    
    # Para el cálculo en CLP del valor de pago
    moneda = caracteristicas['unidad_monetaria'].iloc[0]
    last_uf_date = find_le(list(ufs.keys()), fecha_valor)
    valor_uf = ufs.get(fecha_valor, ufs[last_uf_date])
    
    # Se calcula el valor a pagar en unidades monetarias.
    valor_pago = precio * vpar * monto / 100.0 * (1.0 if moneda == 'CLP' else valor_uf)
    
    return {
        'nemotecnico': nemotecnico,
        'fecha_valor': fecha_valor,
        'precio': precio,
        'valor_par': vpar,
        'valor_presente': vpresente,
        'valor_pago': valor_pago,
        'duracion': dur,
        'convexidad': conv
    }