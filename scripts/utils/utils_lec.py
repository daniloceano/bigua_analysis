"""
Utilidades: Funções auxiliares para análise do Ciclo de Energia de Lorenz (LEC)
Autor: Danilo Couto de Souza
Data: 2026-07-22

Referências:
- Lorenz (1955): Available potential energy and the maintenance of the general circulation
- Li et al. (2007): Lorenz energy cycle of the global atmosphere based on reanalysis datasets
"""

import numpy as np
import xarray as xr

# --- Constantes físicas ---
R_d = 287.05  # Constante dos gases para ar seco (J kg⁻¹ K⁻¹)
c_p = 1004.0  # Calor específico a pressão constante (J kg⁻¹ K⁻¹)
g = 9.81      # Aceleração da gravidade (m s⁻²)
kappa = R_d / c_p  # Razão R/cp (~0.286)


def compute_zonal_mean(data, lon_dim='longitude'):
    """
    Calcula a média zonal de um campo.
    
    Parameters
    ----------
    data : xarray.DataArray
        Campo de dados (pode ter múltiplas dimensões)
    lon_dim : str
        Nome da dimensão de longitude
        
    Returns
    -------
    xarray.DataArray
        Média zonal (longitude colapsada)
    """
    return data.mean(dim=lon_dim)


def compute_eddy_component(data, lon_dim='longitude'):
    """
    Calcula a componente eddy (anomalia em relação à média zonal).
    
    Parameters
    ----------
    data : xarray.DataArray
        Campo de dados
    lon_dim : str
        Nome da dimensão de longitude
        
    Returns
    -------
    xarray.DataArray
        Componente eddy (data - mean_zonal)
    """
    zonal_mean = compute_zonal_mean(data, lon_dim)
    return data - zonal_mean


def compute_kinetic_energy_zonal(u_bar, v_bar):
    """
    Calcula energia cinética zonal K_Z (J kg⁻¹).
    
    K_Z = 0.5 * (u_bar² + v_bar²)
    
    Parameters
    ----------
    u_bar : xarray.DataArray
        Componente zonal do vento (média zonal) [m/s]
    v_bar : xarray.DataArray
        Componente meridional do vento (média zonal) [m/s]
        
    Returns
    -------
    xarray.DataArray
        Energia cinética zonal [J/kg]
    """
    return 0.5 * (u_bar**2 + v_bar**2)


def compute_kinetic_energy_eddy(u_prime, v_prime, lon_dim='longitude'):
    """
    Calcula energia cinética eddy K_E (J kg⁻¹).
    
    K_E = 0.5 * <u'² + v'²>
    onde <·> indica média zonal
    
    Parameters
    ----------
    u_prime : xarray.DataArray
        Anomalia zonal do vento zonal [m/s]
    v_prime : xarray.DataArray
        Anomalia zonal do vento meridional [m/s]
    lon_dim : str
        Nome da dimensão de longitude
        
    Returns
    -------
    xarray.DataArray
        Energia cinética eddy [J/kg]
    """
    return 0.5 * ((u_prime**2 + v_prime**2).mean(dim=lon_dim))


def compute_potential_temperature(T, p):
    """
    Calcula temperatura potencial θ (K).
    
    θ = T * (p0/p)^κ
    onde p0 = 1000 hPa e κ = R/cp
    
    Parameters
    ----------
    T : xarray.DataArray
        Temperatura [K]
    p : xarray.DataArray
        Pressão [Pa] ou [hPa]
        
    Returns
    -------
    xarray.DataArray
        Temperatura potencial [K]
    """
    p0 = 100000.0  # Pressão de referência (Pa)
    
    # Converter hPa → Pa se necessário
    if p.max() < 2000:  # Provavelmente em hPa
        p = p * 100.0
    
    return T * (p0 / p) ** kappa


def compute_static_stability(theta, p_dim='pressure'):
    """
    Calcula estabilidade estática σ (aproximação simplificada).
    
    σ = - (R T / p) * d(ln θ)/dp
    
    Aproximação: σ ≈ - d(θ)/dp
    
    Parameters
    ----------
    theta : xarray.DataArray
        Temperatura potencial [K]
    p_dim : str
        Nome da dimensão de pressão
        
    Returns
    -------
    xarray.DataArray
        Estabilidade estática (aproximada)
    """
    # Derivada vertical de theta
    dtheta_dp = theta.differentiate(p_dim)
    return -dtheta_dp


def compute_APE_eddy(T_prime, sigma, p, lon_dim='longitude'):
    """
    Calcula energia potencial disponível eddy P_E (J kg⁻¹).
    
    P_E = (R / (2 σ p)) * <T'²>
    
    Parameters
    ----------
    T_prime : xarray.DataArray
        Anomalia de temperatura [K]
    sigma : xarray.DataArray or float
        Estabilidade estática
    p : xarray.DataArray
        Pressão [Pa]
    lon_dim : str
        Nome da dimensão de longitude
        
    Returns
    -------
    xarray.DataArray
        APE eddy [J/kg]
    """
    # Converter hPa → Pa se necessário
    if p.max() < 2000:
        p = p * 100.0
    
    T_prime_sq = (T_prime**2).mean(dim=lon_dim)
    return (R_d / (2 * sigma * p)) * T_prime_sq


