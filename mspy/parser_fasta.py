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
import os.path

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load objects
import obj_sequence


# compile basic patterns
spPattern = re.compile('^(sp\|[A-Z][A-Z0-9]+)\|(.*)')
giPattern = re.compile('^(gi\|[0-9]+[\.0-9]*)\|(.*)')
gbPattern = re.compile('^(gb\|[A-Z]{3}[0-9]{5}[\.0-9]*)\|(.*)')
refPattern = re.compile('^(ref\|[A-Z]{2}_[0-9]+[\.0-9]*)\|(.*)')


# PARSE FASTA SEQUENCE FILE
# -------------------------

class parseFASTA():
    """Parse data from FASTA."""
    
    def __init__(self, path):
        self.path = path
        
        # check path
        if not os.path.exists(path):
            raise IOError, 'File not found! --> ' + self.path
    # ----
    
    
    def sequences(self):
        """Get sequences from document."""
        
        # open document
        try:
            document = file(self.path)
            rawData = document.readlines()
            document.close()
        except IOError:
            return False
        
        # read data
        reading = False
        data = []
        for line in rawData:
            line = line.strip()
            
            # discard comments and empty lines
            if not line or line[0] == ';':
                continue
            
            # new sequence started
            if line[0] == '>':
                
                # store previous sequence
                if reading:
                    try:
                        sequence = obj_sequence.sequence(chain, title=title, accession=accession)
                        data.append(sequence)
                    except:
                        pass
                
                # start new sequence
                title = line[1:]
                accession = ''
                chain = ''
                reading = True
                
                # get accession
                if spPattern.match(title):
                    match = spPattern.match(title)
                    accession = match.group(1)
                    title = match.group(2)
                elif giPattern.match(title):
                    match = giPattern.match(title)
                    accession = match.group(1)
                    title = match.group(2)
                elif gbPattern.match(title):
                    match = gbPattern.match(title)
                    accession = match.group(1)
                    title = match.group(2)
                elif refPattern.match(title):
                    match = refPattern.match(title)
                    accession = match.group(1)
                    title = match.group(2)
            
            # get sequence chain
            elif reading:
                for char in ('\t','\n','\r','\f','\v',' ', '*'):
                    line = line.replace(char, '')
                chain += line.upper()
        
        # store last sequence
        if reading:
            try:
                sequence = obj_sequence.sequence(chain, title=title, accession=accession)
                data.append(sequence)
            except:
                pass
        
        return data
    # ----
    
    
