import numpy as np
import pandas as pd
from . import model
from . import phases
from . import chemistry as chem


def get_default_liquid_mol_oxide_comp() -> pd.Series:
    dry_MORB_wt_oxides = pd.Series({
        'SiO2':48.68,'TiO2':1.01,
        'Al2O3':17.64,'Fe2O3':0.89,'Cr2O3':0.0425,
        'FeO':07.59 ,'MnO':0,'MgO':9.10,
        'NiO':0,'CoO':0,'CaO':12.45,
        'Na2O':2.65,'K2O':0.03,
        'P2O5':0,'H2O':0,'CO2':0})
    mol_oxides = dry_MORB_wt_oxides/chem.WT_OXIDES
    mol_oxides /= mol_oxides.sum()
    
    return mol_oxides

def _empirical_redox_buffer(T, P, A=0, B=0, C=0, D=0,
                            ignore_lims=True, Tlims=None):

    logfO2 = A/T + B + C*(P-1)/T + D*np.log(T)

    if (not ignore_lims) and (Tlims is not None):
        logfO2[T<Tlims[0]] = np.nan
        logfO2[T>=Tlims[1]] = np.nan

    return logfO2

def _redox_state_Kress91(T, P, oxide_comp, logfO2=None):
    """
    Fe redox model of Kress and Carmichael 1991

    Calculate ln(Fe2O3/FeO) ratio given lnfO2, T, P, bulk composition.
    Alternatively, can predict lnfO2 values given measured ferric & ferrous comp.

    Parameters
    ----------
    T : double (array)
        temperature in Kelvin
    P : double (array)
        pressure in bars
    oxide_comp : double array (matrix)
        molar oxide composition in standard order. Either measured FeO and Fe2O3 are
        provided, or total iron reported as FeO (e.g. FeO*)
    logfO2 : double (array), default None
        If provided, the measured logfO2 value is used to predict the ln(Fe2O3/FeO).
        Otherwise, reported FeO and Fe2O3 values are used to predict logfO2.




    Returns
    -------
     output : double (array)
         Output depends on whether logfO2 values are provided.
         ln_Fe_oxide_ratio : If logfO2 values are given, return log ferric/ferrous ratio of melt.
         logfO2 : If not, return predicted logfO2, given measured ferric and ferrous content of melt.

    """

    predict_fO2 = False
    if logfO2 is None:
        predict_fO2 = True


    OXIDES = chem.OXIDES
    # ['SiO2', 'TiO2', 'Al2O3', 'Fe2O3', 'Cr2O3', 'FeO', 'MnO', 'MgO',
    #    'NiO', 'CoO', 'CaO', 'Na2O', 'K2O', 'P2O5', 'H2O', 'CO2']

    T0 =  1673.15  # K

    a  =  0.196
    b  =  1.1492e4 # K
    c  = -6.675
    e  = -3.364
    f  = -7.01e-7  * 1.0e5 # K/bar
    g  = -1.54e-10 * 1.0e5 # 1/bar
    h =   3.85e-17 * 1.0e5 * 1.0e5 # K/bar^2
    # dAl2O3 = -2.243
    # dFeO   = -1.828
    # dCaO   =  3.201
    # dNa2O  =  5.854
    # dK2O   =  6.215

    mol_oxides = np.array(oxide_comp.copy())

    # from IPython import embed; embed()
    XFeO_equiv = mol_oxides[:, OXIDES=='FeO'] + 2*mol_oxides[:, OXIDES=='Fe2O3']
    # print(mol_oxides.shape)
    # print(XFeO_equiv.shape)

    if predict_fO2:
        ln_Fe_oxide_ratio = np.squeeze(np.log(mol_oxides[:, OXIDES=='Fe2O3']/mol_oxides[:, OXIDES=='FeO']))
        # display(ln_Fe_oxide_ratio)

    mol_oxides[:, OXIDES=='FeO'] = XFeO_equiv
    mol_oxides[:, OXIDES=='Fe2O3'] = 0.0
    if mol_oxides.ndim==2:
        mol_oxide_tot = np.sum(mol_oxides, axis=1)
        mol_oxides /= mol_oxide_tot[:,np.newaxis]
    elif mol_oxides.ndim==1:
        mol_oxide_tot = np.sum(mol_oxides)
        mol_oxides /= mol_oxide_tot
    else:
        assert False, 'mol_oxides must be either an array of compositions, or a matrix for many experiments'


    d = np.zeros(len(OXIDES))
    d[OXIDES=='Al2O3'] = -2.243
    d[OXIDES=='FeO']   = -1.828
    d[OXIDES=='CaO']   = +3.201
    d[OXIDES=='Na2O']  = +5.854
    d[OXIDES=='K2O']   = +6.215

    atm_terms = b/T + c + e*(1.0-T0/T - np.log(T/T0))
    press_terms = f*P/T + g*(T-T0)*P/T+ h*P*P/T
    comp_terms = np.dot(mol_oxides, d)

    if not predict_fO2:
        lnfO2 = logfO2/np.log10(np.exp(1))
        ln_Fe_oxide_ratio =  a*lnfO2 + atm_terms + press_terms + comp_terms
        return ln_Fe_oxide_ratio
    else:
        # print(ln_Fe_oxide_ratio )
        # print((atm_terms + press_terms + comp_terms))
        lnfO2 = (ln_Fe_oxide_ratio -
                 (atm_terms + press_terms + comp_terms))/a
        logfO2 = lnfO2*np.log10(np.exp(1))
        return logfO2