def compute_conversion_PE_KE(omega_prime, T_prime, p, lon_dim='longitude'):
    """
    Calcula conversão baroclínica C(P_E, K_E) (W kg⁻¹).
    
    C(P_E, K_E) = - (R/p) * <ω' T'>
    
    onde ω = velocidade vertical em coordenadas de pressão (Pa/s)
    
    Parameters
    ----------
    omega_prime : xarray.DataArray
        Anomalia de velocidade vertical [Pa/s]
    T_prime : xarray.DataArray
        Anomalia de temperatura [K]
    p : xarray.DataArray
        Pressão [Pa]
    lon_dim : str
        Nome da dimensão de longitude
        
    Returns
    -------
    xarray.DataArray
        Conversão baroclínica [W/kg]
    """
    # Converter hPa → Pa se necessário
    if p.max() < 2000:
        p = p * 100.0
    
    omega_T_cov = (omega_prime * T_prime).mean(dim=lon_dim)
    return -(R_d / p) * omega_T_cov


def compute_conversion_KE_KZ(u_prime, v_prime, u_bar, v_bar, 
                              lat_dim='latitude', lon_dim='longitude'):
    """
    Calcula conversão barotrópica C(K_E, K_Z) (W kg⁻¹).
    
    C(K_E, K_Z) = - <u'v'> * ∂u_bar/∂y - <v'v'> * ∂v_bar/∂y
    
    Parameters
    ----------
    u_prime, v_prime : xarray.DataArray
        Anomalias de vento [m/s]
    u_bar, v_bar : xarray.DataArray
        Ventos zonais médios [m/s]
    lat_dim : str
        Nome da dimensão de latitude
    lon_dim : str
        Nome da dimensão de longitude
        
    Returns
    -------
    xarray.DataArray
        Conversão barotrópica [W/kg]
    """
    # Covariâncias eddy
    upvp = (u_prime * v_prime).mean(dim=lon_dim)
    vpvp = (v_prime * v_prime).mean(dim=lon_dim)
    
    # Gradientes meridionais da média zonal
    dubar_dy = u_bar.differentiate(lat_dim)
    dvbar_dy = v_bar.differentiate(lat_dim)
    
    return -(upvp * dubar_dy + vpvp * dvbar_dy)


def integrate_vertically(data, p_dim='pressure'):
    """
    Integra verticalmente um campo (ponderado por pressão).
    
    Integral = (1/g) * ∫ data dp
    
    Parameters
    ----------
    data : xarray.DataArray
        Campo a integrar
    p_dim : str
        Nome da dimensão de pressão
        
    Returns
    -------
    xarray.DataArray
        Campo integrado verticalmente [unidade original × Pa / g]
    """
    # Usar integração trapezoidal
    # Se pressão em hPa, converter para Pa
    p = data[p_dim]
    if p.max() < 2000:
        p = p * 100.0
    
    # Integrar usando xarray (assume eixo de pressão ordenado)
    integrated = data.integrate(p_dim)
    
    return integrated / g


def print_lec_summary(KZ, KE, PZ, PE):
    """
    Imprime resumo dos termos do LEC.
    
    Parameters
    ----------
    KZ, KE, PZ, PE : xarray.DataArray ou float
        Termos de energia
    """
    print("=" * 60)
    print("RESUMO — TERMOS DO CICLO DE ENERGIA DE LORENZ")
    print("=" * 60)
    print(f"  K_Z (Energia Cinética Zonal):  {float(KZ):.2e} J/kg")
    print(f"  K_E (Energia Cinética Eddy):   {float(KE):.2e} J/kg")
    print(f"  P_Z (APE Zonal):               {float(PZ):.2e} J/kg")
    print(f"  P_E (APE Eddy):                {float(PE):.2e} J/kg")
    print(f"\n  Total KE = K_Z + K_E:          {float(KZ + KE):.2e} J/kg")
    print(f"  Total APE = P_Z + P_E:         {float(PZ + PE):.2e} J/kg")
    print("=" * 60)


# --- Testes (executar apenas se chamado diretamente) ---
if __name__ == "__main__":
    print("Módulo de utilidades LEC carregado com sucesso!")
    print("\nFunções disponíveis:")
    print("  - compute_zonal_mean")
    print("  - compute_eddy_component")
    print("  - compute_kinetic_energy_zonal")
    print("  - compute_kinetic_energy_eddy")
    print("  - compute_potential_temperature")
    print("  - compute_static_stability")
    print("  - compute_APE_eddy")
    print("  - compute_conversion_PE_KE")
    print("  - compute_conversion_KE_KZ")
    print("  - integrate_vertically")
    print("  - print_lec_summary")
