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

# load libs
import re
import itertools

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load building blocks
import blocks

# load objects
import obj_sequence


# SEQUENCE DIGESTION
# ------------------

def digest(sequence, enzyme, miscleavage=0, allowMods=False, strict=True):
    """Digest seuence by specified enzyme.
        sequence: (sequence) mspy sequence object
        enzyme: (str) enzyme name - must be defined in mspy.enzymes
        miscleavage: (int) number of allowed misscleavages
        allowMods: (bool) do not care about modifications in cleavage site
        strict: (bool) do not cleave even if variable modification is in cleavage site
    """
    
    # check sequence object
    if not isinstance(sequence, obj_sequence.sequence):
        raise TypeError, "Cannot digest non-sequence object!"
    
    # check cyclic peptides
    if sequence.chainType != 'aminoacids':
        raise TypeError, 'Digest function is not supported for non-amino sequences!'
    
    # check cyclic peptides
    if sequence.cyclic:
        raise TypeError, 'Digest function is not supported for cyclic peptides!'
    
    # check sequence
    if not sequence.chain:
        return []
    
    # get enzyme
    if enzyme in blocks.enzymes:
        enzyme = blocks.enzymes[enzyme]
        expression = re.compile(enzyme.expression+'$')
    else:
        raise KeyError, 'Unknown enzyme! -> ' + enzyme
    
    # get digest indices
    slices = [] # from | to | miscl
    lastIndex = 0
    peptide = ''
    for x, aa in enumerate(sequence):
        
        # check expression
        peptide += aa
        if expression.search(peptide):
            
            # skip not allowed modifications
            if not allowMods and sequence.ismodified(x-1, strict) and not enzyme.modsBefore:
                continue
            elif not allowMods and sequence.ismodified(x, strict) and not enzyme.modsAfter:
                continue
            else:
                slices.append((lastIndex, x, 0))
                lastIndex = x
    
    # add last peptide
    slices.append((lastIndex, x+1, 0))
    
    # add indices for partials
    indices = len(slices)
    for x in range(indices):
        for y in range(1, miscleavage+1):
            if x+y < indices:
                slices.append((slices[x][0], slices[x+y][1], y))
            else:
                break
    
    # get peptides slices from protein
    peptides = []
    for indices in slices:
        
        CHECK_FORCE_QUIT()
        
        # get peptide
        peptide = sequence[indices[0]:indices[1]]
        peptide.miscleavages = indices[2]
        
        # add terminal groups
        if indices[0] != 0:
            peptide.nTermFormula = enzyme.nTermFormula
        if indices[1] != len(sequence):
            peptide.cTermFormula = enzyme.cTermFormula
        
        peptides.append(peptide)
    
    return peptides
# ----


def coverage(ranges, length, human=True):
    """Calculate sequence coverage.
        ranges: (list of mspy.sequence or list of user ranges (start,stop))
        length: (int) parent sequence length
        human: (bool) ranges in human (True) or computer (False) indexes
    """
    
    # check data
    if not ranges:
        return 0.
    
    # make a blank sequence
    blank = length*[0]
    
    # list of ranges
    for r in ranges:
        if human:
            for x in range(r[0]-1, r[1]):
                blank[x]=(1)
        else:
            for x in range(r[0], r[1]):
                blank[x]=(1)
    
    # get sequence coverage
    return 100.0*blank.count(1)/length
# ----



# SEQUENCE FRAGMENTATION
# ----------------------