def redox_state(T, P, oxide_comp=None, logfO2=None,
                phase_of_interest=None, method=None):
    """
    Parameters
    ----------
    T : array-like
        Temperature in Kelvin.
    P : array-like
        Pressure in bars.
    oxide_comp : dict of arrays, optional
        Molar oxide composition of each phase.
    logfO2 : double (array), optional
        Base 10 logfO2 values with fO2 in bars
    phase_of_interest : {'Liq', 'Spl'}
        Abbreviation of redox-sensitive phase used to determine
        redox state.
    method : {'consistent', 'coexist', 'stoich', 'Kress91'}
        'consistent' :
        'coexist' :
        'stoich' :
        'Kress91' :

    """

    def not_implemented_error(method, phase_of_interest):
        raise NotImplementedError(
            'The method "'+method+'" is not implemented ' +
            'for phase_of_interest "'+phase_of_interest+'".')

    output = None

    if phase_of_interest=='Liq':
        if method=='Kress91':
            if oxide_comp['Liq'].ndim==1:
                oxide_comp['Liq'] = oxide_comp['Liq'][np.newaxis, :]

            liq_oxide_comp = oxide_comp['Liq']
            # print(liq_oxide_comp.shape)

            output = _redox_state_Kress91(
                T, P, liq_oxide_comp, logfO2=logfO2)

            if logfO2 is None:
                logfO2 = output
            else:
                ln_Fe_oxide_ratio =  output
                Fe_oxide_ratio = np.exp(ln_Fe_oxide_ratio)
                ind_FeO = np.where(chem.OXIDES=='FeO')[0][0]
                ind_Fe2O3 = np.where(chem.OXIDES=='Fe2O3')[0][0]

                XFeO = liq_oxide_comp[:, ind_FeO]
                XFe2O3 = liq_oxide_comp[:, ind_Fe2O3]
                XFeOs = XFeO + 2*XFe2O3
                XFeO = XFeOs/(1+2*Fe_oxide_ratio)
                XFe2O3 = 0.5*(XFeOs - XFeO)

                oxide_comp['Liq'][:, ind_FeO] = XFeO
                oxide_comp['Liq'][:, ind_Fe2O3] = XFe2O3

        else:
            not_implemented_error(method, phase_of_interest)

    elif phase_of_interest=='Spl':
        not_implemented_error(method, phase_of_interest)
    else:
        not_implemented_error(method, phase_of_interest)

    return output


def _O2_chem_potential(T, P):
    Tref = 298.15
    Cp_k0 = 23.10248
    Cp_k1 = 804.8876
    Cp_k2 = 1762835.0
    Cp_k3 = 0.0
    Cp_l1 = 18172.91960
    Cp_Tt = 0.002676
    Hs = (23.10248*(T-Tref) + 2.0*804.8876*(np.sqrt(T)-np.sqrt(Tref))
          - 1762835.0*(1.0/T-1.0/Tref) - 18172.91960*np.log(T/Tref)
          + 0.5*0.002676*(T*T-Tref*Tref))
    Ss = (205.15 + 23.10248*np.log(T/Tref)
          - 2.0*804.8876*(1.0/np.sqrt(T)-1.0/np.sqrt(Tref))
          - 0.5*1762835.0*(1.0/(T*T)-1.0/(Tref*Tref))
          + 18172.91960*(1.0/T-1.0/Tref) + 0.002676*(T-Tref))
    mu_O2 = Hs - T*Ss
    return mu_O2

def _consistent_redox_buffer_QFM(T, P):

    MODELDB_v1_0 = model.Database(database_name="MELTS_v1_0")
    Qz = MODELDB_v1_0.get_phase('Qz')
    Fa = MODELDB_v1_0.get_phase('Fa')
    Mag = MODELDB_v1_0.get_phase('Mag')
    
    mu_O2 = _O2_chem_potential(T, P)

    mu_Qz = Qz.gibbs_energy(T, P, deriv={'dmol':1}).squeeze()
    mu_Fa = Fa.gibbs_energy(T, P, deriv={'dmol':1}).squeeze()
    mu_Mag = Mag.gibbs_energy(T, P, deriv={'dmol':1}).squeeze()

    dGr0 = 2*mu_Mag + 3*mu_Qz - 3*mu_Fa - mu_O2
    logfO2 = 1/(2.303*8.314*T)*dGr0
    return logfO2
