# -------------------------------------------------------------------------
#     Copyright (C) 2005-2013 Martin Strohalm <www.mmass.org>

#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#     GNU General Public License for more details.

#     Complete text of GNU GPL can be found in the file LICENSE.TXT in the
#     main directory of the program.
# -------------------------------------------------------------------------

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load objects
import blocks

# load modules
import mod_basics
import mod_pattern


# COMPOUND OBJECT DEFINITION
# --------------------------

class compound:
    """Compound object definition."""
    
    def __init__(self, expression, **attr):
        
        # check formula
        self._checkFormula(expression)
        self.expression = expression
        
        # buffers
        self._composition = None
        self._formula = None
        self._mass = None
        self._nominalmass = None
        
        # get additional attributes
        self.attributes = {}
        for name, value in attr.items():
            self.attributes[name] = value
    # ----
    
    
    def __iadd__(self, other):
        """Append formula."""
        
        # check and append value
        if isinstance(other, compound):
            self.expression += other.expression
        else:
            self._checkFormula(other)
            self.expression += other
        
        # clear buffers
        self.reset()
        
        return self
    # ----
    
    
    def reset(self):
        """Clear formula buffers."""
        
        self._composition = None
        self._formula = None
        self._mass = None
        self._nominalmass = None
    # ----
    
    
    
    # GETTERS
    
    def count(self, item, groupIsotopes=False):
        """Count atom in formula."""
        
        # get composition
        comp = self.composition()
        
        # get atoms to count
        atoms = [item]
        if groupIsotopes and item in blocks.elements:
            for massNo in blocks.elements[item].isotopes:
                atom = '%s{%d}' % (item,massNo)
                atoms.append(atom)
        
        # count atom
        atomsCount = 0
        for atom in atoms:
            if atom in comp:
                atomsCount += comp[atom]
        
        return atomsCount
    # ----
    
    
    def formula(self):
        """Get formula."""
        
        # check formula buffer
        if self._formula != None:
            return self._formula
        
        self._formula = ''
        
        # get composition
        comp = self.composition()
        elements = sorted(comp.keys())
        
        # add C and H first
        for el in ('C', 'C{12}', 'C{13}', 'C{14}', 'H', 'H{1}', 'H{2}', 'H{3}'):
            if el in elements:
                if comp[el] == 1:
                    self._formula += el
                else:
                    self._formula += '%s%d' % (el, comp[el])
                del elements[elements.index(el)]
        
        # add remaining atoms
        for el in elements:
            if comp[el] == 1:
                self._formula += el
            else:
                self._formula += '%s%d' % (el, comp[el])
        
        return self._formula
    # ----
    
    
    def composition(self):
        """Get elemental composition."""
        
        # check composition buffer
        if self._composition != None:
            return self._composition
        
        # unfold brackets
        unfoldedFormula = self._unfoldBrackets(self.expression)
        
        # group elements
        self._composition = {}
        for symbol, isotop, count in mod_basics.ELEMENT_PATTERN.findall(unfoldedFormula):
            
            # make atom
            if isotop:
                atom = '%s{%s}' % (symbol, isotop)
            else:
                atom = symbol
            
            # convert counting
            if count:
                count = int(count)
            else:
                count = 1
            
            # add atom
            if atom in self._composition:
                self._composition[atom] += count
            else:
                self._composition[atom] = count
        
        # remove zeros
        for atom in self._composition.keys():
            if self._composition[atom] == 0:
                del self._composition[atom]
        
        return self._composition
    # ----
    
    
    def mass(self, massType=None):
        """Get mass."""
        
        # get mass
        if self._mass == None:
            massMo = 0
            massAv = 0
            
            # get composition
            comp = self.composition()
            
            # get mass for each atom
            for atom in comp:
                count = comp[atom]
                
                # check specified isotope and mass
                match = mod_basics.ELEMENT_PATTERN.match(atom)
                symbol, massNumber, tmp = match.groups()
                if massNumber:
                    isotope = blocks.elements[symbol].isotopes[int(massNumber)]
                    atomMass = (isotope[0], isotope[0])
                else:
                    atomMass = blocks.elements[symbol].mass
                
                # multiply atom mass
                massMo += atomMass[0]*count
                massAv += atomMass[1]*count
            
            # store mass in buffer
            self._mass = (massMo, massAv)
        
        # return mass
        if massType == 0:
            return self._mass[0]
        elif massType ==  1:
            return self._mass[1]
        else:
            return self._mass
    # ----
    
    
    def nominalmass(self):
        """Get nominal mass."""
        
        # get mass
        if self._nominalmass == None:
            
            nominalmass = 0
            
            # get composition
            comp = self.composition()
            
            # get mass for each atom
            for atom in comp:
                count = comp[atom]
                
                # check specified isotope and mass
                match = mod_basics.ELEMENT_PATTERN.match(atom)
                symbol, massNumber, tmp = match.groups()
                if massNumber:
                    isotope = blocks.elements[symbol].isotopes[int(massNumber)]
                    atomMass = isotope[0]
                else:
                    atomMass = blocks.elements[symbol].mass[0]
                
                # multiply atom mass
                nominalmass += round(atomMass)*count
            
            # store mass in buffer
            self._nominalmass = nominalmass
        
        return self._nominalmass
    # ----
    
    
    def mz(self, charge, agentFormula='H', agentCharge=1):
        """Get ion m/z."""
        
        return mod_basics.mz(self.mass(),
            charge = charge,
            agentFormula = agentFormula,
            agentCharge = agentCharge
        )
    # ----
    
    
    def pattern(self, fwhm=0.1, threshold=0.01, charge=0, agentFormula='H', agentCharge=1, real=True):
        """Get isotopic pattern."""
        
        return mod_pattern.pattern(
            compound = self,
            fwhm = fwhm,
            threshold = threshold,
            charge = charge,
            agentFormula = agentFormula,
            agentCharge = agentCharge,
            real = real
        )
    # ----
    
    
    def rdbe(self):
        """Get RDBE (Range or Double Bonds Equivalents)."""
        
        return mod_basics.rdbe(self)
    # ----
    
    
    def isvalid(self, charge=0, agentFormula='H', agentCharge=1):
        """Check ion composition."""
        
        # check agent formula
        if agentFormula != 'e' and not isinstance(agentFormula, compound):
            agentFormula = compound(agentFormula)
        
        # make ion compound
        if charge and agentFormula != 'e':
            ionFormula = self.expression
            for atom, count in agentFormula.composition().items():
                ionFormula += '%s%d' % (atom, count*(charge/agentCharge))
            ion = compound(ionFormula)
        else:
            ion = compound(self.expression)
        
        # get composition
        for atom, count in ion.composition().items():
            if count < 0:
                return False
        
        return True
    # ----
    
    
    def frules(self, rules=['HC','NOPSC','NOPS','RDBE'], HC=(0.1, 3.0), NOPSC=(4,3,2,3), RDBE=(-1,40)):
        """Check formula rules."""
        
        return mod_basics.frules(
            compound = self,
            rules = rules,
            HC = HC,
            NOPSC = NOPSC,
            RDBE = RDBE
        )
    # ----
    
    
    
    # MODIFIERS
    
    def negate(self):
        """Make all atom counts negative."""
        
        # get composition
        comp = self.composition()
        
        # negate composition
        formula = ''
        for el in sorted(comp.keys()):
            formula += '%s%d' % (el, -1*comp[el])
        self.expression = formula
        
        # clear buffers
        self.reset()
    # ----
    
    
    
    # HELPERS
    
    def _checkFormula(self, formula):
        """Check given formula."""
        
        # check formula
        if not mod_basics.FORMULA_PATTERN.match(formula):
            raise ValueError, 'Wrong formula! --> ' + formula
        
        # check elements and isotopes
        for atom in mod_basics.ELEMENT_PATTERN.findall(formula):
            if not atom[0] in blocks.elements:
                raise ValueError, 'Unknown element in formula! --> ' + atom[0] + ' in ' + formula
            elif atom[1] and not int(atom[1]) in blocks.elements[atom[0]].isotopes:
                raise ValueError, 'Unknown isotope in formula! --> ' + atom[0] + atom[1] + ' in ' + formula
        
        # check brackets
        if formula.count(')') != formula.count('('):
            raise ValueError, 'Wrong number of brackets in formula! --> ' + formula
    # ----
    
    
    def _unfoldBrackets(self, string):
        """Unfold formula and count each atom."""
        
        unfoldedFormula = ''
        brackets = [0,0]
        enclosedFormula = ''
        
        i = 0
        while i < len(string):
            
            # handle brackets
            if string[i] == '(':
                brackets[0] += 1
            elif string[i] == ')':
                brackets[1] += 1
            
            # part outside brackets
            if brackets == [0,0]:
                unfoldedFormula += string[i]
            
            # part within brackets
            else:
                enclosedFormula += string[i]
                
                # unfold part within brackets
                if brackets[0] == brackets[1]:
                    enclosedFormula = self._unfoldBrackets(enclosedFormula[1:-1])
                    
                    # multiply part within brackets
                    count = ''
                    while len(string)>(i+1) and string[i+1].isdigit():
                        count += string[i+1]
                        i += 1
                    if count:
                        enclosedFormula = enclosedFormula * int(count)
                    
                    # add and clear
                    unfoldedFormula += enclosedFormula
                    enclosedFormula = ''
                    brackets = [0,0]
            
            i += 1
            
        return unfoldedFormula
    # ----
    
    