def fragment(sequence, series, scrambling=False):
    """Generate list of neutral peptide fragments from given peptide.
        sequence: (sequence) mspy sequence object
        series: (list) list of fragment serie names - must be defined in mspy.fragments
        scrambling: (int) allow sequence scrambling
    """
    
    frags = []
    scramblingFilter = ('M')
    
    # check sequence object
    if not isinstance(sequence, obj_sequence.sequence):
        raise TypeError, "Cannot fragment non-sequence object!"
    
    # generate fragments for linear peptide
    if not sequence.cyclic:
        for serie in series:
            frags += fragmentserie(sequence, serie)
    
    # generate fragments for cyclic peptide
    else:
        for peptide in sequence.linearized():
            for serie in series:
                frags += fragmentserie(peptide, serie, cyclicParent=True)
    
    # generate scrambling fragments
    if scrambling:
        buff = []
        for frag in frags:
            
            # check fragment
            if len(frag) <= 2 or not frag.fragmentSerie in ('a', 'b', 'M'):
                continue
            elif frag.fragmentSerie == 'M' and sequence.cyclic:
                continue
            
            # generate fragments
            for peptide in frag.linearized():
                for serie in series:
                    if not serie in scramblingFilter:
                        buff += fragmentserie(peptide, serie, cyclicParent=sequence.cyclic)
        
        frags += buff
    
    # remove same fragments
    buff = []
    have = []
    for frag in frags:
        frhash = [frag.fragmentSerie] + frag.indexes()
        if frag.fragmentSerie == 'M':
            frhash.sort()
        if not frhash in have:
            buff.append(frag)
            have.append(frhash)
    
    frags = buff
    
    return frags
# ----


def fragmentserie(sequence, serie, cyclicParent=False):
    """Generate list of neutral peptide fragments from given peptide.
        sequence: (sequence) mspy sequence object
        serie: (str) fragment serie name - must be defined in mspy.fragments
    """
    
    # check sequence object
    if not isinstance(sequence, obj_sequence.sequence):
        raise TypeError, "Cannot fragment non-sequence object!"
    
    # check cyclic peptides
    if sequence.cyclic:
        raise TypeError, 'Direct fragmentation of cyclic peptides is not supported!'
    
    frags = []
    length = len(sequence)
    
    # get serie definition
    serie = blocks.fragments[serie]
    
    # molecular ion
    if serie.terminus == 'M':
        frag = sequence[:]
        frag.fragmentSerie = serie.name
        frags.append(frag)
    
    # N-terminal fragments
    elif serie.terminus == 'N':
        for x in range(length):
            frag = sequence[:x+1]
            frag.fragmentSerie = serie.name
            frag.fragmentIndex = (x+1)
            frag.cTermFormula = serie.cTermFormula
            frags.append(frag)
            
            CHECK_FORCE_QUIT()
    
    # C-terminal fragments
    elif serie.terminus == 'C':
        for x in range(length):
            frag = sequence[length-(x+1):]
            frag.fragmentSerie = serie.name
            frag.fragmentIndex = (x+1)
            frag.nTermFormula = serie.nTermFormula
            frags.append(frag)
            
            CHECK_FORCE_QUIT()
    
    # singlet fragments
    elif serie.terminus == 'S':
        for x in range(length):
            frag = sequence[x:x+1]
            frag.fragmentSerie = serie.name
            frag.fragmentIndex = (x+1)
            frag.nTermFormula = serie.nTermFormula
            frag.cTermFormula = serie.cTermFormula
            frags.append(frag)
            
            CHECK_FORCE_QUIT()
    
    # internal fragments
    elif serie.terminus == 'I':
        for x in range(1,length-1):
            for y in range(2,length-x):
                frag = sequence[x:x+y]
                frag.fragmentSerie = serie.name
                frag.nTermFormula = serie.nTermFormula
                frag.cTermFormula = serie.cTermFormula
                frags.append(frag)
                
                CHECK_FORCE_QUIT()
    
    # correct termini for cyclic peptides
    if cyclicParent:
        for frag in frags:
            if serie.terminus == 'M':
                frag.nTermFormula = ''
                frag.cTermFormula = ''
            elif serie.terminus == 'N':
                frag.nTermFormula = 'H'
            elif serie.terminus == 'C':
                frag.cTermFormula = 'H-1'
    
    # remove nonsense terminal fragments
    if serie.terminus == 'N':
        if frags and serie.nTermFilter:
            del frags[0]
        if frags and serie.cTermFilter:
            del frags[-1]
    elif serie.terminus == 'C':
        if frags and serie.nTermFilter:
            del frags[-1]
        if frags and serie.cTermFilter:
            del frags[0]
    elif serie.terminus == 'S':
        if frags and serie.nTermFilter:
            del frags[0]
        if frags and serie.cTermFilter:
            del frags[-1]
    
    return frags