# 
# def _consistent_redox_buffer_HM(T, P):
#     mu_O2 = _O2_chem_potential(T, P)
# 
#     mu_Hem = get_phase('Hem').chem_potential(T, P)
#     mu_Mag = get_phase('Mag').chem_potential(T, P)
# 
#     dGr0 = 6*mu_Hem - 4*mu_Mag - mu_O2
#     logfO2 = 1/(2.303*8.314*T)*dGr0
#     return logfO2



def redox_buffer(T, P, buffer=None, method=None,
                 ignore_lims=True):
    """
    Calculate logfO2 values for common oxygen buffers.

    Parameters
    ----------
    T : double (array)
        Temperature in Kelvin
    P : double (array)
        Pressure in bars
    buffer : {'IW', 'IM', 'NNO', 'Co+CoO', 'Cu+Cu2O', ('HM'/'MH'),
              ('MW'/'WM'), 'MMO', 'CCO', ('QFM'/'FMQ'), 'QIF'}
        Models of common oxygen fugacity buffer systems with sources.
        'IW' : Iron-Wustite [1?,2,3]
        'IM' : Iron-Magnetite [1?,3]
        'NNO' : Nickel-Nickel Oxide [2,3]
        'Co+CoO' : Cobalt-Cobalt Oxide [3]
        'Cu+Cu2O' : Copper-Copper Oxide [2]
        'HM' or 'MH' : Magnetite-Hematite [1,2,3]
        'MW' or 'WM' : Magnetite-Wustite [1?,2,3]
        'MMO' : MnO-Mn3O4 [2]
        'CCO' : Graphite-CO-CO2 [2]
        'QFM' or 'FMQ' : Quartz-Fayalite-Magnetite [1,2,3]
        'QIF' : Quartz-Iron-Fayalite [1?,3]
    method : {'consistent', 'LEPR', 'Frost1991'}
        Method used to calculate redox buffer value. Default depends on
        buffer availability (see above), in preference order
        {'consistent', 'LEPR', 'Frost1991'}.
        [1] 'consistent' : Directly evaluate chemical potentials for each
            phase using current thermodynamic database
        [2] 'LEPR' : Empirical expressions constructed for LEPR database
            (Hirschmann et al. 2008) based on previously published studies
        [3] 'Frost91' : Empirical expressions from review article
            Frost 1991

    Returns
    -------
    logfO2 : double (array)
        Base 10 logfO2 values with fO2 in bars


    Publication Sources
    -------------------
    [1] consistent method based on MELTS thermodynamic database,
        incorporating Berman 1988 and ???
    [2] M. Hirschmann et al. (2008) Library of Experimental Phase Relations
        (LEPR): A database and Web portal for experimental magmatic
        phase equilibria data
    [3] B. R. Frost (1991) Introduction to oxygen fugacity and
        its petrologic importance

    """
    BUFFER_OPTS = ['IW', 'IM', 'NNO', 'Co+CoO', 'Cu+Cu2O', 'HM', 'MH',
                   'MW', 'WM', 'MMO', 'CCO', 'QFM', 'FMQ', 'QIF']
    assert buffer in BUFFER_OPTS, (
        'Selected buffer ' + buffer + ' is not available. Please select from ' + str(BUFFER_OPTS)
    )

    def not_implemented_error(method, buffer):
        raise NotImplementedError(
            'The method "'+method+'" is not implimented ' +
            'for the redox buffer "'+buffer+'".')

    if buffer=='IW':
        method = 'LEPR' if method is None else method
        if method=='consistent':
            not_implemented_error(method, buffer)
        elif method=='LEPR':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-28776.8, B=14.057, C=.055, D=-.8853)
        elif method=='Frost91':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-27489, B=6.702, C=.055, ignore_lims=ignore_lims,
                Tlims=np.array([565, 1200])+273.15)
        else:
            not_implemented_error(method, buffer)

    elif buffer=='IM':
        method = 'Frost91' if method is None else method
        if method=='consistent':
            not_implemented_error(method, buffer)
        elif method=='LEPR':
            not_implemented_error(method, buffer)
        elif method=='Frost91':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-28690.6, B=8.13, C=.056,
                ignore_lims=ignore_lims,
                Tlims=np.array([300, 565])+273.15)
        else:
            not_implemented_error(method, buffer)

    elif buffer=='NNO':
        method = 'LEPR' if method is None else method
        if method=='consistent':
            not_implemented_error(method, buffer)
        elif method=='LEPR':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-25018.7, B=12.981, C=0.046, D=-0.5117)
        elif method=='Frost91':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-24930, B=9.36, C=.046, ignore_lims=ignore_lims,
                Tlims=np.array([600, 1200])+273.15)
        else:
            not_implemented_error(method, buffer)

    elif buffer=='Co+CoO':
        method = 'Frost91' if method is None else method
        if method=='consistent':
            not_implemented_error(method, buffer)
        elif method=='LEPR':
            not_implemented_error(method, buffer)
        elif method=='Frost91':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-24332.6, B=7.295, C=0.052,
                ignore_lims=ignore_lims,
                Tlims=np.array([600, 1200])+273.15)
        else:
            not_implemented_error(method, buffer)

    elif buffer=='Cu+Cu2O':
        method = 'LEPR' if method is None else method
        if method=='consistent':
            not_implemented_error(method, buffer)
        elif method=='LEPR':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-18162.2, B=12.855, C=0, D=-.6741)
        elif method=='Frost91':
            not_implemented_error(method, buffer)
        else:
            not_implemented_error(method, buffer)

    elif buffer in ['HM', 'MH']:
        method = 'consistent' if method is None else method
        if method=='consistent':
            not_implemented_error(method, buffer)
            # logfO2 = _consistent_redox_buffer_HM(T, P)
        elif method=='LEPR':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-25632, B=14.620, C=0.019)
        elif method=='Frost91':
            logfO2_T1 = _empirical_redox_buffer(
                T, P, A=-25497.5, B=14.33, C=.019,
                ignore_lims=ignore_lims,
                Tlims=np.array([300, 573])+273.15)
            logfO2_T2 = _empirical_redox_buffer(
                T, P, A=-26452.6, B=15.455, C=.019,
                Tlims=np.array([573, 682])+273.15,
                ignore_lims=ignore_lims)
            logfO2_T3 = _empirical_redox_buffer(
                T, P, A=-25700.6, B=14.558, C=.019,
                Tlims=np.array([682, 1100])+273.15,
                ignore_lims=ignore_lims)

            logfO2 = np.vstack((logfO2_T1, logfO2_T2, logfO2_T3))
            logfO2 = np.nanmean(logfO2, axis=0)
        else:
            not_implemented_error(method, buffer)

    elif buffer in ['MW', 'WM']:
        method = 'LEPR' if method is None else method
        if method=='consistent':
            not_implemented_error(method, buffer)
        elif method=='LEPR':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-30396, B=-3.427, C=0.083, D=2.0236)
        elif method=='Frost91':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-32807, B=13.012, C=.083,
                Tlims=np.array([565, 1200])+273.15,
                ignore_lims=ignore_lims)
        else:
            not_implemented_error(method, buffer)

    elif buffer=='MMO':
        method = 'LEPR' if method is None else method
        if method=='consistent':
            not_implemented_error(method, buffer)
        elif method=='LEPR':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-29420.7, B=92.025, C=0, D=-11.517)
        elif method=='Frost91':
            not_implemented_error(method, buffer)
        else:
            not_implemented_error(method, buffer)


    elif buffer=='CCO':
        method = 'LEPR' if method is None else method
        if method=='consistent':
            not_implemented_error(method, buffer)
        elif method=='LEPR':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-21803, B=4.325, C=0.171)
        elif method=='Frost91':
            not_implemented_error(method, buffer)
        else:
            not_implemented_error(method, buffer)

    elif buffer in ['QFM', 'FMQ']:
        method = 'consistent' if method is None else method
        if method=='consistent':
            # not_implemented_error(method, buffer)
            logfO2 = _consistent_redox_buffer_QFM(T, P)
        elif method=='LEPR':
            logfO2 = _empirical_redox_buffer(
                T, P, A=-30686, B=82.760, C=.094, D=-10.620)
        elif method=='Frost91':
            logfO2 = _empirical_redox_buffer(
                T, P, A=0, B=0, C=0, ignore_lims=ignore_lims,
                Tlims=np.array([0, 0])+273.15)

            logfO2_T1 = _empirical_redox_buffer(
                T, P, A=-26455.3, B=10.344, C=.092,
                Tlims=np.array([400, 573])+273.15,
                ignore_lims=ignore_lims)
            logfO2_T2 = _empirical_redox_buffer(
                T, P, A=-25096.3, B=8.735, C=.110,
                Tlims=np.array([573, 1200])+273.15,
                ignore_lims=ignore_lims)

            logfO2 = np.vstack((logfO2_T1, logfO2_T2))
            logfO2 = np.nanmean(logfO2, axis=0)
        else:
            not_implemented_error(method, buffer)

    elif buffer=='QIF':
        method = 'Frost91' if method is None else method
        if method=='consistent':
            not_implemented_error(method, buffer)
        elif method=='LEPR':
            not_implemented_error(method, buffer)
        elif method=='Frost91':
            logfO2_T1 = _empirical_redox_buffer(
                T, P, A=-29435.7, B=7.391, C=.044,
                Tlims=np.array([150, 573])+273.15,
                ignore_lims=ignore_lims)
            logfO2_T2 = _empirical_redox_buffer(
                T, P, A=-29520.8, B=7.492, C=.05,
                Tlims=np.array([573, 1200])+273.15,
                ignore_lims=ignore_lims)

            logfO2 = np.vstack((logfO2_T1, logfO2_T2))
            logfO2 = np.nanmean(logfO2, axis=0)
        else:
            not_implemented_error(method, buffer)

    return logfO2





