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
