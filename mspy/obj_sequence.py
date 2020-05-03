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

#load libs
import re
import copy

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load blocks
import blocks

# load objects
import obj_compound

# load modules
import mod_basics
import mod_pattern


# SEQUENCE OBJECT DEFINITION
# --------------------------

class sequence:
    """Sequence object definition."""
    
    def __init__(self, chain, title='', accession='', chainType='aminoacids', cyclic=False, **attr):
        
        self.chain = []
        self.chainType = chainType
        self.cyclic = cyclic
        
        # get sequence chain
        if type(chain) == list:
            self.chain = chain
        
        elif self.chainType == 'aminoacids':
            for symbol in chain.upper():
                if not symbol in ('\t','\n','\r','\f','\v', ' ', '-', '*', '.', ''):
                    self.chain.append(symbol)
        else:
            for symbol in chain.split('|'):
                symbol = symbol.strip()
                if not symbol in ('\t','\n','\r','\f','\v', ' ', '-', '*', '.', ''):
                    self.chain.append(symbol)
        
        for monomer in self.chain:
            if not monomer in blocks.monomers:
                raise KeyError, 'Unknown monomer in the sequence! --> ' + monomer
        
        # set terminal groups
        if self.cyclic:
            self.nTermFormula = ''
            self.cTermFormula = ''
        else:
            self.nTermFormula = 'H'
            self.cTermFormula = 'OH'
        
        # [[name, position=[#|symbol], state=[f|v]], ] (f->fixed, v->variable)
        self.modifications = []
        self.labels = []
        
        # for proteins
        self.title = title
        self.accession = accession
        self.orgName = ''
        self.pi = None
        self.score = None
        
        # for peptides
        self.history = [('init', 0, len(self.chain))]
        self.itemBefore = ''
        self.itemAfter = ''
        self.miscleavages = 0
        
        # for fragments
        self.fragmentSerie = None
        self.fragmentIndex = None
        self.fragmentLosses = []
        self.fragmentGains = []
        self.fragmentFiltered = False
        
        # buffers
        self._formula = None
        self._composition = None
        self._mass = None
        
        # get additional attributes
        self.attributes = {}
        for name, value in attr.items():
            self.attributes[name] = value
    # ----
    
    
    def __nonzero__(self):
        """Check sequence length."""
        return bool(len(self.chain))
    # ----
    
    
    def __len__(self):
        """Get sequence length."""
        return len(self.chain)
    # ----
    
    
    def __getitem__(self, i):
        return self.chain[i]
    # ----
    
    
    def __getslice__(self, start, stop):
        """Get slice of the sequence."""
        
        # check slice
        if stop <= start and not self.cyclic:
            raise ValueError, 'Invalid slice!'
        
        # break the links
        parent = copy.deepcopy(self)
        
        # check slice
        start = max(start, 0)
        stop = min(stop, len(parent))
        
        # make new sequence object
        if start < stop:
            seq = parent.chain[start:stop]
            peptide = sequence(seq, chainType=parent.chainType, cyclic=False)
        elif self.cyclic:
            seq = parent.chain[start:] + parent.chain[:stop]
            peptide = sequence(seq, chainType=parent.chainType, cyclic=False)
        
        # add previous history
        peptide.history = parent.history
        
        # add modifications
        for mod in parent.modifications:
            if mod[1] == 'nTerm' and start == 0:
                peptide.modifications.append(mod)
            elif mod[1] == 'cTerm' and (stop == -1 or stop == len(parent)):
                peptide.modifications.append(mod)
            elif type(mod[1]) in (str, unicode) and mod[1] in peptide.chain:
                peptide.modifications.append(mod)
            elif type(mod[1]) == int:
                if start <= mod[1] < stop:
                    mod[1] -= start
                    peptide.modifications.append(mod)
                elif start >= stop and mod[1] >= start:
                    mod[1] -= start
                    peptide.modifications.append(mod)
                elif start >= stop and mod[1] < stop:
                    mod[1] += len(parent) - start
                    peptide.modifications.append(mod)
        
        # add labels
        for mod in parent.labels:
            if type(mod[1]) in (str, unicode) and mod[1] in peptide.chain:
                peptide.labels.append(mod)
            elif type(mod[1]) == int:
                if start <= mod[1] < stop:
                    mod[1] -= start
                    peptide.labels.append(mod)
                elif start >= stop and mod[1] >= start:
                    mod[1] -= start
                    peptide.labels.append(mod)
                elif start >= stop and mod[1] < stop:
                    mod[1] += len(parent) - start
                    peptide.labels.append(mod)
        
        # add terminal modifications
        if start == 0:
            peptide.nTermFormula = parent.nTermFormula
        if stop >= len(parent):
            peptide.cTermFormula = parent.cTermFormula
        if parent.cyclic:
            peptide.nTermFormula = 'H'
            peptide.cTermFormula = 'OH'
        
        # set adjacent monomers
        if start > 0 or parent.cyclic:
            peptide.itemBefore = parent.chain[start-1]
        if stop < len(parent):
            peptide.itemAfter = parent.chain[stop]
        if stop == len(parent) and parent.cyclic:
            peptide.itemAfter = parent.chain[0]
        
        # add event to history
        peptide.history.append(('slice', start, stop))
        
        # ensure buffers are cleaned
        peptide.reset()
        
        return peptide
    # ----
    
    
    def __iter__(self):
        self._index = 0
        return self
    # ----
    
    
    def next(self):
        if self._index < len(self.chain):
            self._index += 1
            return self.chain[self._index-1]
        else:
            raise StopIteration
    # ----
    
    
    def reset(self):
        """Clear sequence buffers."""
        
        self._formula = None
        self._mass = None
        self._composition = None
    # ----
    
    
    
    # SEQUENCE EDITOR ESSENTIALS
    
    def __setslice__(self, start, stop, value):
        """Insert sequence object (essential for sequence editor)."""
        
        # check slice
        if stop < start:
            raise ValueError, 'Invalid slice!'
        
        # check value
        if not isinstance(value, sequence):
            raise TypeError, 'Invalid object to instert!'
        
        # check chain type
        if value.chainType != self.chainType:
            raise TypeError, 'Invalid chain type to instert!'
        
        # break the links
        value = copy.deepcopy(value)
        
        # delete slice
        if stop != start:
            del(self[start:stop])
        
        # insert sequence
        self.chain = self.chain[:start] + value.chain + self.chain[start:]
        
        # shift modifications
        for x, mod in enumerate(self.modifications):
            if type(mod[1]) == int and mod[1] >= start:
                self.modifications[x][1] += (len(value))
        
        # shift labels
        for x, mod in enumerate(self.labels):
            if type(mod[1]) == int and mod[1] >= start:
                self.labels[x][1] += (len(value))
        
        # adding modifications not implemented
        if value.modifications or value.labels:
            raise NotImplementedError, "Sequence __setslice__ doesn't support modifications and labels."
        
        # clear some values
        self.history = [('init', 0, len(self.chain))]
        self.itemBefore = ''
        self.itemAfter = ''
        self.miscleavages = 0
        
        # clear buffers
        self.reset()
    # ----
    
    
    def __delslice__(self, start, stop):
        """Delete slice of sequence (essential for sequence editor)."""
        
        # check slice
        if stop < start:
            raise ValueError, 'Invalid slice!'
        
        # remove sequence
        self.chain = self.chain[:start] + self.chain[stop:]
        
        # remove modifications
        keep = []
        for mod in self.modifications:
            if type(mod[1]) == int and (mod[1] < start or mod[1] >= stop):
                if mod[1] >= stop:
                    mod[1] -= (stop - start)
                keep.append(mod)
            elif type(mod[1]) in (str, unicode) and (mod[1] in self.chain or mod[1] in ('nTerm', 'cTerm')):
                keep.append(mod)
        self.modifications = keep
        
        # remove labels
        keep = []
        for mod in self.labels:
            if type(mod[1]) == int and (mod[1] < start or mod[1] >= stop):
                if mod[1] >= stop:
                    mod[1] -= (stop - start)
                keep.append(mod)
            elif type(mod[1]) in (str, unicode) and mod[1] in self.chain:
                keep.append(mod)
        self.labels = keep
        
        # clear some values
        self.history = [('init', 0, len(self.chain))]
        self.itemBefore = ''
        self.itemAfter = ''
        self.miscleavages = 0
        
        # clear buffers
        self.reset()
    #----
    
    
    
    # GETTERS
    
    def duplicate(self):
        """Return copy of current sequence."""
        
        dupl = copy.deepcopy(self)
        dupl.reset()
        
        return dupl
    # ----
    
    
    def count(self, item):
        """Count item in the chain."""
        return self.chain.count(item)
    # ----
    
    
    def formula(self):
        """Get formula."""
        
        # check formula buffer
        if self._formula != None:
            return self._formula
        
        # get composition
        comp = self.composition()
        
        # format composition
        self._formula = ''
        for el in sorted(comp.keys()):
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
        
        self._composition = {}
        
        # add monomers to formula
        for monomer in self.chain:
            for el, count in blocks.monomers[monomer].composition.items():
                if el in self._composition:
                    self._composition[el] += count
                else:
                    self._composition[el] = count
        
        # add modifications and labels
        mods = self.modifications + self.labels
        for name, position, state in mods:
            multi = 1
            if type(position) in (str, unicode) and position !='' and not position in ('nTerm', 'cTerm'):
                multi = self.chain.count(position)
            for el, count in blocks.modifications[name].composition.items():
                if el in self._composition:
                    self._composition[el] += multi*count
                else:
                    self._composition[el] = multi*count
        
        # add terminal formulae
        if not self.cyclic:
            termCmpd = obj_compound.compound(self.nTermFormula + self.cTermFormula)
            for el, count in termCmpd.composition().items():
                if el in self._composition:
                    self._composition[el] += count
                else:
                    self._composition[el] = count
        
        # subtract neutral losses for fragments
        for loss in self.fragmentLosses:
            lossCmpd = obj_compound.compound(loss)
            for el, count in lossCmpd.composition().items():
                if el in self._composition:
                    self._composition[el] -= count
                else:
                    self._composition[el] = -1*count
        
        # add neutral gains for fragments
        for gain in self.fragmentGains:
            gainCmpd = obj_compound.compound(gain)
            for el, count in gainCmpd.composition().items():
                if el in self._composition:
                    self._composition[el] += count
                else:
                    self._composition[el] = count
        
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
            self._mass = obj_compound.compound(self.formula()).mass()
        
        # return mass
        if massType == 0:
            return self._mass[0]
        elif massType ==  1:
            return self._mass[1]
        else:
            return self._mass
    # ----
    
    
    def mz(self, charge, agentFormula='H', agentCharge=1):
        """Get ion m/z"""
        
        return mod_basics.mz(
            mass = self.mass(),
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
    
    
    def format(self, template='S [m]'):
        """Get formated sequence."""
        
        keys = {}
        
        # make sequence keys
        if self.chainType == 'aminoacids':
            keys['S'] = ''.join(self.chain)
            keys['s'] = ''.join(self.chain).lower()
            keys['B'] = self.itemBefore
            keys['A'] = self.itemAfter
            keys['b'] = self.itemBefore.lower()
            keys['a'] = self.itemAfter.lower()
        else:
            keys['S'] = ' | '.join(self.chain)
            keys['s'] = '|'.join(self.chain)
            keys['b'] = self.itemBefore
            keys['a'] = self.itemAfter
            keys['B'] = self.itemBefore
            keys['A'] = self.itemAfter
        
        # make terminal formula keys
        keys['N'] = self.nTermFormula
        keys['C'] = self.cTermFormula
        
        # make modification keys
        keys['m'] = self._formatModifications(self.modifications)
        keys['M'] = self._formatModifications(self.modifications + self.labels)
        keys['l'] = self._formatModifications(self.labels)
        keys['p'] = self.miscleavages
        
        # make history key
        keys['h'] = ''
        if 'h' in template:
            for item in self.history[1:]:
                if item[0] == 'slice':
                    keys['h'] += '[%s-%s]' % (item[1]+1, item[2])
                elif item[0] == 'break':
                    keys['h'] += '[%s|%s]' % (item[1]+1, item[2]+1)
        
        # make fragment name key
        keys['f'] = ''
        if 'f' in template and self.fragmentSerie:
            keys['f'] = self.fragmentSerie
            if self.fragmentIndex != None:
                keys['f'] += str(self.fragmentIndex)
            for gain in self.fragmentGains:
                keys['f'] += ' +'+gain
            for loss in self.fragmentLosses:
                keys['f'] += ' -'+loss
        
        # format
        buff = ''
        for char in template:
            if char in keys:
                buff += keys[char]
            else:
                buff += char
        
        # clear format
        buff = buff.replace('[]', '')
        buff = buff.replace('()', '')
        buff = buff.strip()
        
        return buff
    # ----
    
    
    def search(self, mass, charge, tolerance, enzyme=None, semiSpecific=True, tolUnits='Da', massType=0, maxMods=1, position=False):
        """Search sequence for specified ion.
            mass: (float) m/z value to search for
            charge: (int) charge of the m/z value
            tolerance: (float) mass tolerance
            tolUnits: ('Da', 'ppm') tolerance units
            enzyme: (str) enzyme used for peptides endings, if None H/OH is used
            semiSpecific: (bool) semispecific cleavage is checked (enzyme must be set)
            massType: (0 or 1) mass type of the mass value, 0 = monoisotopic, 1 = average
            maxMods: (int) maximum number of modifications at one residue
            position: (bool) retain position for variable modifications (much slower)
        """
        
        # check cyclic peptides
        if self.cyclic:
            raise TypeError, 'Search function is not supported for cyclic peptides!'
        
        matches = []
        
        # set terminal modifications
        if enzyme:
            enzyme = blocks.enzymes[enzyme]
            expression = re.compile(enzyme.expression+'$')
            nTerm = enzyme.nTermFormula
            cTerm = enzyme.cTermFormula
        else:
            semiSpecific = False
            nTerm = 'H'
            cTerm = 'OH'
        
        # set mass limits
        if tolUnits == 'ppm':
            lowMass = mass - (tolerance * mass/1000000)
            highMass = mass + (tolerance * mass/1000000)
        else:
            lowMass = mass - tolerance
            highMass = mass + tolerance
        
        # search sequence
        length = len(self)
        for i in range(length):
            for j in range(i+1, length+1):
                
                CHECK_FORCE_QUIT()
                
                # get peptide
                peptide = self[i:j]
                if i != 0:
                    peptide.nTerminalFormula = nTerm
                if j != length:
                    peptide.cTerminalFormula = cTerm
                
                # check enzyme specifity
                if semiSpecific and peptide.itemBefore and peptide.itemAfter:
                    if not expression.search(peptide.itemBefore+peptide.chain[0]) and not expression.search(peptide.chain[-1]+peptide.itemAfter):
                        continue
                
                # variate modifications
                variants = peptide.variations(maxMods=maxMods, position=position)
                
                # check mass limits
                peptides = []
                masses = []
                for pep in variants:
                    pepMZ = pep.mz(charge)[massType]
                    peptides.append((pepMZ, pep))
                    masses.append(pepMZ)
                if max(masses) < lowMass:
                    continue
                elif min(masses) > highMass:
                    break
                
                # search for matches
                for pep in peptides:
                    if lowMass <= pep[0] <= highMass:
                        matches.append(pep[1])
        
        return matches
    # ----
    
    
    def variations(self, maxMods=1, position=True, enzyme=None):
        """Calculate all possible combinations of variable modifications.
            maxMods: (int) maximum modifications allowed per one residue
            position: (bool) retain modifications positions (much slower)
            enzyme: (str) enzyme name to ensure that modifications are not presented in cleavage site
        """
        
        variablePeptides = []
        
        # get modifications
        fixedMods = []
        variableMods = []
        for mod in self.modifications:
            
            # fixed modifications
            if mod[2] == 'f':
                fixedMods.append(mod)
            
            # positioned modifications
            elif type(mod[1]) == int:
                variableMods.append(mod)
            
            # terminal modifications
            elif mod[1] in ('nTerm', 'cTerm'):
                variableMods.append(mod)
            
            # retain position of global modifications
            elif position:
                for x, symbol in enumerate(self.chain):
                    if symbol == mod[1]:
                        variableMods.append([mod[0], x, 'v'])
            else:
                variableMods += [mod] * self.chain.count(mod[1])
        
        # make combinations of variable modifications
        variableMods = self._countUniqueModifications(variableMods)
        combinations = []
        for x in self._uniqueCombinations(variableMods):
            combinations.append(x)
        
        # disable positions occupied by fixed modifications
        occupied = []
        for mod in fixedMods:
            count = max(1, self.chain.count(str(mod[1])))
            occupied += [mod[1]]*count
        
        # disable modifications at cleavage sites
        if enzyme:
            enz = blocks.enzymes[enzyme]
            if not enz.modsBefore and self.itemAfter:
                occupied += [len(self)-1]*maxMods
            if not enz.modsAfter and self.itemBefore:
                occupied += [0]*maxMods
        
        CHECK_FORCE_QUIT()
        
        # filter modifications
        buff = []
        for combination in combinations:
            positions = occupied[:]
            for mod in combination:
                positions += [mod[0][1]]*mod[1]
            if self._checkModifications(positions, self.chain, maxMods):
                buff.append(combination)
        combinations = buff
        
        CHECK_FORCE_QUIT()
        
        # format modifications and filter same
        buff = []
        for combination in combinations:
            mods = []
            for mod in combination:
                if position:
                    mods += [[mod[0][0], mod[0][1], 'f']]*mod[1]
                elif mod[0][1] in ('nTerm', 'cTerm'):
                    mods += [[mod[0][0], mod[0][1],'f']]
                else:
                    mods += [[mod[0][0],'','f']]*mod[1]
            mods.sort()
            if not mods in buff:
                buff.append(mods)
        combinations = buff
        
        # make new peptides
        for combination in combinations:
            
            CHECK_FORCE_QUIT()
            
            variablePeptide = self.duplicate()
            variablePeptide.modifications[:] = fixedMods+combination
            
            # check composition
            if variablePeptide.isvalid():
                variablePeptides.append(variablePeptide)
        
        return variablePeptides
    # ----
    
    
    def linearized(self, breakPoint=None):
        """Return list of all linearized sequences resulted from cyclic parent."""
        
        # ensure sequence is cyclic
        cyclic = self.cyclic
        self.cyclic = True
        
        # set break points
        breakPoints = range(len(self))
        if breakPoint != None:
            breakPoints = [breakPoint]
        
        # make peptides for all break points
        peptides = []
        for x in breakPoints:
            
            # make peptide
            peptide = self[x:x]
            
            # add new event to history
            del peptide.history[-1]
            if x != 0:
                peptide.history.append(('break', x-1, x))
            else:
                peptide.history.append(('break', len(self)-1, x))
            
            # remove terminal modifications
            todelete = []
            for i, mod in enumerate(peptide.modifications):
                if mod[1] in ('nTerm', 'cTerm'):
                    todelete.append(i)
            for i in sorted(todelete, reverse=True):
                del peptide.modifications[i]
            
            # append peptide
            peptides.append(peptide)
        
        # revert self to original cyclization
        self.cyclic = cyclic
        
        if breakPoint:
            return peptides[0]
        else:
            return peptides
    # ----
    
    
    def indexes(self):
        """Calculate parent indexes from sequence history."""
        
        ranges = range(self.history[0][1], self.history[0][2])
        for item in self.history[1:]:
            if item[0] == 'slice':
                ranges = ranges[item[1] : item[2]]
            elif item[0] == 'break':
                ranges = ranges[item[2]:]+ranges[:item[1]+1]
        
        return ranges
    # ----
    
    
    def ismodified(self, position=None, strict=False):
        """Check if selected amino acid or whole sequence has any modification.
            position: (int) amino acid index
            strict: (bool) check variable modifications
        """
        
        # check specified position only
        if position != None:
            for mod in self.modifications:
                if (strict or mod[2]=='f'):
                    if mod[1] == position \
                    or mod[1] == self.chain[position] \
                    or (mod[1] == 'nTerm' and position == 0) \
                    or (mod[1] == 'cTerm' and position == -1) \
                    or (mod[1] == 'cTerm' and position == (len(self.chain) - 1)):
                        return True
        
        # check whole sequence
        else:
            for mod in self.modifications:
                if strict or mod[2]=='f':
                    return True
        
        # not modified
        return False
    # ----
    
    
    def isvalid(self, charge=0, agentFormula='H', agentCharge=1):
        """Utility to check ion composition."""
        
        # make compound
        formula = obj_compound.compound(self.formula())
        
        # check ion composition
        return formula.isvalid(
            charge = charge,
            agentFormula = agentFormula,
            agentCharge = agentCharge
        )
    # ----
    
    
    
    # MODIFIERS
    
    def modify(self, name, position, state='f'):
        """Apply modification to sequence."""
        
        # check modification
        if not name in blocks.modifications:
            raise KeyError, 'Unknown modification! --> ' + name
        
        # check position
        try: position = int(position)
        except: position = str(position)
        
        if self.cyclic and position in ('nTerm', 'cTerm'):
            return False
        if type(position) == str and (not position in ('nTerm', 'cTerm') and not position in self.chain):
            return False
        if type(position) == int and (position < 0 or position >= len(self)):
            return False
        
        # add modification
        self.modifications.append([name, position, str(state)])
        
        # clear buffers
        self.reset()
        
        return True
    # ----
    
    
    def unmodify(self, name=None, position=None, state='f'):
        """Remove modification from sequence."""
        
        # remove all modifications
        if name == None:
            del self.modifications[:]
        
        # remove modification
        else:
            try: mod = [name, int(position), str(state)]
            except: mod = [name, str(position), str(state)]
            while mod in self.modifications:
                del self.modifications[self.modifications.index(mod)]
        
        # clear buffers
        self.reset()
    # ----
    
    
    def label(self, name, position, state='f'):
        """Apply label modification to sequence."""
        
        # check modification
        if not name in blocks.modifications:
            raise KeyError, 'Unknown modification! --> ' + name
        
        # check position
        try: position = int(position)
        except: position = str(position)
        if type(position) == str and not position in self.chain:
            return False
        elif type(position) == int and (position < 0 or position >= len(self)):
            return False
        
        # add label
        self.labels.append([name, position, state])
        
        # clear buffers
        self.reset()
        
        return True
    # ----
    
    
    def cyclize(self, cyclic=True):
        """Make current sequence cyclic/linear."""
        
        # make sequence cyclic
        if cyclic:
            self.cyclic = True
            self.nTermFormula = ''
            self.cTermFormula = ''
        else:
            self.cyclic = False
            self.nTermFormula = 'H'
            self.cTermFormula = 'OH'
        
        # remove terminal modifications
        if cyclic:
            todelete = []
            for x, mod in enumerate(self.modifications):
                if mod[1] in ('nTerm', 'cTerm'):
                    todelete.append(x)
            for x in sorted(todelete, reverse=True):
                del self.modifications[x]
        
        # clear buffers
        self.reset()
    # ----
    
    
    
    # HELPERS
    
    def _formatModifications(self, modifications):
        """Format modifications."""
        
        # get modifications
        modifs = {}
        for mod in modifications:
            
            # count modification
            if mod[1] == '' or type(mod[1]) == int:
                count = 1
            elif mod[1] in ('nTerm', 'cTerm'):
                count = 1
            else:
                count = self.chain.count(mod[1])
            
            # add modification to dic
            if count and mod[0] in modifs:
                modifs[mod[0]] += count
            elif count:
                modifs[mod[0]] = count
        
        # format modifications
        if modifs:
            mods = ''
            for mod in sorted(modifs.keys()):
                mods += '%sx%s; ' % (modifs[mod], mod)
            return '%s' % mods[:-2]
        else:
            return ''
    # ----
    
    
    def _uniqueCombinations(self, items):
        """Generate unique combinations of items."""
        
        for i in range(len(items)):
            for cc in self._uniqueCombinations(items[i+1:]):
                for j in range(items[i][1]):
                    yield [[items[i][0],items[i][1]-j]] + cc
        yield []
    # ----
    
    
    def _countUniqueModifications(self, modifications):
        """Get list of unique modifications with counter."""
        
        uniqueMods = []
        modsCount = []
        for mod in modifications:
            if mod in uniqueMods:
                modsCount[uniqueMods.index(mod)] +=1
            else:
                uniqueMods.append(mod)
                modsCount.append(1)
        
        modsList = []
        for x, mod in enumerate(uniqueMods):
            modsList.append([mod, modsCount[x]])
        
        return modsList
    # ----
    
    
    def _checkModifications(self, positions, chain, maxMods):
        """Check if current modification set is applicable."""
        
        for x in positions:
            count = positions.count(x)
            if type(x) == int:
                if count > maxMods:
                    return False
            elif x in ('nTerm', 'cTerm'):
                if count > maxMods:
                    return False
            elif type(x) in (str, unicode):
                available = chain.count(x)
                for y in positions:
                    if type(y) == int and chain[y] == x:
                        available -= 1
                if count > (available * maxMods):
                    return False
        
        return True
    # ----
    
    