def buffer(T, buffer, dlogfO2=0., P=1.):
    logfO2 = redox_buffer(
        T, P, buffer=buffer)+dlogfO2
    return logfO2

def calc_total_Fe(mol_oxides:pd.Series) -> float:
    return 2*mol_oxides['Fe2O3'] + mol_oxides['FeO']

def get_redox_ratio(mol_oxides:pd.Series) -> float:
    return mol_oxides['Fe2O3']/mol_oxides['FeO']

def impose_redox_ratio(ratio:float, mol_oxides:pd.Series) -> pd.Series:
    mol_oxides_adj = mol_oxides.copy()
    
    total_Fe = calc_total_Fe(mol_oxides)
    FeO_fac = 1/(1+2*ratio)
    
    FeO = FeO_fac*total_Fe
    # Fe2O3 = FeO_fac*ratio*total_Fe
    Fe2O3 = 0.5*(total_Fe-FeO)
    
    mol_oxides_adj['Fe2O3'] = Fe2O3
    mol_oxides_adj['FeO'] = FeO
    
    return mol_oxides_adj



class ONeill18():
    fO2_coef = 0.25
    redox_ratio_coef = -1.35

    comp_coefs = pd.Series(0.0, index=chem.OXIDES)
    comp_coefs['Na2O']  = +0.034
    comp_coefs['K2O']   = +0.044
    comp_coefs['CaO']   = +0.023
    comp_coefs['P2O5']  = -0.018

    # @classmethod
    # def calc_liquid_logfO2(cls, T:float, P:float, mol_oxides:pd.Series):

    #     log_redox_ratio = np.log10(get_redox_ratio(mol_oxides))

    #     wt_oxides = mol_oxides*chem.WT_OXIDES[mol_oxides.index]
    #     wt_oxides = wt_oxides/wt_oxides.sum()

    #     dQFM_1bar = wtcomp.dot(coefs_Oneill18)
    #     wt_oxides.dot(d)

    @classmethod
    def calc_redox_ratio(cls, logfO2:float, T:float, P:float, 
                                mol_oxides:pd.Series):
        assert False, 'This class not yet fully implemented!!'

        QFM = buffer(T, 'QFM', P=P)
        dQFM = logfO2 - QFM

        wt_oxides = cls._calc_wt_oxides(mol_oxides)

        log_redox_ratio = cls.fO2_coef*dQFM + cls.redox_ratio_coef + wt_oxides.dot(cls.comp_coefs)
        return 10**log_redox_ratio
    
    @classmethod
    def _calc_wt_oxides(cls, mol_oxides:pd.Series) -> pd.Series:
        assert False, 'This class not yet fully implemented!!'

        wt_oxides = mol_oxides*chem.WT_OXIDES[mol_oxides.index]
        wt_oxides = 100*wt_oxides/wt_oxides.sum()
        return wt_oxides
        
