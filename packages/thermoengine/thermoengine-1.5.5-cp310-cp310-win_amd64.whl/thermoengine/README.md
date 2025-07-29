# Todo

## Merge Mark's changes to equilibrate back into thermoengine version
* Mark relied on old sub-package architecture
* we update to use submodules and put all objective C stuff in core
* need to import core and use core functions


## Implement phase derivative functions
[o]  _calc_Cp(self, T, P, mol=[], V=None):
[o]  _calc_dV_dT(self, T, P, mol=[], V=None):
[o]  _calc_dV_dP(self, T, P, mol=[], V=None):
[o]  _calc_dCp_dT(self, T, P, mol=[], V=None):
[o]  _calc_d2V_dT2(self, T, P, mol=[], V=None):
[o]  _calc_d2V_dTdP(self, T, P, mol=[], V=None):
[o]  _calc_d2V_dP2(self, T, P, mol=[], V=None):
[o]  _calc_mu(self, T, P, mol=[], V=None):
[ ]  _calc_dG_dm(self, T, P, mol=[], V=None):
[ ]  _calc_a(self, T, P, mol=[], V=None):
[ ]  _calc_dV_dm(self, T, P, mol=[], V=None):
[ ]  _calc_dS_dm(self, T, P, mol=[], V=None):
[ ]  _calc_d2G_dm2(self, T, P, mol=[], V=None):
[ ]  _calc_da_dm(self, T, P, mol=[], V=None):
[ ]  _calc_dCp_dm(self, T, P, mol=[], V=None):
[ ]  _calc_d2V_dmdT(self, T, P, mol=[], V=None):
[ ]  _calc_d2V_dmdP(self, T, P, mol=[], V=None):
[ ]  _calc_d2S_dm2(self, T, P, mol=[], V=None):
[ ]  _calc_d2V_dm2(self, T, P, mol=[], V=None):
[ ]  _calc_d3G_dm3(self, T, P, mol=[], V=None):




# (PhaseObjC) Stoichiometric Phase Protocol

## deriv (order=0)
-(double)getGibbsFreeEnergyFromT_andP_
-(double)getEnthalpyFromT_andP_

## deriv (order=1)
-(double)getEntropyFromT_andP_
-(double)getVolumeFromT_andP_
-(double)getChemicalPotentialFromT_andP_

## deriv (order=2)
-(double)getHeatCapacityFromT_andP_
-(double)getDvDtFromT_andP_
-(double)getDvDpFromT_andP_

## deriv (order=3)
-(double)getDcpDtFromT_andP_
-(double)getD2vDt2FromT_andP_
-(double)getD2vDtDpFromT_andP_
-(double)getD2vDp2FromT_andP_




## General
-(NSString )getFormulaFromInternalVariables


# (PhaseObjC) Solution Phase Protocol

## deriv (order=0)
-(double)getGibbsFreeEnergyFromMolesOfComponents_andT_andP_
-(double)getEnthalpyFromMolesOfComponents_andT_andP_

## deriv (order=1)
-(double)getEntropyFromMolesOfComponents_andT_andP_
-(double)getVolumeFromMolesOfComponents_andT_andP_
-(DoubleVector )getChemicalPotentialFromMolesOfComponents_andT_andP_
-(DoubleVector )getDgDmFromMolesOfComponents_andT_andP_
-(DoubleVector )getActivityFromMolesOfComponents_andT_andP_

## deriv (order=2)
-(double)getHeatCapacityFromMolesOfComponents_andT_andP_
-(double)getDvDtFromMolesOfComponents_andT_andP_
-(double)getDvDpFromMolesOfComponents_andT_andP_



# (thermoengine update) joint Phase solution

## deriv (order=0)
- calc_G()
- calc_H()

## deriv (order=1)
- calc_S()
- calc_V()

- calc_mu()
- calc_dGdm()
- calc_a()

## deriv (order=2)
- calc_Cp()
- calc_dVdT()
- calc_dVdP()

- calc_dVdm()
- calc_dSdm()
- calc_d2Gdm2()
- calc_dadm()

## deriv (order=3)
- calc_dCpdT()
- calc_d2VdT2()
- calc_d2VdTdP()
- calc_d2VdP2()

- calc_dCpdm()
- calc_d2VdmdT()
- calc_d2VdmdP()
- calc_d2Sdm2()
- calc_d2Vdm2()
- calc_d3Gdm3()


-(DoubleVector )getDvDmFromMolesOfComponents_andT_andP_
-(DoubleVector )getDsDmFromMolesOfComponents_andT_andP_
-(DoubleMatrix )getD2gDm2FromMolesOfComponents_andT_andP_
-(DoubleMatrix )getDaDmFromMolesOfComponents_andT_andP_

## deriv (order=3)
-(double)getDcpDtFromMolesOfComponents_andT_andP_
-(double)getD2vDt2FromMolesOfComponents_andT_andP_
-(double)getD2vDtDpFromMolesOfComponents_andT_andP_
-(double)getD2vDp2FromMolesOfComponents_andT_andP_

-(DoubleVector )getDCpDmFromMolesOfComponents_andT_andP_
-(DoubleVector )getD2vDmDtFromMolesOfComponents_andT_andP_
-(DoubleVector )getD2vDmDpFromMolesOfComponents_andT_andP_
-(DoubleMatrix )getD2sDm2FromMolesOfComponents_andT_andP_
-(DoubleMatrix )getD2vDm2FromMolesOfComponents_andT_andP_
-(DoubleTensor )getD3gDm3FromMolesOfComponents_andT_andP_


## General
```
-(void)setResultsToMixingQuantities:(BOOL)yesForMixing
-(NSUInteger)numberOfSolutionComponents
-(id)componentAtIndex:(NSUInteger)index
-(BOOL)testPermissibleValuesOfComponents_
-(DoubleVector )convertElementsToMoles_
-(double)convertElementsToTotalMoles_
-(double)convertElementsToTotalMass_
-(DoubleVector )convertMolesToMoleFractions_
-(DoubleVector )convertMolesToElements_
-(double)totalMolesFromMolesOfComponents_

-(NSString )getFormulaFromMolesOfComponents_andT_andP_
-(NSString *)nameOfPhaseWithComposition_
```

```
-(NSUInteger)numberOfSolutionSpecies
-(NSString )nameOfSolutionSpeciesAtIndex_
-(DoubleVector )elementalCompositionOfSpeciesAtIndex_
-(DoubleVector )convertMolesOfSpeciesToMolesOfComponents_
-(DoubleVector )chemicalPotentialsOfSpeciesFromMolesOfComponents_andT_andP_

-(NSArray )affinityAndCompositionFromLiquidChemicalPotentialSum_andT_andP_
-(NSDictionary *)checkForAndDetermineCompositionOfCoexistingImmisciblePhase_andT_andP_
-(void)incrementInstanceCountOfPhase
-(void)decrementInstanceCountOfPhase
```

@param chemicalPotentials chemical potentials of endmember components in the solution. A zero entry indicates a component is absent.
@param t temperature in K
@param p pressure in bars
@return NSArray output structure:
(0): NSNumber object wrapping a double - chemical affinity
(1...NA): NSnumber object wrapping a double - X[0] - X[NA-1], mole fraction compositional variables
(NA+1): NSNumber object wapping a BOOL - convergence flag
(NA+2): NSNumber object wrapping an NSUInteger - iteration count
(NA+3): NSNumber object wrapping a double - number of atoms in formula unit to scale affinity
(NA+4): NSNumber object wrapping a double - approximate error in calculated affinity
