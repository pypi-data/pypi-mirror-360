"""The Model module of ThermoEngine implements a Python interface with the Phase
objective-C classes as well as the infrastructure for pure phase thermodynamic
calibration. The module contains methods that allow for loading and selection of built-in
thermodynamic databases.

"""

from thermoengine_utils import core
from thermoengine_utils.core import chem

from thermoengine import phases
from thermoengine.phases import Phase, PhaseCalculator, LegacyPhaseCalculator, PurePhaseCalculator

from typing import Type, List, Dict, Optional


import numpy as np
import pandas as pd
import re
import os
from os import path
from collections import OrderedDict
import warnings
import deprecation
import sys
import json

DATADIR = 'data/databases'

#warnings.filterwarnings('error', category=DeprecationWarning)
warnings.filterwarnings('module', category=DeprecationWarning)

__all__ = ['Database']

def _read_database_file(filename, index_col=None):
    # database = self.phase_details['database']
    # phase_details = self.phase_details

    parentpath = path.dirname(__file__)
    pathname = path.join(parentpath, DATADIR, filename)

    tableDB = pd.read_csv(pathname, index_col=index_col)
    return  tableDB, pathname
#===================================================
# def get_phase_model(id:str) -> Phase:
#     if id=='MELTS_Liquid_v1_0':
#         # from phase_library.MELTS import Liquid_v1_0
#         phs = phases.SolutionPhase(
#             'cy_Liquid_Liquid_v1_0_calib_', 'Liq', source='coder', 
#             coder_module='thermoengine.phase_library.MELTS.Liquid_v1_0')
#     else:
#         assert False, f'The phase model id {id} is not available.'
        
#     return phs

#===================================================
def get_phase_calculator(id:str, return_phase_type_flag=False) -> PhaseCalculator:
    legacy_phase = False
    pure_phase = False
    if id=='MELTS_Liquid_v1_0':
        coder_module='thermoengine.phase_library.MELTS.Liquid_v1_0'
    elif id=='MELTS_Liquid_v1_2':
        coder_module='thermoengine.phase_library.MELTS.Liquid_v1_2'
    elif id=='MELTS_Liquid_v2_0':
        coder_module='thermoengine.phase_library.MELTS.Liquid_v2_0'
    elif id=='MELTS_Olivine_HSG':
        coder_module='thermoengine.phase_library.MELTS.Olivine_HSG'
    elif id=='MELTS_Spinel_SG91':
        coder_module='thermoengine.phase_library.MELTS.Spinel_SG91'
    elif id=='MELTS_Fluid_DZ06':
        legacy_phase = True
        coder_module='thermoengine.phase_library.MELTS.Fluid_DZ06'
    elif id=='MELTS_Feldspar_EG90':
        coder_module='thermoengine.phase_library.MELTS.Feldspar_EG90'
    elif id=='MELTS_Feldspar_EG90_rhyoliteMELTS':
        coder_module='thermoengine.phase_library.MELTS.Feldspar_EG90_rhyoliteMELTS'
    elif id=='MELTS_Clinopyroxene_SG94':
        coder_module='thermoengine.phase_library.MELTS.Clinopyroxene_SG94'
    elif id=='MELTS_Orthopyroxene_SG94':
        coder_module='thermoengine.phase_library.MELTS.Orthopyroxene_SG94'
    elif id=="MELTS_Fayalite_Berman":
        pure_phase = True
        phase_name = 'Fayalite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Magnetite_Berman":
        pure_phase = True
        phase_name = 'Magnetite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Kyanite_Berman":
        pure_phase = True
        phase_name = 'Kyanite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Sillimanite_Berman":
        pure_phase = True
        phase_name = 'Sillimanite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Andalusite_Berman":
        pure_phase = True
        phase_name = 'Andalusite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Albite_Berman":
        pure_phase = True
        phase_name = 'Albite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Almandine_Berman":
        pure_phase = True
        phase_name = 'Almandine'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Anorthite_Berman":
        pure_phase = True
        phase_name = 'Anorthite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Antigorite_Berman":
        pure_phase = True
        phase_name = 'Antigorite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Coesite_Berman":
        pure_phase = True
        phase_name = 'Coesite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Corundum_Berman":
        pure_phase = True
        phase_name = 'Corundum'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Diopside_Berman":
        pure_phase = True
        phase_name = 'Diopside'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Orthoenstatite_Berman":
        pure_phase = True
        phase_name = 'Orthoenstatite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Fayalite_Berman":
        pure_phase = True
        phase_name = 'Fayalite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Ferrosilite_Berman":
        pure_phase = True
        phase_name = 'Ferrosilite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Forsterite_Berman":
        pure_phase = True
        phase_name = 'Forsterite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Water_Berman":
        pure_phase = True
        phase_name = 'Water'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Hematite_Berman":
        pure_phase = True
        phase_name = 'Hematite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Hydrogen_Gas_Berman":
        pure_phase = True
        phase_name = 'Hydrogen_Gas'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Jadeite_Berman":
        pure_phase = True
        phase_name = 'Jadeite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Potassium_Feldspar_Berman":
        pure_phase = True
        phase_name = 'Potassium_Feldspar'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Muscovite_Berman":
        pure_phase = True
        phase_name = 'Muscovite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Oxygen_Gas_Berman":
        pure_phase = True
        phase_name = 'Oxygen_Gas'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Pyrope_Berman":
        pure_phase = True
        phase_name = 'Pyrope'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Spinel_Berman":
        pure_phase = True
        phase_name = 'Spinel'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Tremolite_Berman":
        pure_phase = True
        phase_name = 'Tremolite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Quartz_Berman":
        pure_phase = True
        phase_name = 'Quartz'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_Quartz_Berman_rhyoliteMELTS":
        pure_phase = True
        phase_name = 'Quartz'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman_rhyoliteMELTS'
    elif id=="MELTS_Tridymite_Berman":
        pure_phase = True
        phase_name = 'Tridymite'
        coder_module='thermoengine.phase_library.MELTS.PurePhases_Berman'
    elif id=="MELTS_aqueous":
        pure_phase = True
        coder_module="thermoengine.phase_library.MELTS.aqueous"
        phase_name="SWIM"
    else:
        assert False, f'The phase model id {id} is not available.'
    
    if legacy_phase:
        phs_calc = LegacyPhaseCalculator(coder_module)
    elif pure_phase:
        phs_calc = PurePhaseCalculator(coder_module, phase_name)
    else:
        phs_calc = PhaseCalculator(coder_module)
    
    if return_phase_type_flag:
        return phs_calc, pure_phase
    return phs_calc

def get_phase_from_library(id:str, abbrev:str):
    phs_calc, pure_phase = get_phase_calculator(id, return_phase_type_flag=True)
    if pure_phase:
        phs = phases.PurePhase(abbrev, phs_calc)
    else:
        phs = phases.SolutionPhase(abbrev, phs_calc)
    return phs



#===================================================
def load_json_pkg_data(filename:str, dirname:str) -> dict:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    pathname = os.path.join(dir_path, dirname, filename)
    with open(pathname) as f:
        json_data = json.load(f)

    return  json_data


# dir_path = os.path.dirname(os.path.realpath(__file__))

# def __init__(self, phase_name):
#     with open(f'{self.dir_path}/output_objc/{phase_name}.json') as f:
#         phs_data = json.load(f)