class MELTSLiq():

    def _eval_liq_mu0(T, P, endmem_name, Liq): 
        mol_pure_endmem = 1.0*(Liq.endmember_names==endmem_name)
        mu0 = Liq.gibbs_energy(T, P, mol=mol_pure_endmem)
        return mu0.squeeze()
    
    def _filter_X_liq(X_liq, Wh):
        X_liq = X_liq.copy()
        X_liq = (X_liq.T/X_liq.sum(axis=1)).T

        drop_components = ['MnSi0.5O2','NiSi0.5O2','CoSi0.5O2','H2O','CO2']
        X_liq = X_liq.drop(columns=drop_components, errors='ignore')
        X_liq.columns = Wh.columns

        return X_liq
    
    @classmethod
    def _eval_oxy_energetics(cls, T, P, X_liq, Wh, Liq):
        oxy_energy = {}
        
        mu_O2_0 = np.array([O2.gibbs_energy(iT) for iT in T])

        mu_oxy_0 = (+cls._eval_liq_mu0(T, P, 'Fe2O3', Liq)
                    +cls._eval_liq_mu0(T, P, 'SiO2', Liq)
                    -cls._eval_liq_mu0(T, P, 'Fe2SiO4', Liq))
        
        oxy_energy['dmu_oxy_0'] = mu_oxy_0 - 0.5*mu_O2_0 
        oxy_energy['Wh_oxy'] = Wh['Fe3+'] + Wh['Si'] - Wh['Fe2+']
        oxy_energy['G_ex'] = 0.5*(X_liq.dot(Wh)*X_liq).sum(axis=1)

        return oxy_energy
    
    @classmethod
    def _adjust_Fe_cation_ratio(cls, X_liq, Fe_cation_ratio) -> pd.DataFrame:
        if type(X_liq) is not pd.DataFrame:
            X_liq = pd.DataFrame(X_liq).T

        Fe2_tot = X_liq['Fe2O3'] + X_liq['Fe2SiO4']
        Si_tot = X_liq['SiO2'] + X_liq['Fe2SiO4']

        Fe3p = Fe2_tot*Fe_cation_ratio/(1+Fe_cation_ratio)
        Fe2p = Fe2_tot - Fe3p
        Si = Si_tot - Fe2p

        X_liq['Fe2O3'] = Fe3p
        X_liq['Fe2SiO4'] = Fe2p
        X_liq['SiO2'] = Si

        X_liq = (X_liq.T/X_liq.sum(axis=1)).T
        return X_liq
    
    @classmethod
    def update_redox(cls, T, P, logfO2, X_liq, Wh, Liq, 
                     count_max=5, wt_next=.3, print_ind=None):
        
        T, P, X_liq = chem.broadcast_exp_conditions(T, P, X_liq)


        
        count = 1
        ln_cation_ratio = cls.ln_Fe_cation_ratio(
            T, P, logfO2, X_liq, Wh, Liq)
        Fe_cation_ratio = np.exp(ln_cation_ratio)
        X_liq = 0.5*(X_liq + cls._adjust_Fe_cation_ratio(X_liq, Fe_cation_ratio))

        while True:
            if count >= count_max:
                break

            count = count + 1 

            ln_cation_ratio_next = cls.ln_Fe_cation_ratio(T, P, logfO2, X_liq, Wh, Liq)
            ln_cation_ratio = (1-wt_next)*ln_cation_ratio + wt_next*ln_cation_ratio_next
            Fe_cation_ratio = np.exp(ln_cation_ratio)

            X_liq = cls._adjust_Fe_cation_ratio(X_liq, Fe_cation_ratio)

            if print_ind is not None:
                print(ln_cation_ratio[print_ind])

        return X_liq

    @classmethod
    def ln_Fe_cation_ratio(cls, T:np.array, P:np.array, logfO2:np.array, 
                           X_liq:pd.DataFrame, Wh:pd.DataFrame, 
                           Liq:phases.SolutionPhase):
        
        T, P, X_liq = chem.broadcast_exp_conditions(T, P, X_liq)
        X_liq = cls._filter_X_liq(X_liq, Wh)

        oxy_energy = cls._eval_oxy_energetics(T, P, X_liq, Wh, Liq)

        RT = chem.RGAS*T
        ln_cation_ratio = (0.5*logfO2*np.log(10) - np.log(X_liq['Si']) 
                           -1/RT*(+oxy_energy['dmu_oxy_0'] 
                                  +X_liq.dot(oxy_energy['Wh_oxy']) 
                                  -oxy_energy['G_ex']))
        return ln_cation_ratio

    @classmethod
    def logfO2(cls, T:np.array, P:np.array, X_liq:pd.DataFrame,
               Wh:pd.DataFrame, Liq:phases.SolutionPhase):
        
        T, P, X_liq = chem.broadcast_exp_conditions(T, P, X_liq)
        X_liq = cls._filter_X_liq(X_liq, Wh)

        oxy_energy = cls._eval_oxy_energetics(T, P, X_liq, Wh, Liq)

        RT = chem.RGAS*T
        logfO2_eq = 2/(RT*np.log(10))*(
            RT*np.log(X_liq['Si']*X_liq['Fe3+']/X_liq['Fe2+']) 
            + oxy_energy['dmu_oxy_0'] + X_liq.dot(oxy_energy['Wh_oxy']) 
            - oxy_energy['G_ex'])
        
        return logfO2_eq
    
