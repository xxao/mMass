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
import httplib
import webbrowser
import xml.dom.minidom

# load stopper
from mod_stopper import CHECK_FORCE_QUIT


# MASCOT SEARCH FUNCTIONS
# -----------------------

class mascot():
    """Mascot search module."""
    
    def __init__(self, host, path='/mascot/'):
        
        # server settings
        self.server = {
            'host': host,
            'path': path,
            'search': 'cgi/nph-mascot.exe',
            'result': 'cgi/master_results.pl',
            'export': 'cgi/export_dat_2.pl',
            'params': 'cgi/get_params.pl',
        }
        
        # export settings
        self.export = {
            'do_export': 1,
            'export_format': 'XML',
            'report': 'AUTO',
            
            '_showallfromerrortolerant': 0,
            '_onlyerrortolerant': 0,
            '_noerrortolerant': 0,
            '_show_decoy_report': 0,
            '_sigthreshold': 0.05,
            '_server_mudpit_switch': 0.000000001,
            '_ignoreionsscorebelow': 0,
            '_showsubsets': 0,
            '_requireboldred': 1,
            
            'search_master': 0,
            'show_header': 0,
            'show_mods': 0,
            'show_params': 0,
            'show_format': 0,
            'show_masses': 0,
            'show_same_sets': 0,
            'show_unassigned': 0,
            
            'protein_master': 1,
            'prot_hit_num': 0,
            'prot_acc': 1,
            'prot_score': 1,
            'prot_desc': 1,
            'prot_mass': 1,
            'prot_matches': 1,
            'prot_cover': 1,
            'prot_len': 1,
            'prot_pi': 1,
            'prot_tax_str': 1,
            'prot_tax_id': 1,
            'prot_seq': 1,
            'prot_empai': 1,
            'prot_thresh': 1,
            'prot_expect': 1,
            
            'peptide_master': 1,
            'pep_query': 1,
            'pep_rank': 1,
            'pep_isbold': 1,
            'pep_exp_mz': 1,
            'pep_exp_mr': 1,
            'pep_exp_z': 1,
            'pep_calc_mr': 1,
            'pep_delta': 1,
            'pep_start': 1,
            'pep_end': 1,
            'pep_miss': 1,
            'pep_score': 1,
            'pep_homol': 1,
            'pep_ident': 1,
            'pep_expect': 1,
            'pep_seq': 1,
            'pep_res_before': 1,
            'pep_res_after': 1,
            'pep_frame': 1,
            'pep_var_mod': 1,
            'pep_var_mod_pos': 1,
            'pep_num_match': 1,
            'pep_scan_title': 1,
            
            'query_master': 0,
            'query_title': 0,
            'query_qualifiers': 0,
            'query_params': 0,
            'query_peaks': 0,
            'query_raw': 0,
        }
        
        self.resultsPath = None
        self.resultsXML = None
        self.hits = {}
    # ----
    
    
    def search(self, query):
        """Send MGF query to Mascot server."""
        
        # clear results
        self.resultsPath = None
        self.resultsXML = None
        self.hits = {}
        
        # make body
        boundary = '----------ThIs_Is_tHe_bouNdaRY_$'
        body = '--' + boundary + '\r\n'
        body += 'Content-Disposition: form-data; name="QUE"\r\n\r\n'
        body += query
        body += '\r\n'
        body += '--' + boundary + '--\r\n'
        
        # send data to server
        try:
            conn = httplib.HTTPConnection(self.server['host'])
            conn.putrequest('POST', self.server['path'] + self.server['search'] + '?1')
            conn.putheader('content-type', 'multipart/form-data; boundary=%s' % boundary)
            conn.putheader('content-length', str(len(body)))
            conn.endheaders()
            conn.send(body)
            response = conn.getresponse()
            data = response.read()
            conn.close()
        except:
            return False
        
        # error
        if response.status != 200:
            return False
        
        # get results path
        match = re.search('master_results\.pl\?file=(.*)\"', data)
        if match:
            self.resultsPath = match.group(1)
            return True
        else:
            return False
    # ----
    
    
    def report(self, path=None):
        """View search results in a browser."""
        
        # show user defined path
        if path:
            path = 'http://%s?file="%s"' % (self.server['host'] + self.server['path'] + self.server['result'], path)
            webbrowser.open(path)
        
        # show current results
        elif self.resultsPath:
            path = 'http://%s?file="%s"' % (self.server['host'] + self.server['path'] + self.server['result'], self.resultsPath)
            webbrowser.open(path)
    # ----
    
    
    def fetchall(self, path=None):
        """Get search results in XML format."""
        
        # clear results
        self.resultsXML = None
        self.hits = {}
        
        # set path
        if path:
            path = '%s?file="%s"' % (self.server['path'] + self.server['export'], path)
        elif self.resultsPath:
            path = '%s?file="%s"' % (self.server['path'] + self.server['export'], self.resultsPath)
        else:
            return False
        
        # add export params
        for name, value in self.export.items():
            path += '&%s=%s' % (name, value)
        
        # get data from the server
        try:
            conn = httplib.HTTPConnection(self.server['host'])
            conn.request('GET', path)
            response = conn.getresponse()
            data = response.read()
            conn.close()
        except:
            return False
        
        # error
        if response.status != 200:
            return False
        
        # parse data
        self.resultsXML = data
        status = self.parse()
        
        return status
    # ----
    
    
    def parse(self, data=None, path=None):
        """Get hits from results."""
        
        self.hits = {}
        
        # parse results XML
        try:
            if path:
                self.resultsPath = None
                self.resultsXML = None
                data = xml.dom.minidom.parse(path)
            elif data:
                self.resultsPath = None
                self.resultsXML = None
                data = xml.dom.minidom.parseString(data)
            elif self.resultsXML:
                data = xml.dom.minidom.parseString(self.resultsXML)
            else:
                return False
        except:
            return False
        
        # get all hits
        hitTags = data.getElementsByTagName('hit')
        for hitTag in hitTags:
            hitNumber = int(hitTag.getAttribute('number'))
            
            # get proteins
            proteins = {}
            proteinTags = hitTag.getElementsByTagName('protein')
            for proteinTag in proteinTags:
                protein = {}
                protein['prot_accession'] = proteinTag.getAttribute('accession')
                for tag in proteinTag.childNodes:
                    if tag.nodeType == xml.dom.minidom.Node.ELEMENT_NODE and tag.tagName != 'peptide':
                        protein[tag.tagName] = ''
                        for child in tag.childNodes:
                            protein[tag.tagName] += child.data
                
                # get peptides
                protein['peptides'] = []
                peptideTags = hitTag.getElementsByTagName('peptide')
                for peptideTag in peptideTags:
                    peptide = {}
                    peptide['query'] = peptideTag.getAttribute('query')
                    peptide['rank'] = peptideTag.getAttribute('rank')
                    peptide['isbold'] = peptideTag.getAttribute('isbold')
                    for tag in peptideTag.childNodes:
                        if tag.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                            peptide[tag.tagName] = ''
                            for child in tag.childNodes:
                                peptide[tag.tagName] += child.data
                    
                    # add peptide
                    protein['peptides'].append(peptide)
                
                # add protein
                proteins[protein['prot_accession']] = protein
            
            # add hit
            self.hits[hitNumber] = proteins
        
        return True
    # ----
    
    
    def save(self, path):
        """Save Mascot results XML."""
        
        # check results
        if not self.resultsXML:
            return False
        
        # save file
        try:
            save = file(path, 'w')
            save.write(self.resultsXML.encode("utf-8"))
            save.close()
            return True
        except:
            return False
    # ----
    
    
    def parameters(self):
        """Get form params from the server."""
        
        # get data from the server
        try:
            conn = httplib.HTTPConnection(self.server['host'])
            conn.connect()
            conn.request('GET', self.server['path'] + self.server['params'])
            response = conn.getresponse()
            data = response.read()
            conn.close()
        except:
            return False
        
        # parse parameter file
        params = {
            'DB':[],
            'TAXONOMY':['All entries'],
            'CLE':[],
            'MODS':[],
            'HIDDEN_MODS':[],
            'INSTRUMENT':['Default'],
            'QUANTITATION':['None'],
            'OPTIONS':['None'],
        }
        
        sectionPattern = re.compile('^\[([a-zA-Z_]*)\]$')
        for line in data.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # section header
            if sectionPattern.match(line):
                section = line[1:-1]
                params[section]=[]
            else:
                params[section].append(line)
        
        return params
    # ----
    
    
    