class Database:
    DATABASE_DATA_DIR = 'phase_library/databases'
    def __init__(self, database_name="MELTS_v1_0"):
        filename = f"{database_name}.json"
        database_props = load_json_pkg_data(filename, self.DATABASE_DATA_DIR)

        # self._init_database
        phases = self._init_phases(database_props)

        self._phases = phases
        self._database_props = database_props


    def _init_phases(self, database_props:dict) -> dict:
        phases = {}

        database_phases = database_props['phases']
        for phase_id in database_phases:
            abbrev = database_phases[phase_id]['abbrev']
            phases[abbrev] = get_phase_from_library(phase_id, abbrev)
        
        return phases

    @property
    def phase_list(self) -> list[str]:
        phase_abbrevs =  list(self._phases.keys())
        return phase_abbrevs
    
    @property
    def phases(self) -> dict[str, Phase]:
        return self._phases

    def get_phase(self, phs_abbrev:str) -> Phase:
        assert phs_abbrev in self.phase_list, (f"That is not a valid phase abbreviation. "
                                               f"Choose something from the phase_list: {self.phase_list}")
        return self._phases[phs_abbrev]

    def get_phases(self, phs_abbrev_list:Optional[list[str]]=None):
        if phs_abbrev_list is None:
            phs_abbrev_list = self.phase_list

        phases = []
        for phs_abbrev in phs_abbrev_list:
            phases.append(self.get_phase(phs_abbrev))

        return phases