class KressSpecies():

    R = chem.RGAS
    y = 0.3
    K2 = 0.4
    T0=1673


    rxn = {
        'dH0' :-106.2e3,
        'dS0' : -55.1,
        'dCP0':  31.86,
        }

    dW = pd.Series({
        'Al2O3':  39.86e3,
        'CaO'  : -65.52e3,
        'Na2O' :-102.0e3,
        'K2O'  :-119.0e3,
        }, index=chem.OXIDES).fillna(0)

    @classmethod
    def ln_Fe_cation_ratio(cls, T:np.array, P:np.array, logfO2:np.array, 
                           X_liq:pd.DataFrame):
        
        T, P, X_liq = chem.broadcast_exp_conditions(T, P, X_liq)

        if np.any(P>1.1):
            assert False, 'High pressure not yet implemented for Kress Species model'

        R = cls.R
        RT = R*T

        y = cls.y
        K2 = cls.K2


        fO2 = 10**logfO2

        KD1 = np.exp(-cls.rxn['dH0']/RT +cls.rxn['dS0']/R 
             -cls.rxn['dCP0']/R*(1-cls.T0/T-np.log(T/cls.T0))
             -1/RT*cls.dW.dot(X_liq.T))

        ln_Fe_cation_ratio = (
            +np.log(KD1*fO2**0.25 + 2*y*K2*KD1**(2*y)*fO2**(y/2))
            -np.log(1 + (1-2*y)*K2*KD1**(2*y)*fO2**(y/2)))
        return ln_Fe_cation_ratio