# ----


def fragmentlosses(fragments, losses=[], defined=False, limit=1, filterIn={}, filterOut={}):
    """Apply specified neutral losses to fragments.
        fragments: (list) list of sequence fragments
        losses: (list) list of neutral losses
        defined: (bool) use monomer-defined neutral losses
        limit: (int) max length of loss combination
        filterIn: (dic) allowed series for specified losses
        filterOut: (dic) not allowed series for specified losses
    """
    
    # make losses combinations
    combinations = []
    for x in range(1, min(len(losses), limit) + 1):
        for c in itertools.combinations(losses, x):
            combinations.append(list(c))
    
    # generate fragments
    buff = []
    for frag in fragments:
        
        CHECK_FORCE_QUIT()
        
        # get monomer-defined losses to check specifity
        definedLosses = []
        for monomer in frag:
            definedLosses += blocks.monomers[monomer].losses
        
        # append new combinations with monomer-defined losses
        lossesToApply = combinations[:]
        if defined:
            for monomer in frag:
                for item in ([[]] + lossesToApply[:]):
                    for loss in blocks.monomers[monomer].losses:
                        newItem = item + [loss]
                        newItem.sort()
                        
                        if not [loss] in lossesToApply:
                            lossesToApply.append([loss])
                        if len(newItem) <= limit and not newItem in lossesToApply:
                            lossesToApply.append(newItem)
        
        # make fragment
        for combination in lossesToApply:
            newFrag = frag.duplicate()
            skip = False
            
            # apply losses
            for loss in combination:
                newFrag.fragmentLosses.append(loss)
                
                # check neutral gains
                if loss in frag.fragmentGains:
                    skip = True
                    break
                
                # check fragment type filter
                if (loss in filterOut and frag.fragmentSerie in filterOut[loss]) \
                    or (loss in filterIn and not frag.fragmentSerie in filterIn[loss]):
                    skip = True
                    break
                
                # check fragment composition
                if not newFrag.isvalid():
                    skip = True
                    break
                
                # filter non-specific losses
                if not loss in definedLosses:
                    newFrag.fragmentFiltered = True
            
            # store fragment
            if not skip:
                buff.append(newFrag)
    
    return buff
# ----


def fragmentgains(fragments, gains=[], filterIn={'H2O':['b'], 'CO':['b', 'c', 'break']}, filterOut={}):
    """Apply specified neutral gains to fragments.
        fragments: (list) list of sequence fragments
        gains: (list) list of neutral gains
        filterIn: (dic) allowed series for specified gains
        filterOut: (dic) not allowed series for specified gains
    """
    
    # generate fragments
    buff = []
    for frag in fragments:
        
        CHECK_FORCE_QUIT()
        
        # is parent cyclic?
        cyclicParent = False
        for item in frag.history:
            if 'break' in item:
                cyclicParent = True
                break
        
        # apply gains
        for gain in gains:
            
            # check neutral losses
            if gain in frag.fragmentLosses:
                continue
            
            # check fragment type filters
            if (gain in filterOut and frag.fragmentSerie in filterOut[gain]) \
                or (gain in filterIn and not frag.fragmentSerie in filterIn[gain]):
                continue
            
            # check break (cyclic parent)
            if gain in filterIn and 'break' in filterIn[gain] and not cyclicParent:
                continue
            
            # make fragment
            newFrag = frag.duplicate()
            newFrag.fragmentGains.append(gain)
            
            # check fragment composition
            if not newFrag.isvalid():
                continue
            
            # store fragment
            buff.append(newFrag)
    
    return buff
# ----


  