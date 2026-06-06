import pandas as pd
import os

# --- Lógica de Cana-de-açúcar ---
def calcular_insumo_cana(area, unidade):
    """
    Calcula fertilizante NPK 20-05-20 com dosagem de 500 kg por hectare.
    """
    if unidade == "m²":
        area_ha = area / 10000
    else:
        area_ha = area
        
    quantidade_insumo = area_ha * 500
    return quantidade_insumo, area_ha

# --- Lógica de Laranja ---
def calcular_ruas_laranja(largura, espacamento):
    return int(largura // espacamento)

def calcular_comprimento_ruas_laranja(total_ruas, comprimento):
    return total_ruas * comprimento

def calcular_herbicida_laranja(largura, comprimento, dose_por_hectare):
    area_m2 = largura * comprimento
    area_ha = area_m2 / 10000
    return area_ha * dose_por_hectare