class Kress91():
    T0 =  1673.15  # K
    d = pd.Series(0.0, index=chem.OXIDES)
    d['Al2O3'] = -2.243
    d['FeO']   = -1.828
    d['CaO']   = +3.201
    d['Na2O']  = +5.854
    d['K2O']   = +6.215
    
    PARAMS = {
        'a':0.196,
        'b':1.1492e4, # K
        'c':-6.675,
        'e':-3.364,
        'f':-7.01e-7  * 1.0e5, # K/bar
        'g':-1.54e-10 * 1.0e5, # 1/bar
        'h':3.85e-17 * 1.0e5 * 1.0e5, # K/bar^2
        'd': d,
    }

    @classmethod
    def ln_Fe_oxide_ratio(cls, T:np.array, P:np.array, logfO2:np.array, 
                          mol_oxides:pd.DataFrame) -> np.array:
        
        PARAMS = cls.PARAMS
        T, P, mol_oxides = chem.broadcast_exp_conditions(T, P, mol_oxides)

        env_comp_terms = cls._calc_all_env_comp_terms(
            T, P, mol_oxides)

        lnfO2 = logfO2*np.log(10)
        ln_ratio = PARAMS['a']*lnfO2 + env_comp_terms
        return ln_ratio
    
    @classmethod
    def logfO2(cls, T:np.array, P:np.array, mol_oxides:pd.DataFrame):
        PARAMS = cls.PARAMS
        T, P, mol_oxides = chem.broadcast_exp_conditions(T, P, mol_oxides)
        
        env_comp_terms = cls._calc_all_env_comp_terms(
            T, P, mol_oxides)
        
        ln_ratio = np.log(mol_oxides['Fe2O3']/mol_oxides['FeO'])

        lnfO2 = (ln_ratio - env_comp_terms)/PARAMS['a']
        logfO2 = lnfO2/np.log(10)

        return logfO2
    
    @classmethod
    def calc_redox_ratio(cls, logfO2:float, T:float, P:float, 
                                mol_oxides:pd.Series) -> float:
        PARAMS = cls.PARAMS
        env_comp_terms = cls._calc_env_comp_terms(
            T, P, mol_oxides)
        
        lnfO2 = logfO2*np.log(10)
        ln_ratio = PARAMS['a']*lnfO2 + env_comp_terms
        return np.exp(ln_ratio)

    @classmethod
    def calc_logfO2(cls, T:float, P:float, mol_oxides:pd.Series):
        PARAMS = cls.PARAMS
        env_comp_terms = cls._calc_env_comp_terms(
            T, P, mol_oxides)
        ln_ratio = np.log(get_redox_ratio(mol_oxides))
        
        lnfO2 = 1/PARAMS['a']*(ln_ratio - env_comp_terms)
        logfO2 = lnfO2/np.log(10)
        
        return logfO2
    
    @classmethod
    def _standardize_mol_oxide_comp(cls, mol_oxides:pd.Series):
        mol_oxides_std = mol_oxides.copy()

        mol_oxides_std['FeO'] = calc_total_Fe(mol_oxides)
        mol_oxides_std['Fe2O3'] = 0
        mol_oxides_std /= mol_oxides_std.sum()
        return mol_oxides_std
    
    @classmethod
    def _calc_all_env_comp_terms(cls, T:np.array, P:np.array, 
                                 mol_oxides:pd.DataFrame) -> np.array:
        T0 = cls.T0
        PARAMS = cls.PARAMS


        # mol_oxides_std = cls._standardize_mol_oxide_comp(mol_oxides)

        mol_oxides_std = mol_oxides.copy()
        mol_Fe_tot = mol_oxides_std['FeO']+mol_oxides_std['Fe2O3']
        mol_oxides_std['FeO'] = mol_Fe_tot
        mol_oxides_std['Fe2O3'] = 0
        mol_oxides_std = (mol_oxides_std.T/mol_oxides_std.sum(axis=1)).T
        
        atm_terms = (PARAMS['b']/T + PARAMS['c'] + 
                     PARAMS['e']*(1.0-T0/T - np.log(T/T0)))
        press_terms = (PARAMS['f']*P/T + PARAMS['g']*(T-T0)*P/T+ 
                       PARAMS['h']*P*P/T)
        comp_terms = np.dot(mol_oxides_std, PARAMS['d'])

        return atm_terms + press_terms + comp_terms
        
    @classmethod
    def _calc_env_comp_terms(cls, T:float, P:float, 
                             mol_oxides:pd.Series) -> float:
        T0 = cls.T0
        PARAMS = cls.PARAMS


        mol_oxides_std = cls._standardize_mol_oxide_comp(mol_oxides)

        atm_terms = (PARAMS['b']/T + PARAMS['c'] + 
                     PARAMS['e']*(1.0-T0/T - np.log(T/T0)))
        press_terms = (PARAMS['f']*P/T + PARAMS['g']*(T-T0)*P/T+ 
                       PARAMS['h']*P*P/T)
        comp_terms = np.dot(mol_oxides_std, PARAMS['d'])

        return atm_terms + press_terms + comp_terms