class DatabaseLegacy:
    """
    Thermodynamic database model object

    Simple access to many competing thermodynamic database models. A wide
    variety of published models are available. Models are defined using
    low-level code together with list of implemented Pure and Solution phases.

    Parameters
    ----------
    database: {'Berman', 'Stixrude', 'HollandAndPowell', 'CoderModule'}
        Chosen thermodynamic database (str ID)
    liq_mod: {'v1.0', 'v1.1', 'v1.2', 'pMELTS'}
        Chosen version of liquid model (str ID)
    calib: {True, False}
        Access calibration code or code optimized for speed (bool)
    phase_tuple: {None}
        A tuple that is set if database is 'CoderModule'. The first element is a
        string corresponding to the name of the module. The second element is a
        dictionary of abbreviations (keys) and a list of [ClassName, PhaseType]
        (values) containing phases coded by the module. The abbreviations must
        be consistent with the standard list in PurePhasdeList.csv or
        SolutionPhaseList.csv.  The ClassNames are implementation-specific.
        PhaseType is either 'pure' or 'solution'.

    Methods
    -------
    disable_gibbs_energy_reference_state
    enable_gibbs_energy_reference_state
    get_assemblage
    get_phase
    get_rxn
    redox_buffer
    redox_state

    Attributes
    ----------
    calib
    coder_module
    database
    liq_mod
    phase_info
    phase_tuple
    phases

    Examples
    --------
    Retrieve a copy of the Berman/MELTS database.

    >>> model.Database()

    Retrieve a copy of the Stixrude database.

    >>> model.Database(database='Stixrude')

    Retrieve a copy of the *Berman* database generated by the Coder module in
    ThermoEngine that contains the pure (stoichiometric) phase class
    *Potassium_Feldspar* with code generation that includes parameter
    calibration methods.

    >>> modelDB = model.Database(database="CoderModule", calib=True,
        phase_tuple=('berman', {'Or':['Potassium_Feldspar','pure']}))

    Retrieve a copy of the *Simple_Solution* database generated by the coder
    module in ThermoEngine that contains the solution phase class *Feldspar*
    with code generation that includes parameter calibration methods.

    >>> modelDB = model.Database(database="CoderModule", calib=True,
        phase_tuple=('Simple_Solution', {'Fsp':['Feldspar','solution']}))

    Notes
    -----
    The database maintains a single copy of each phase object, which is shared
    among all processes. Thus, any changes to phase models (through
    calibration, for example) automatically propagate across all uses of the
    database.

    Deprecated methods

    - phase_attributes
    - phase_details
    - phase_obj
    - phase_props

    NEEDS UPDATING

    - disable_gibbs_energy_reference_state
    - enable_gibbs_energy_reference_state

    """

    _phases: Dict[str, Type[Phase]]

    def __init__(self, database='Berman', liq_mod='v1.0', calib=True,
        phase_tuple=None):

        # Store database name at top-level for convenience
        # load active phase list

        # self._init_phase_details()
        # self._init_active_phases(liq_mod=liq_mod)
        # self._init_phase_attributes()

        # Read in allowable phases
        fixH2O = True
        global_phase_info, global_info_files = phases.get_phase_info()

        if phase_tuple and database == 'CoderModule':
            coder_module = phase_tuple[0]
            phase_dict   = phase_tuple[1]
            # self.valid_phase_symbols.extend(phase_dict.keys())
        else:
            coder_module = None
            phase_dict   = None

        self._database = database
        self._coder_module = coder_module
        self._calib = calib
        self._liq_mod = liq_mod
        self._phase_tuple = phase_tuple

        self._init_active_phase_info(global_info_files, global_phase_info, phase_dict)
        self._init_special_phases(fixH2O)
        # self._init_database()

        self._phase_info = pd.DataFrame(columns=['abbrev', 'phase_name', 'formula',
                                           'phase_type', 'endmember_num'])
        for iabbrev, iphs in self._phases.items():
            self._add_phase_info(iphs)


        pass

    def _add_phase_info(self, phase):
        phs_info = pd.DataFrame(
            [[phase.abbrev, phase.phase_name, phase.formula, phase.phase_type,phase.endmember_num]],
            columns=['abbrev', 'phase_name', 'formula', 'phase_type', 'endmember_num']
        )
        self._phase_info = pd.concat([self._phase_info, phs_info])

    def _init_special_phases(self, fixH2O):
        self._phases = OrderedDict()
        if self._database != 'CoderModule':
            self._load_special_phases('solution', fixH2O, self._liq_mod)
            self._load_special_phases('pure', fixH2O, self._liq_mod)

    def _init_active_phase_info(self, global_info_files, global_phase_info, phase_dict):
        database=self._database
        active_pure_filename, active_pure_phases = (
            self._load_validate_info('PurePhases.csv', database, 'pure',
                                     global_phase_info, global_info_files,
                                     phase_dict=phase_dict)
        )
        active_soln_filename, active_soln_phases = (
            self._load_validate_info('SolutionPhases.csv', database, 'solution',
                                     global_phase_info, global_info_files,
                                     phase_dict=phase_dict)
        )
        self.valid_phase_symbols = []
        self.valid_phase_symbols.extend(active_pure_phases.Abbrev)
        self.valid_phase_symbols.extend(active_soln_phases.Abbrev)
        self._phase_model_class_info = {}
        for indx, phase_info in active_pure_phases.iterrows():
            self._phase_model_class_info[phase_info['Abbrev']] = {
                'type': 'pure',
                'classname': phase_info['ClassName']}
        for indx, phase_info in active_soln_phases.iterrows():
            self._phase_model_class_info[phase_info['Abbrev']] = {
                'type': 'solution',
                'classname': phase_info['ClassName']}

    def _load_validate_info(self, basename, database, phase_type,
                           global_phase_info, global_info_files,
                           phase_dict=None):
        # load
        phase_info = global_phase_info[phase_type]
        if database != 'CoderModule':
            filename = database+basename
            active_phases, active_filename = _read_database_file(
                filename)
        elif phase_dict:
            data = []
            for key,value in phase_dict.items():
                if value[1] == phase_type:
                    data.append([key, value[0], None])
            active_phases = pd.DataFrame(data,
                columns=['Abbrev', 'ClassName', 'FormulaOveride'])
            active_filename = 'CoderModule'
            return active_filename, active_phases
        else:
            print ('If database is set to "CoderModule" then the second ' +
                'argument of "phase_tuple" must contain a dictionary of ' +
                'phase Abbreviations:ClassNames that are available in the ' +
                'module.')

        # validate
        abbrev_valid = active_phases['Abbrev'].isin(phase_info['Abbrev'])
        err_msg = (
            'The {phase_type} phase library defined in '
            '{filename} contains some invalid phase '
            'abbreviations, shown below: \n\n'
            '{invalid_phases}\n\n'
            'Check that the abbreviations conform to the '
            'list given in: "{phase_info_file}"')
        invalid_phases = str(active_phases[~abbrev_valid])
        phase_info_file = global_info_files[phase_type]
        assert abbrev_valid.all(), (
            err_msg.format(phase_type=phase_type,
                           filename=active_filename,
                           invalid_phases=invalid_phases,
                           phase_info_file=phase_info_file)
        )

        return active_filename, active_phases

    def _init_database(self):
        # Create and store class for each phase
        # propsDB = OrderedDict()

        for abbrev in self._phase_model_class_info:
            info = self._phase_model_class_info[abbrev]
            self._phases[abbrev] = self._init_phase_model(abbrev, info['classname'], info['type'])

    def _init_phase_model(self, abbrev, classnm, phase_type):
        try:
            phase_ptr = self._init_phase_coder(self._coder_module, classnm,
                                                abbrev, phase_type, calib=(self._calib))

        except:
            print('{classnm} is not a valid ClassName for '
                  'the {database} database.'. \
                  format(classnm=classnm, database=(self._database)))

        return phase_ptr

    def _load_special_phases(self, phase_type, fixH2O, liq_mod):
        def add_special_phase(abbrev, phase_obj):
            self._phases[abbrev] = phase_obj
            self.valid_phase_symbols.append(abbrev)

        if fixH2O and (phase_type=='pure'):
            H2O_classnm = 'GenericH2O'

            H2O_phase_obj = self._init_phase_coder(
                H2O_classnm, 'H2O', phase_type, calib=False)

            add_special_phase('H2O', H2O_phase_obj)

        if (liq_mod is not None) and (phase_type=='solution'):
            if liq_mod=='v1.0':
                liq_classnm = 'LiquidMelts'
            elif liq_mod=='v1.1':
                liq_classnm = 'LiquidMeltsPlusOldH2OandNewCO2'
            elif liq_mod=='v1.2':
                liq_classnm = 'LiquidMeltsPlusCO2'
            elif liq_mod=='pMELTS':
                liq_classnm = 'LiquidpMelts'
            else:
                assert False, (
                    'Chosen liq_mod is not valid'
                )

            liq_phase_obj = self._init_phase_coder(
                liq_classnm, 'Liq', phase_type, calib=True)

            add_special_phase('Liq', liq_phase_obj)


        if (phase_type=='solution'):
            alloy_solid_classnm = 'AlloySolid'
            alloy_liquid_classnm = 'AlloyLiquid'

            MtlS_phase_obj = self._init_phase_coder(
                alloy_solid_classnm, 'MtlS', phase_type, calib=False)
            MtlL_phase_obj = self._init_phase_coder(
                alloy_liquid_classnm, 'MtlL', phase_type, calib=False)

            add_special_phase('MtlS', MtlS_phase_obj)
            add_special_phase('MtlL', MtlL_phase_obj)

    #########################################################

    def _init_phase_coder(self, coder_module, classnm, abbrev, phase_type,
        calib=False):
        ptr_name = 'cy_' + classnm + '_' + coder_module.split('.')[-1] + '_' + (
            'calib_' if calib else '')

        if phase_type=='pure':
            if calib is None:
                phase_ptr = phases.PurePhase(ptr_name, abbrev, source='coder',
                    coder_module=coder_module)
            else:
                phase_ptr = phases.PurePhase(ptr_name, abbrev, calib=calib,
                    source='coder', coder_module=coder_module)
        elif phase_type=='solution':
            if calib is None:
                phase_ptr = phases.SolutionPhase(ptr_name, abbrev,
                    source='coder', coder_module=coder_module)
            else:
                phase_ptr = phases.SolutionPhase(ptr_name, abbrev, calib=calib,
                    source='coder', coder_module=coder_module)

        return phase_ptr

    @property
    def liq_mod(self):
        """
        Name of current liquid model

        Refers to version of MELTS.
        """
        return self._liq_mod

    @property
    def database(self):
        """
        Name of current database
        """
        return self._database

    @property
    def phases(self) -> Dict[str, Type[phases.Phase]]:
        """
        Dictionary of phase objects

        Phase objects stored under official abbreviation. See phase_info for
        information on each phase.
        """
        return self._phases

    @property
    def phase_info(self):
        """
        Phase info table for all members of current database

        Basic phase information stored in pandas dataframe with columns:
            'abbrev' - Official phase abbreviation

            'phase_name' - Full phase name

            'formula' -  Chemical formula (or generic formula for solution phases)

            'phase_type' - Solution or pure

            'endmember_num' - Number of endmembers (1 for pure phases)

        """
        return self._phase_info

    @property
    def calib(self):
        """
        The code base for this phase implements model calibration functions.

        Returns
        -------
        bool
        """
        return self._calib

    @property
    def coder_module(self):
        """
        Module name of Coder-generated database

        Returns
        -------
        str

        Name of Coder module
        """
        return self._coder_module

    @property
    def phase_tuple(self):
        """
        Dictionary of phases in a Coder-generated database

        Returns
        -------
        tuple of strs

        (1) str of coder_module

        (2) dict of phases coded in the coder_module. *key* is abbreviation.
            *value* is a two-component list of phase_name and phase_type;
            *phase_type* is either 'pure' or 'solution'.
        """
        return self._phase_tuple

    @property
    @deprecation.deprecated(
        deprecated_in="1.0", removed_in="2.0",
        details="Use phase_info instead.")
    def phase_details(self):
        # deprecated_in="1.0", removed_in="2.0",
        # current_version=__version__,
        # warnings.warn(
        #     "phase_details is deprecated, use phase_info instead.",
        #     DeprecationWarning)
        pass

    @property
    @deprecation.deprecated(
        deprecated_in="1.0", removed_in="2.0",
        details=(
            "For basic phase properties, use phase_info instead.\n"
            "For detailed phase properties, retrieve them directly "
            "from the desired phase object stored in phases." ))
    def phase_attributes(self):
        # warnings.warn((
        #     "'phase_attributes' is deprecated.\n"
        #     "For basic phase properties, use 'phase_info' instead.\n"
        #     "For detailed phase properties, retrieve them directly "
        #     "from the desired phase object stored in 'phases'."),
        #     DeprecationWarning)
        pass


    @property
    @deprecation.deprecated(
        deprecated_in="1.0", removed_in="2.0",
        details=(
            "Direct access to the non-Python phase calculation object is "
            "not recommended. Instead, use the Python interface provided by "
            "the desired phase stored in phases."))
    def phase_obj(self):
        # warnings.warn((
        #     "'phase_obj' is deprecated.\n"
        #     "Direct access to the non-python phase calculation object is "
        #     "not recommended. Instead, use the python interface provided by "
        #     "the desired phase stored in 'phases'."),
        #     DeprecationWarning)
        pass

    @property
    @deprecation.deprecated(
        deprecated_in="1.0", removed_in="2.0",
        details=(
            "Instead retrieve properties directly "
            "from the desired phase object stored in phases."))
    def phase_props(self):
        # warnings.warn((
        #     "'phase_props' is deprecated.\n"
        #     "Instead retrieve properties directly "
        #     "from the desired phase object stored in 'phases'."),
        #     DeprecationWarning)
        pass

    ##################

    def enable_gibbs_energy_reference_state(self):
        """
        Enable Helgeson convention of Gibbs energy.

        Use Helgeson (SUPCRT) convention of Gibbs free energy
        of formation rather than enthalpy of formation at Tr, Pr.
        """
        # call method on any phase class (automatically applied to all)
        # next(iter(self.phases.values()))
        for phase in self.phases.values():
            phase.enable_gibbs_energy_reference_state()


    def disable_gibbs_energy_reference_state(self):
        """
        Disable Helgeson convention of Gibbs energy.

        Use standard enthalpy of formation at Tr, Pr as reference, rather
        than Helgeson (SUPCRT) convention of Gibbs free energy of formation.
        """
        # call method on any phase class (automatically applied to all)
        # next(iter(self.phases.values()))
        for phase in self.phases.values():
            phase.disable_gibbs_energy_reference_state()

    def get_phase_obj(self, phasesym_l):
        """
        Get a phase that is coded in Objective-C by symbol.

        Parameters
        ----------
        phasesym_l : []
            A list of abbreviations of desired phases.

        Returns
        -------
        phase_obj_l
            List of phase objects corresponding to desired phases.
        """

        phase_details = self.phase_details
        phase_obj_l = []
        for phasesym in phasesym_l:
            try:
                # phase_obj_l.append(phase_details['purephase_obj_d'][phasesym])
                phase_obj_l.append(phase_details['pure_props'][phasesym]['obj'])
            except:
                assert False, '"'+phasesym+'" is not a valid phase abbreviation. Try again.'

        return phase_obj_l

    def get_all_phases(self) -> List[Type[Phase]]:
        all_phases = self.valid_phase_symbols
        if self._database is not 'Berman':
            filtered_phases = [phs for phs in all_phases
                          if phs not in ['Liq', 'MtlS', 'MtlL','H2O']]
            all_phases = filtered_phases
        return self.get_phases(all_phases)

    def get_phase(self, phase_symbol:str) -> Type[Phase]:
        """
        Get phase from current database by symbol.

        Parameters
        ----------
        phase_symbol : str
            Abbreviation of desired phase. Must use correct ThermoEngine format.

        Returns
        -------
        phase : obj
            Phase object corresponding to desired phase.

        Notes
        -----
        The phase object retrieved by this method remains tied to the Database
        (i.e., it points to a single copy stored in the Database).
        Any changes made to this phase (e.g., through calibration) thus
        propagate to the entire Database.


        Examples
        --------
        phase = modelDB.get_phase('Aeg')

        sym_list = ['Aeg', 'Ky', 'Sil', 'Qtz']
        phase_list = [modelDB.get_phase(sym) for sym in sym_list]

        """

        # warn_val =  warnings.warn(
        #     "phase_details is deprecated, use phase_info instead.",
        #     DeprecationWarning)

        self._validate_phase_symbol(phase_symbol)
        if phase_symbol not in self.phases:
            info = self._phase_model_class_info[phase_symbol]
            phs = self._init_phase_model(phase_symbol, info['classname'], info['type'])
            self._phases[phase_symbol] = phs
            self._add_phase_info(phs)


        return self.phases[phase_symbol]

    def get_phases(self, phase_symbols:List[str]) -> List[Type[Phase]]:
        return [self.get_phase(sym) for sym in phase_symbols]

    def _validate_phase_symbol(self, phase_symbol):
        if phase_symbol not in self.valid_phase_symbols:
            err_msg = (
                '"{phase_symbol}" is not a valid '
                'phase symbol for this database. '
                'Select from the following available '
                'phase symbol keys: {allowedsyms}'
            )
            phase_list = self.valid_phase_symbols
            if self.phase_tuple is not None:
                phase_list.append((self.phase_tuple[1]).keys())

            raise self.InvalidPhaseSymbol(
                err_msg.format(
                    phase_symbol=phase_symbol,
                    allowedsyms=phase_list)
            )

    class InvalidPhaseSymbol(Exception):
        pass

    def warn_test(self):
        """
        This method is called when some function is deprecated.
        """
        warnings.filterwarnings('error', category=DeprecationWarning)
        print('hello')
        warnings.warn("Big old warning test", DeprecationWarning)
        print(sys.stderr)
        print('world')

    def get_assemblage(self, phase_symbols):
        """
        Get phase assemblage from current database by symbol.

        An assemblage represents a set of coexisting phases.

        Parameters
        ----------
        phase_symbols : list of strings
            List of abbreviations of coexisting phases.
            Must use correct ThermoEngine format.

        Returns
        -------
        assemblage : obj
            Assemblage object corresponding to coexisting phases.

        Examples
        --------
        sym_list = ['Ky', 'Sil', 'Qtz']
        assemblage = modelDB.get_assemblage(sym_list)

        """
        phase_objs = []
        for phase_symbol in phase_symbols:
            phase_obj = self.get_phase(phase_symbol)
            phase_objs.append(phase_obj)

        assemblage = phases.Assemblage(phase_objs, obj_is_classnm=False)
        return assemblage

    def get_rxn(self, phase_symbols, endmember_ids, rxn_coefs,
                coefs_per_atom=False):
        """
        Get an endmember reaction from current database.

        A reaction is represented as a stoichiometrically balanced
        exchange of atoms between a set of endmember (or pure) phases.

        Parameters
        ----------
        phase_symbols : list of strings
            List of abbreviations of reacting phases
        endmember_ids : list of ints
            List of integers representing endmember ID number for each phase
        rxn_coefs : array
            Array of reaction coefficients. Positive values are products;
            negative values are reactants. Coefficients should be
            stoichiometrically balanced.
        coefs_per_atom : bool, default False
            If False, rxn coefficients are defined per formula unit of each
            endmember.

            If True, coefficients are given on per atom basis. Thus they are
            independent of the formula unit definition.

            This is useful to avoid mistakes for phases with multiple standard
            formula definitions (e.g., En is often given as MgSiO3 OR Mg2Si2O6).

        Returns
        -------
        rxn : obj
            rxn object for reacting endmember phases

        Examples
        --------
        phase_symbols = ['Per', 'Qz', 'Cpx']

        endmember_ids = [0, 0, 1]

        rxn_coefs = [2, 2, 1]

        rxn = modelDB.get_rxn(phase_symbols, endmember_ids, rxn_coefs)

        # rxn_coefs defined per atom basis

        rxn_coefs = [2, 3, 5]

        rxn = modelDB.get_rxn(phase_symbols, endmember_ids, rxn_coefs,
        coefs_per_atom=True)
        """

        assert (
            (len(endmember_ids) == len(phase_symbols)) and (len(phase_symbols) == len(rxn_coefs))), 'phase_symbols, endmember_ids, and rxn_coefs must all be equal'

        phase_objs = []
        for phase_symbol in phase_symbols:
            phase_objs.append(self.get_phase(phase_symbol))

        # from IPython import embed;embed();import ipdb;ipdb.set_trace()
        rxn = phases.Rxn(phase_objs, endmember_ids, rxn_coefs,
                         coefs_per_atom=coefs_per_atom)
        return rxn

    def _redox_state_Kress91(self, T, P, oxide_comp, logfO2=None):
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


        OXIDES = chem.OXIDE_ORDER
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


    def redox_state(self, T, P, oxide_comp=None, logfO2=None,
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

                output = self._redox_state_Kress91(
                    T, P, liq_oxide_comp, logfO2=logfO2)

                if logfO2 is None:
                    logfO2 = output
                else:
                    ln_Fe_oxide_ratio =  output
                    Fe_oxide_ratio = np.exp(ln_Fe_oxide_ratio)
                    ind_FeO = np.where(chem.OXIDE_ORDER=='FeO')[0][0]
                    ind_Fe2O3 = np.where(chem.OXIDE_ORDER=='Fe2O3')[0][0]

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


    def _O2_chem_potential(self, T, P):
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

    def _consistent_redox_buffer_QFM(self, T, P):
        mu_O2 = self._O2_chem_potential(T, P)

        mu_Qz = self.get_phase('Qz').chem_potential(T, P)
        mu_Fa = self.get_phase('Fa').chem_potential(T, P)
        mu_Mag = self.get_phase('Mag').chem_potential(T, P)

        dGr0 = 2*mu_Mag + 3*mu_Qz - 3*mu_Fa - mu_O2
        logfO2 = 1/(2.303*8.314*T)*dGr0
        return logfO2

    def _consistent_redox_buffer_HM(self, T, P):
        mu_O2 = self._O2_chem_potential(T, P)

        mu_Hem = self.get_phase('Hem').chem_potential(T, P)
        mu_Mag = self.get_phase('Mag').chem_potential(T, P)

        dGr0 = 6*mu_Hem - 4*mu_Mag - mu_O2
        logfO2 = 1/(2.303*8.314*T)*dGr0
        return logfO2

    def _empirical_redox_buffer(self, T, P, A=0, B=0, C=0, D=0,
                                ignore_lims=True, Tlims=None):

        logfO2 = A/T + B + C*(P-1)/T + D*np.log(T)

        if (not ignore_lims) and (Tlims is not None):
            logfO2[T<Tlims[0]] = np.nan
            logfO2[T>=Tlims[1]] = np.nan

        return logfO2

    @classmethod
    def parse_rxn(cls, rxn_eqn_str, rxn_result_str=None, sort=True ):
        rxn_phs_str, rxn_eqn_str = cls._get_reaction_phase_str( rxn_eqn_str, sort=sort, full_output=True)
        reac_l, prod_l = cls._get_reaction_phases( rxn_phs_str )

        if rxn_result_str is not None:
            rxn_dir = cls._get_rxn_dir(rxn_phs_str, rxn_result_str)
        else:
            rxn_dir = None

        rxn_d = {}
        rxn_d['rxn_eqn'] = rxn_eqn_str
        rxn_d['rxn_phs_str'] = rxn_phs_str
        rxn_d['reac_l'] = reac_l
        rxn_d['prod_l'] = prod_l
        rxn_d['rxn_dir'] = rxn_dir

        return rxn_d

    @classmethod
    def _parse_rxn_result(cls, result_str):
        # Remove surrounding whitespace
        result_str = result_str.strip()
        if result_str == 'NC':
            phs_l = None
            obs_l = result_str
            return phs_l, obs_l

        parse_result = re.compile(r'\w+\s*[+-?]+\s*')
        phs_result_l = parse_result.findall(result_str)
        phs_a = []
        obs_a = []
        for iphs_result in phs_result_l:
            ires = iphs_result.strip().split()
            phs_a.append(ires[0])
            obs_a.append(ires[1])

        phs_a = np.array(phs_a)
        obs_a = np.array(obs_a)

        return phs_a, obs_a

    @classmethod
    def _get_rxn_dir(cls, rxn_phs_str, result):
        # Determine Reaction Direction: ['FWD','REV','NC','FWD?','REV?','INV']
        # print('rxn_phs_str = ',rxn_phs_str)
        # print('results = ',result)
        # print('===========')

        reac_l, prod_l = cls._get_reaction_phases(rxn_phs_str)
        phs_a, obs_a = cls._parse_rxn_result(result)

        if phs_a is None:
            rxn_dir = 'NC'
            return rxn_dir

        fwd_cnt = 0
        fwd_maybe_cnt = 0
        rev_cnt = 0
        rev_maybe_cnt = 0

        for reac in reac_l:
            if reac not in phs_a:
                continue
            obs = obs_a[phs_a==reac]
            if obs == '-':
                fwd_cnt += 1
            elif obs == '-?':
                fwd_maybe_cnt +=1
            elif obs == '+':
                rev_cnt += 1
            elif obs == '+?':
                rev_maybe_cnt += 1
            elif obs == '?':
                # Do nothing
                pass
            else:
                # print('*****************')
                # print('reac = ',reac)
                # print('prod = ',prod)
                # print('obs = ', obs)
                # print('prod_l = ',prod_l)
                # print('reac_l = ',reac_l)
                # print('phs_a = ',phs_a)
                # print('obs_a = ',obs_a)
                # print('*****************')
                assert False, obs + ' is not a supported Results code.'

        for prod in prod_l:
            if prod not in phs_a:
                continue
            obs = obs_a[phs_a==prod]
            if obs == '+':
                fwd_cnt += 1
            elif obs == '+?':
                fwd_maybe_cnt +=1
            elif obs == '-':
                rev_cnt += 1
            elif obs == '-?':
                rev_maybe_cnt += 1
            elif obs == '?':
                # Do nothing
                pass
            else:
                # print('*****************')
                # print('reac = ',reac)
                # print('prod = ',prod)
                # print('obs = ', obs)
                # print('prod_l = ',prod_l)
                # print('reac_l = ',reac_l)
                # print('phs_a = ',phs_a)
                # print('obs_a = ',obs_a)
                # print('*****************')
                assert False, obs + ' is not a supported Results code.'

        # Reaction Direction Options: ['FWD','REV','NC','FWD?','REV?','INV']
        if (fwd_cnt==0)&(fwd_maybe_cnt==0)&(rev_cnt==0)&(rev_maybe_cnt==0):
            rxn_dir = 'INV'
        if fwd_maybe_cnt > 0:
            rxn_dir = 'FWD?'
        if rev_maybe_cnt > 0:
            rxn_dir = 'REV?'
        if (fwd_maybe_cnt > 0) & (rev_maybe_cnt > 0):
            rxn_dir = 'NC'
        if fwd_cnt > 0:
            rxn_dir = 'FWD'
        if rev_cnt > 0:
            rxn_dir = 'REV'
        if (fwd_cnt > 0) & (rev_cnt > 0):
            rxn_dir = 'INV'

        return rxn_dir

    @classmethod
    def _get_reaction_phases(cls, rxn_phs_str):
        reac_str, prod_str = str.split(rxn_phs_str,':')
        reac_l = reac_str.split(',')
        prod_l = prod_str.split(',')
        return reac_l, prod_l

    @classmethod
    def _split_phases(cls, phs_combo_str):
        return [re.sub('^[0-9]','',phs.strip()) \
                for phs in phs_combo_str.split('+')]

    @classmethod
    def _get_reaction_phase_str(cls, rxn_eqn_str, sort=True, full_output=False ):
        reac_str, prod_str = str.split(rxn_eqn_str,'=')
        reac_str = str.strip(reac_str)
        prod_str = str.strip(prod_str)

        reac_l = cls._split_phases(reac_str)
        prod_l = cls._split_phases(prod_str)

        if sort:
            reac_l.sort()
            prod_l.sort()

            first_phs = [reac_l[0],prod_l[0]]
            first_phs.sort()
            if first_phs[0] == prod_l[0]:
                reac_l, prod_l = prod_l, reac_l
                rxn_eqn_str = prod_str + ' = ' + reac_str

        rxn_phs_str = ''
        for phs in reac_l[:-1]:
            rxn_phs_str += phs+','

        rxn_phs_str += reac_l[-1]
        rxn_phs_str += ':'
        for phs in prod_l[:-1]:
            rxn_phs_str += phs+','

        rxn_phs_str += prod_l[-1]

        if full_output:
            return rxn_phs_str, rxn_eqn_str
        else:
            return rxn_phs_str
#===================================================
class SysComp:
    '''
    Lightweight composition object

    Parameters
    ----------
    comp : array or dataframe of compositions (1D or 2D)
        Array or table defining compositions. If labeled datafame is provided,
        then column headers are used as components by default. Otherwise,
        the components must be defined in the optional components parameter.
    H2O : {'input','none',value(s)}, optional
        Optional override for H2O content.
            'input' - (default) comp table value used if present
            'none' - H2O is ignored as a component
            value(s) - H2O value is overriden using float or float array
    CO2 : {'input','none',value(s)}, optional
        Optional override for CO2 content.
            'input' - comp table value used if present
            'none' - (default) CO2 is ignored as a component
            value(s) - CO2 value is overriden using float or float array
    units : {'wt','mol'}, optional
        Define input units for comp array
    basis : {'formula', 'atomic'}, optional
        Define input basis for molar comp
    components : {'oxides', 'major_oxides', implicit column headers,
                  explicit str array}, optional
        Define names of input component endmembers. Standard oxides are assumed
        by default unless the comp table include headers.
            'oxides' - standard petrology oxide order (see SysComp.STD_OXIDES)
            'major_oxides' - Major geological oxides (see SysComp.MAJOR_OXIDES)
            implicit col headers - comp data table includes column headers,
                they will be used
            explicit str array - Defines order for complete set of components.
                If comp data array lacks column headers, they are provided here.
                Otherwise, this defines the full set of components, while comp
                array may include only subset.
    stoic : dicts, optional
        Nested dicts defining the elemental stoichiometry of each endmember.
        Optional input requirerd only for custom components. Input unneeded
        for standard oxides.

        Example input ...
        stoic = {'MgSiO3': {'Mg':1, 'Si':1, 'O':3},
                 'Mg2SiO4': {'Mg':2, 'Si':1, 'O':4},
                 'Fe2SiO4': {'Fe':2, 'Si':1, 'O':4},}

    More Info
    ---------

    '''

    DEFAULT_COMPONENTS='oxides'
    DBL_MAX = 999999.0
    STD_OXIDES = np.array([
        'SiO2','TiO2','Al2O3','Fe2O3','Cr2O3','FeO','MnO','MgO',
        'NiO','CoO','CaO','Na2O','K2O','P2O5','H2O','CO2'])
    MAJOR_OXIDES = np.array([
        'SiO2','Al2O3','FeO','MgO','CaO','Na2O','K2O','H2O'])

    IONIC_COMPOUNDS_STOIC = {
        'SiO2':{'Si':1, 'O':2},
        'TiO2':{'Ti':1, 'O':2},
        'Al2O3':{'Al':2, 'O':3},
        'Fe2O3':{'Fe':2, 'O':3},
        'Cr2O3':{'Cr':2, 'O':3},
        'FeO':{'Fe':1, 'O':1},
        'FeO*':{'Fe':1, 'O':1},
        'MnO':{'Mn':1, 'O':1},
        'MgO':{'Mg':1, 'O':1},
        'NiO':{'Ni':1, 'O':1},
        'CoO':{'Co':1, 'O':1},
        'CaO':{'Ca':1, 'O':1},
        'Na2O':{'Na':2, 'O':1},
        'K2O':{'K':2, 'O':1},
        'P2O5':{'P':2, 'O':5},
        'H2O':{'H':2, 'O':1},
        'CO2':{'C':1, 'O':2},
        'As2O3':{'As':2,'O':3},
        'Au2O':{'Au':2,'O':1},
        'B2O3':{'B':2,'O':3},
        'BaO':{'Ba':1,'O':1},
        'BeO':{'Be':1,'O':1},
        'CeO2':{'Ce':1,'O':2 },
        'Ce2O3':{'Ce':2,'O':3},
        'Cs2O':{'Cs':2,'O':1},
        'CuO':{'Cu':1,'O':1},
        'Dy2O3':{'Dy':2,'O':3},
        'Er2O3':{'Er':2,'O':3},
        'EuO':{'Eu':1,'O':1},
        'Eu2O3':{'Eu':2,'O':3},
        'Ga2O3':{'Ga':2,'O':3},
        'Gd2O3':{'Gd':2,'O':3},
        'GeO2':{'Ge':1,'O':2},
        'HfO2':{'Hf':1,'O':2},
        'Ho2O3':{'Ho':2,'O':3},
        'La2O3':{'La':2,'O':3},
        'Li2O':{'Li':2,'O':1},
        'Lu2O3':{'Lu':2,'O':3},
        'MnO2':{'Mn':1,'O':2},
        'Mn3O4':{'Mn':3,'O':4},
        'MoO3':{'Mo':1,'O':3},
        'Nb2O5':{'Nb':2,'O':5},
        'Nd2O3':{'Nd':2,'O':3},
        'PbO':{'Pb':1,'O':1},
        'Pr2O3':{'Pr':2,'O':3},
        'Rb2O':{'Rb':2,'O':1},
        'SO3':{'S':1,'O':3},
        'Sb2O3':{'Sb':2,'O':3},
        'Sc2O3':{'Sc':2,'O':3},
        'Sm2O3':{'Sm':2,'O':3},
        'SnO2':{'Sn':1,'O':2},
        'SrO':{'Sr':1,'O':1},
        'Ta2O5':{'Ta':2,'O':5},
        'Tb2O3':{'Tb':2,'O':3},
        'ThO2':{'Th':1,'O':2},
        'Ti2O3':{'Ti':2,'O':3},
        'Tm2O3':{'Tm':2,'O':3},
        'UO2':{'U':1,'O':2},
        'U3O8':{'U':3,'O':8},
        'V2O5':{'V':2,'O':5},
        'WO3':{'W':1,'O':3},
        'Y2O3':{'Y':2,'O':3},
        'Yb2O3':{'Yb':2,'O':3},
        'ZnO':{'Zn':1,'O':1},
        'ZrO2':{'Zr':1,'O':2},
    }

    OXIDES_STOIC = {
        'SiO2':{'Si':1, 'O':2},
        'TiO2':{'Ti':1, 'O':2},
        'Al2O3':{'Al':2, 'O':3},
        'Fe2O3':{'Fe':2, 'O':3},
        'Cr2O3':{'Cr':2, 'O':3},
        'FeO':{'Fe':1, 'O':1},
        'FeO*':{'Fe':1, 'O':1},
        'MnO':{'Mn':1, 'O':1},
        'MgO':{'Mg':1, 'O':1},
        'NiO':{'Ni':1, 'O':1},
        'CoO':{'Co':1, 'O':1},
        'CaO':{'Ca':1, 'O':1},
        'Na2O':{'Na':2, 'O':1},
        'K2O':{'K':2, 'O':1},
        'P2O5':{'P':2, 'O':5},
        'H2O':{'H':2, 'O':1},
        'CO2':{'C':1, 'O':2},
    }
    PERIODIC_ORDER = np.array([
        None, 'H', 'He', 'Li', 'Be',  'B', 'C', 'N', 'O', 'F', 'Ne', 'Na',
        'Mg', 'Al', 'Si', 'P', 'S',   'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V',
        'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se',
        'Br', 'Kr', 'Rb', 'Sr', 'Y',  'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh',
        'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La',
        'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm',
        'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl',
        'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U',
        'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr',
        'Rf', 'Db', 'Sg' ])
    PERIODIC_NAMES = np.array([
        None, 'hydrogen', 'helium', 'lithium',  'beryllium', 'boron',
        'carbon', 'nitrogen', 'oxygen', 'fluorine', 'neon', 'sodium',
        'magnesium', 'aluminum', 'silicon', 'phosphorous', 'sulfur',
        'chlorine', 'argon', 'potassium', 'calcium', 'scandium', 'titanium',
        'vanadium', 'chromium', 'manganese', 'iron', 'cobalt', 'nickel',
        'copper', 'zinc', 'gallium', 'germanium', 'arsenic', 'selenium',
        'bromine', 'krypton', 'rubidium', 'strontium', 'yttrium', 'zirconium',
        'niobium', 'molybdenum', 'technetium', 'ruthenium', 'rhodium',
        'palladium', 'silver', 'cadmium', 'indium', 'tin', 'antimony',
        'tellurium', 'iodine', 'xenon', 'cesium', 'barium', 'lantahnum',
        'cerium', 'praseodymium', 'neodymium', 'promethium', 'samarium',
        'europium', 'gadolinium', 'terbium', 'dysprosium', 'holmium', 'erbium',
        'thulium', 'ytterbium', 'lutetium', 'hafnium', 'tantalum', 'tungsten',
        'rhenium', 'osmium', 'iridium', 'platinum', 'gold', 'mercury',
        'thallium', 'lead', 'bismuth', 'polonium', 'astatine', 'radon',
        'francium', 'radium', 'actinium', 'thorium', 'protactinium', 'uranium',
        'neptunium', 'plutonium', 'americium', 'curium', 'berkelium',
        'californium', 'einsteinium', 'fermium', 'mendelevium', 'nobelium',
        'lawrencium', 'ruferfordium', 'dubnium', 'seaborgium' ])
    PERIODIC_WEIGHTS = np.array([
        0.0, 1.0079, 4.00260, 6.94, 9.01218, 10.81, 12.011, 14.0067, 15.9994,
        18.998403, 20.179, 22.98977, 24.305, 26.98154, 28.0855, 30.97376, 32.06,
        35.453, 39.948, 39.102, 40.08, 44.9559, 47.90, 50.9415, 51.996, 54.9380,
        55.847, 58.9332, 58.71, 63.546, 65.38, 69.735, 72.59, 74.9216, 78.96,
        79.904, 83.80, 85.4678, 87.62, 88.9059, 91.22, 92.9064, 95.94, 98.9062,
        101.07, 102.9055, 106.4, 107.868, 112.41, 114.82, 118.69, 121.75,
        127.60, 126.9045, 131.30, 132.9054, 137.33, 138.9055, 140.12, 140.9077,
        144.24, 145., 150.4, 151.96, 157.25, 158.9254, 162.50, 164.9304, 167.26,
        168.9342, 173.04, 174.967, 178.49, 180.9479, 183.85, 186.207, 190.2,
        192.22, 195.09, 196.9665, 200.59, 204.37, 207.2, 208.9804, 209., 210.,
        222., 223., 226.0254, 227., 232.0381, 231.0359, 238.029, 237.0482, 244.,
        243., 247., 247., 251., 254., 257., 258., 259., 260., 260., 260., 263.])
    # These entropy values are from Robie, Hemingway and Fisher (1979) USGS
    # Bull 1452 as stipulated by Berman (1988).  They are NOT the most recent
    # values (e.g.NIST)
    PERIODIC_ENTROPES = ([
        0.0, 130.68/2.0, 126.15, 29.12, 9.54, 5.90, 5.74, 191.61/2.0,
        205.15/2.0, 202.79/2.0, 146.32, 51.30, 32.68, 28.35, 18.81, 22.85,
        31.80, 223.08/2.0, 154.84, 64.68, 41.63, 34.64, 30.63, 28.91, 23.64,
        32.01, 27.28, 30.04, 29.87, 33.15, 41.63, 40.83, 31.09, 35.69, 42.27,
        245.46/2.0, 164.08, 76.78, 55.40, 44.43, 38.99, 36.40, 28.66, DBL_MAX,
        28.53, 31.54, 37.82, 42.55, 51.80, 57.84, 51.20, 45.52, 49.50,
        116.15/2.0, 169.68, 85.23, 62.42, 56.90, 69.46, 73.93, 71.09,
        DBL_MAX, 69.50, 80.79, 68.45, 73.30, 74.89, 75.02, 73.18, 74.01,
        59.83, 50.96, 43.56, 41.51, 32.64, 36.53, 32.64, 35.48, 41.63, 47.49,
        75.90, 64.18, 65.06, 56.74, DBL_MAX, DBL_MAX, 176.23, DBL_MAX, DBL_MAX,
        DBL_MAX, 53.39, DBL_MAX, 50.29, DBL_MAX, 51.46, DBL_MAX, DBL_MAX,
        DBL_MAX, DBL_MAX, DBL_MAX, DBL_MAX, DBL_MAX, DBL_MAX, DBL_MAX, DBL_MAX,
        DBL_MAX, DBL_MAX ])

    def __init__(self, comp, H2O='input', CO2='none',
                 units='wt', basis='formula',
                 components=None, stoic=None):

        endmembers = self._validate_components(comp, components)
        comp = self._format_comp(comp, endmembers)

        comp = self._override_endmember_component(H2O, 'H2O', comp)
        comp = self._override_endmember_component(CO2, 'CO2', comp)
        endmembers = comp.columns.values
        self._endmembers = endmembers

        endmem_stoic = self._init_endmem_stoic(endmembers, stoic)

        self._init_component_elems(endmembers, endmem_stoic)
        self._convert_comp(comp, units, basis)

    def _override_endmember_component(self, override_option, component, comp):
        if override_option=='none':
            if component in comp:
                # comp.drop(component, axis='columns', inplace=True)
                # Remove SettingWithCopyWarning
                comp = comp.drop(component, axis='columns')
        else:
            try:
                values = np.array(override_option, dtype='float')
                comp[component] = values
            except:
                assert override_option=='input', (
                    component + " value is invalid. "
                    "Select from valid options {'input','none',value(s)}"
                    )

        return comp

    def _validate_components(self, comp, components):
        try:
            columns = comp.columns
        except:
            columns = None

        if components is None:
            if columns is None:
                components = self.DEFAULT_COMPONENTS
            else:
                components = columns

        if np.array(components).size>1:
            endmembers = components
        elif components=='oxides':
            endmembers = self.STD_OXIDES
        elif components=='major_oxides':
            endmembers = self.MAJOR_OXIDES
        else:
            assert False, ('components must be a array-like list '
                           'of component names')

        return endmembers

    def _format_comp(self, comp, endmembers):
        try:
            columns = comp.columns
            isendmem = [col in endmembers for col in columns]
            assert np.all(isendmem), (
                'Every column of the comp data table must be a valid endmember.'
            )

            for endmem in endmembers:
                if endmem not in columns:
                    comp[endmem]=0

            comp = comp[endmembers]

        except:
            comp = np.array(comp)
            endmembers = np.array(endmembers)

            if comp.ndim==1:
                comp = comp[np.newaxis,:]

            assert comp.shape[1]==len(endmembers),(
                'For array input composition, number of columns in array '
                'must equal number of component endmembers.'
            )
            comp = pd.DataFrame(comp, columns=endmembers)

        return comp

    def _init_endmem_stoic(self, endmembers, stoic):
        if stoic is None:
            stoic = {}

        stoic_library = {**stoic, **self.IONIC_COMPOUNDS_STOIC}
        stoic = {key:stoic_library[key] for key in endmembers}
        endmem_stoic0 = pd.DataFrame(stoic).fillna(0).T
        elems0 = np.array(list(endmem_stoic0.columns))
        elems = np.array([elem for elem in self.PERIODIC_ORDER
                          if elem in elems0])
        endmem_stoic = endmem_stoic0[elems]

        self._elems = elems
        self._endmember_stoic = endmem_stoic
        return endmem_stoic


    def _init_component_elems(self, endmembers, endmem_stoic):
        elems = endmem_stoic.columns

        atomic_nums = 1+np.arange(len(self.PERIODIC_ORDER[1:]))
        periodic_wts = dict(
            zip(self.PERIODIC_ORDER[1:],
                self.PERIODIC_WEIGHTS[1:]))
        periodic_names = dict(
            zip(self.PERIODIC_ORDER[1:],
                self.PERIODIC_NAMES[1:]))
        periodic_nums = dict(
            zip(self.PERIODIC_ORDER[1:],
                atomic_nums))

        elem_wts = pd.Series({key:periodic_wts[key] for key in elems})
        elem_names = pd.Series({key:periodic_names[key] for key in elems})
        elem_nums = pd.Series({key:periodic_nums[key] for key in elems})

        endmem_wts = endmem_stoic.dot(elem_wts)

        self._endmember_natom = endmem_stoic.sum(axis=1)
        self._endmember_wts = endmem_wts
        self._elem_wts = elem_wts
        self._elem_names = elem_names
        self._elem_nums = elem_nums

    def _convert_comp(self, comp, units, basis):

        if units=='wt':
            wt_comp = comp
            mol_comp = wt_comp/self.endmember_wts

        elif units=='mol':
            mol_comp = comp
            wt_comp = mol_comp*self.endmember_wts

        else:
            assert False, "units are not valid, must select from {'wt','mol'}"

        elem_comp = mol_comp.dot(self._endmember_stoic)

        self._elem_comp = elem_comp
        self._mol_comp = mol_comp
        self._wt_comp = wt_comp

    def mol_comp(self, components='oxides', basis='formula', normalize=False):
        '''
        Molar composition

        Parameters
        ----------
        components : {'oxides','endmems','elems'}, optional
            Define components for expression of composition
        basis : {'formula', 'atomic'}, optional
            Define molar comp basis for oxides or endmems
        normalize : boolean, optional
            Normalize output, default is False.

        Returns
        -------
        mol_comp : pandas DataFrame
            Data table of mols of each component

        '''

        if components=='elems':
            mol_comp = self._elem_comp

        elif components=='oxides':
            if basis=='formula':
                mol_comp = self._mol_comp

            elif basis=='atomic':
                mol_comp = self._mol_comp/self.endmember_natom

            else:
                assert False, 'chosen basis is not valid'

        else:
            assert False, ("components is invalid, must select from "
                           "{'oxides','endmems','elems'}")

        if normalize:
            return 100*mol_comp/mol_comp.sum(axis=1)[np.newaxis,:]

        else:
            return mol_comp

    def wt_comp(self, components='oxides', normalize=False):
        '''
        Composition by weight

        Parameters
        ----------
        components : {'oxides','endmems','elems'}, optional
            Define components for expression of composition
        normalize : boolean, optional
            Normalize output, default is False.

        Returns
        -------
        wt_comp : pandas DataFrame
            Data table of wt for each component

        '''

        wt_comp = self._wt_comp

        if normalize:
            return 100*wt_comp/wt_comp.sum(axis=1)[np.newaxis,:]
        else:
            return wt_comp

    @property
    def endmembers(self):
        return self._endmembers

    @property
    def elems(self):
        return self._elems

    @property
    def elem_wts(self):
        return self._elem_wts

    @property
    def elem_names(self):
        return self._elem_names

    @property
    def elem_nums(self):
        return self._elem_nums

    @property
    def endmember_wts(self):
        return self._endmember_wts

    @property
    def endmember_stoic(self):
        return self._endmember_stoic

    @property
    def endmember_natom(self):
        return self._endmember_natom
#===================================================
class GeoCompDB:
    COMP_COL_PREFIX = 'wt:'
    def __init__(self):
        comps, pathname = _read_database_file(
            'GeoSysComps.csv', index_col='Bulk_Comp')
        comps = comps.fillna(0.000)
        self._comps = comps

    @property
    def record_names(self):
        return self._comps.index.values.astype(str)

    def get_record(self, entry_name):
        comps = self._comps
        return comps.loc[entry_name]

    def get_syscomp(self, entry_name, components='oxides',
                    H2O='input', CO2='none'):
        record = self.get_record(entry_name)
        prefix = self.COMP_COL_PREFIX

        oxides = [col for col in record.index
                  if col.startswith(prefix)]
        comp = record[oxides]
        comp.index = [idx[len(prefix):] for idx in comp.index]
        comp = pd.DataFrame(comp).T
        comp = comp.astype(float)

        syscomp = SysComp(comp, units=prefix[:-1], components=components,
                          H2O=H2O,  CO2=CO2)
        return syscomp
#===================================================