def calc_logfO2_from_liquid_comps(exp_cond_table:pd.DataFrame, 
                                  mol_oxide_table:pd.DataFrame,
                                  redox_model=Kress91) -> pd.Series:
    
    liquid_data = pd.concat((exp_cond_table, mol_oxide_table), axis=1)
    logfO2 = []
    for _, exp in liquid_data.iterrows():
        mol_oxides = exp[chem.OXIDES]
        ilogfO2 = calc_logfO2_from_liquid_comp(exp['T'], exp['P'], mol_oxides)
        logfO2.append(ilogfO2)
        
    return pd.Series(logfO2, index=liquid_data.index)
        
    
def calc_logfO2_from_liquid_comp(T:float, P:float, mol_oxides:pd.Series,
                                 redox_model=Kress91) -> float:
    
    return redox_model.calc_logfO2(T, P, mol_oxides)

def adjust_liquid_redox_ratio(logfO2:float, T:float, P:float,
                              mol_oxides:pd.Series,
                              redox_model=Kress91) -> pd.Series:
    
    redox_ratio = redox_model.calc_redox_ratio(logfO2, T, P, mol_oxides)
    return impose_redox_ratio(redox_ratio, mol_oxides)

def adjust_all_liquid_redox_ratios(liquid_table:pd.DataFrame,
                                   model=Kress91):
    
    liquid_table_adj = liquid_table.copy()
    mol_oxides_adj_all = []
    for index, exp in liquid_table.iterrows():
        mol_oxides = exp[chem.OXIDES]
        mol_oxides_adj = adjust_liquid_redox_ratio(
            exp['logfO2'],exp['T'],exp['P'],mol_oxides,
            redox_model=model)
        mol_oxides_adj_all.append(mol_oxides_adj)
        # liquid_table_adj.loc[index,chem.OXIDES] = mol_oxides_adj
        
    liquid_table_adj[chem.OXIDES] = chem.normalize_comp(np.array(mol_oxides_adj_all))
        
    return liquid_table_adj

def get_all_redox_ratios(liquid_table:pd.DataFrame) -> pd.Series:
    redox_ratios = []
    for _, exp in liquid_table.iterrows():
        mol_oxides = exp[chem.OXIDES]
        redox_ratios.append(get_redox_ratio(mol_oxides))

    return pd.Series(redox_ratios, index=liquid_table.index)

class O2():
    JANAF_COEFS = {'A':30.03235,'B':8.772972,'C':-3.988133,
        'D':0.788313,'E':-0.741599,'F':-11.32468,
        'G':236.1663,'H':-48.593}

    @classmethod
    def gibbs_energy(cls, T:float, logfO2:float=0) -> float:
        lnfO2 = logfO2*np.log(10)
        return cls._calc_gibbs_energy_at_1bar(T) + chem.RGAS*T*lnfO2
    
    @classmethod
    def _calc_gibbs_energy_at_1bar(cls, T:float) -> float:
        T_MAX = 2000
    
        if T>T_MAX:
            raise(TempOutOfBoundsException)
        
        return cls._janaf_G(T)
        
    @classmethod
    def _janaf_G(cls, T):
        R = chem.RGAS
        dH_scale = 1e3
        dH = (cls._janaf_dH(T, cls.JANAF_COEFS) ) * dH_scale

        S = cls._janaf_S(T, cls.JANAF_COEFS)
        G = dH - T * S
        return G

    @classmethod
    def _janaf_dH(cls, T, coefs):
        t = T / 1e3
        dH = (coefs['A'] * t + coefs['B'] / 2 * t ** 2 + coefs['C'] / 3 * t ** 3
                + coefs['D'] / 4 * t ** 4 - coefs['E'] / t) + coefs['F']
        # kJ/mol
        return dH

    # NOTE: H has been removed bc it is not relevant for some reason... reproduces Lamoreaux now
    #  or unnecessary
    @classmethod
    def _janaf_S(cls, T, coefs):
        t = T / 1e3
        S = (coefs['A'] * np.log(t) + coefs['B'] * t + coefs['C'] / 2 * t ** 2
                + coefs['D'] / 3 * t ** 3 - coefs['E'] / 2 / t ** 2) + coefs['G']
        # J/mol/K
        return S
    
class TempOutOfBoundsException(Exception):
    pass



####################
# Internal methods #
####################
