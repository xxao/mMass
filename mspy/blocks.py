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
import os.path
import xml.dom.minidom

# load objects
import obj_compound

# set default blocks path
blocksdir = '.'


# OBJECT DEFINITIONS
# ------------------

class element:
    """Element object definition.
        name: (str) name
        symbol: (str) symbol
        atomicNumber: (int) atomic number
        isotopes: (dict) dict of isotopes {mass number:(mass, abundance),...}
        valence: (int)
    """
    
    def __init__(self, name, symbol, atomicNumber, isotopes={}, valence=None):
        
        self.name = name
        self.symbol = symbol
        self.atomicNumber = int(atomicNumber)
        self.isotopes = isotopes
        self.valence = valence
        
        # init masses
        massMo = 0
        massAv = 0
        maxAbundance = 0
        for isotop in self.isotopes.values():
            massAv += isotop[0]*isotop[1]
            if maxAbundance < isotop[1]:
                massMo = isotop[0]
                maxAbundance = isotop[1]
        if massMo == 0 or massAv == 0:
            massMo = isotopes[0][0]
            massAv = isotopes[0][0]
        
        self.mass = (massMo, massAv)
    # ----
    


class monomer:
    """Monomer object definition.
        abbr: (str) unique monomer abbreviation
        formula: (str) molecular formula
        losses: (list) list of applicable neutral losses
        name: (str) name
        category: (str) category name
    """
    
    def __init__(self, abbr, formula, losses=[], name='', category=''):
        
        self.abbr = abbr
        self.formula = formula
        self.losses = losses
        self.name = name
        self.category = category
        
        # init masses and composition
        cmpd = obj_compound.compound(self.formula)
        self.composition = cmpd.composition()
        self.mass = cmpd.mass()
        
        # check formulae
        for loss in losses:
            cmpd = obj_compound.compound(loss)
    # ----
    


class enzyme:
    """Enzyme object definition.
        name: (str) name
        expression: (str) regular expression of cleavage site
        nTermFormula: (str) molecular formula for new N-terminus
        cTermFormula: (str) molecular formula for new C-terminus
        modsBefore: (bool) allow modifications before cleavage site
        modsAfter: (bool) allow modifications after cleavage site
    """
    
    def __init__(self, name='', expression='', nTermFormula='', cTermFormula='', modsBefore=True, modsAfter=True):
        
        self.name = name
        self.expression = expression
        self.nTermFormula = nTermFormula
        self.cTermFormula = cTermFormula
        self.modsBefore = modsBefore
        self.modsAfter = modsAfter
        
        # check formulae
        cmpd = obj_compound.compound(nTermFormula)
        cmpd = obj_compound.compound(cTermFormula)
    # ----
    


class fragment:
    """Peptide ion fragment object definition.
        name: (str) name
        teminus: (M or N or C on S or I) fragment type (M-molecular ion, N-terminal, C-terminal, I-internal, S-single amino)
        nTermFormula: (str) molecular formula of N-terminal gain or loss
        cTermFormula: (str) molecular formula of C-terminal gain or loss
        nTermFilter: (bool) filter N-terminal fragment
        cTermFilter: (bool) filter C-terminal fragment
    """
    
    def __init__(self, name='', terminus='', nTermFormula='', cTermFormula='', nTermFilter=False, cTermFilter=False):
        
        self.name = name
        self.terminus = terminus
        self.nTermFormula = nTermFormula
        self.cTermFormula = cTermFormula
        self.nTermFilter = nTermFilter
        self.cTermFilter = cTermFilter
        
        # check formulae
        cmpd = obj_compound.compound(nTermFormula)
        cmpd = obj_compound.compound(cTermFormula)
    # ----
    


class modification:
    """Modification object definition.
        name: (str) name
        gainFormula: (str) gain molecular formula
        lossFormula: (str) loss molecular formula
        aminoSpecifity: (str) specific amino acids which can be modified
        termSpecifity: (N or C) can modify N or C terminal amino acid
        description: (str) description
    """
    
    def __init__(self, name='', gainFormula='', lossFormula='', aminoSpecifity='', termSpecifity='', description=''):
        
        self.name = name
        self.gainFormula = gainFormula
        self.lossFormula = lossFormula
        self.aminoSpecifity = aminoSpecifity
        self.termSpecifity = termSpecifity
        self.description = description
        
        # init masses and composition
        lossCmpd = obj_compound.compound(self.lossFormula)
        lossComposition = lossCmpd.composition()
        
        formula = self.gainFormula
        for el, count in lossComposition.items():
            formula += '%s%d' % (el, -1*count)
        
        cmpd = obj_compound.compound(formula)
        self.composition = cmpd.composition()
        self.mass = cmpd.mass()
    # ----
    



# DEFAULT BLOCKS
# --------------

elements = {
    'Ac': element( name='Actinium', symbol='Ac', atomicNumber=89, isotopes={227: (227.02774700000001, 1.0)}, valence=3),
    'Ag': element( name='Silver', symbol='Ag', atomicNumber=47, isotopes={107: (106.90509299999999, 0.51839000000000002), 109: (108.90475600000001, 0.48160999999999998)}, valence=1),
    'Al': element( name='Aluminium', symbol='Al', atomicNumber=13, isotopes={27: (26.981538440000001, 1.0)}, valence=3),
    'Am': element( name='Americium', symbol='Am', atomicNumber=95, isotopes={241: (241.05682289999999, 0.0), 243: (243.06137269999999, 1.0)}, valence=3),
    'Ar': element( name='Argon', symbol='Ar', atomicNumber=18, isotopes={40: (39.962383123000002, 0.99600299999999997), 36: (35.967546280000001, 0.0033649999999999999), 38: (37.962732199999998, 0.00063199999999999997)}, valence=0),
    'As': element( name='Arsenic', symbol='As', atomicNumber=33, isotopes={75: (74.921596399999999, 1.0)}, valence=3),
    'At': element( name='Astatine', symbol='At', atomicNumber=85, isotopes={210: (209.98713100000001, 0.0), 211: (210.987481, 1.0)}, valence=1),
    'Au': element( name='Gold', symbol='Au', atomicNumber=79, isotopes={197: (196.96655200000001, 1.0)}, valence=1),
    'B': element( name='Boron', symbol='B', atomicNumber=5, isotopes={10: (10.012937000000001, 0.19900000000000001), 11: (11.0093055, 0.80100000000000005)}, valence=3),
    'Ba': element( name='Barium', symbol='Ba', atomicNumber=56, isotopes={130: (129.90630999999999, 0.00106), 132: (131.905056, 0.00101), 134: (133.90450300000001, 0.024170000000000001), 135: (134.90568300000001, 0.065920000000000006), 136: (135.90457000000001, 0.078539999999999999), 137: (136.905821, 0.11232), 138: (137.90524099999999, 0.71697999999999995)}, valence=2),
    'Be': element( name='Beryllium', symbol='Be', atomicNumber=4, isotopes={9: (9.0121821000000004, 1.0)}, valence=2),
    'Bh': element( name='Bohrium', symbol='Bh', atomicNumber=107, isotopes={264: (264.12473, 1.0)}, valence=0),
    'Bi': element( name='Bismuth', symbol='Bi', atomicNumber=83, isotopes={209: (208.98038299999999, 1.0)}, valence=5),
    'Bk': element( name='Berkelium', symbol='Bk', atomicNumber=97, isotopes={249: (249.07498000000001, 0.0), 247: (247.07029900000001, 1.0)}, valence=3),
    'Br': element( name='Bromine', symbol='Br', atomicNumber=35, isotopes={81: (80.916291000000001, 0.49309999999999998), 79: (78.918337600000001, 0.50690000000000002)}, valence=1),
    'C': element( name='Carbon', symbol='C', atomicNumber=6, isotopes={12: (12.0, 0.98929999999999996), 13: (13.0033548378, 0.010699999999999999), 14: (14.003241987999999, 0.0)}, valence=4),
    'Ca': element( name='Calcium', symbol='Ca', atomicNumber=20, isotopes={40: (39.962591199999999, 0.96940999999999999), 42: (41.958618299999998, 0.0064700000000000001), 43: (42.958766799999999, 0.0013500000000000001), 44: (43.9554811, 0.02086), 46: (45.953692799999999, 4.0000000000000003e-05), 48: (47.952534, 0.0018699999999999999)}, valence=2),
    'Cd': element( name='Cadmium', symbol='Cd', atomicNumber=48, isotopes={106: (105.906458, 0.012500000000000001), 108: (107.904183, 0.0088999999999999999), 110: (109.903006, 0.1249), 111: (110.90418200000001, 0.128), 112: (111.9027572, 0.24129999999999999), 113: (112.9044009, 0.1222), 114: (113.90335810000001, 0.2873), 116: (115.90475499999999, 0.074899999999999994)}, valence=2),
    'Ce': element( name='Cerium', symbol='Ce', atomicNumber=58, isotopes={136: (135.90714, 0.0018500000000000001), 138: (137.90598600000001, 0.0025100000000000001), 140: (139.90543400000001, 0.88449999999999995), 142: (141.90924000000001, 0.11114)}, valence=4),
    'Cf': element( name='Californium', symbol='Cf', atomicNumber=98, isotopes={249: (249.07484700000001, 0.0), 250: (250.07640000000001, 0.0), 251: (251.07957999999999, 1.0), 252: (252.08161999999999, 0.0)}, valence=3),
    'Cl': element( name='Chlorine', symbol='Cl', atomicNumber=17, isotopes={35: (34.96885271, 0.75780000000000003), 37: (36.9659026, 0.2422)}, valence=1),
    'Cm': element( name='Curium', symbol='Cm', atomicNumber=96, isotopes={243: (243.0613822, 0.0), 244: (244.06274629999999, 0.0), 245: (245.06548559999999, 0.0), 246: (246.06721759999999, 0.0), 247: (247.070347, 1.0), 248: (248.07234199999999, 0.0)}, valence=3),
    'Co': element( name='Cobalt', symbol='Co', atomicNumber=27, isotopes={59: (58.933200200000002, 1.0)}, valence=2),
    'Cr': element( name='Chromium', symbol='Cr', atomicNumber=24, isotopes={50: (49.946049600000002, 0.043450000000000003), 52: (51.940511899999997, 0.83789000000000002), 53: (52.9406538, 0.095009999999999997), 54: (53.938884899999998, 0.023650000000000001)}, valence=3),
    'Cs': element( name='Caesium', symbol='Cs', atomicNumber=55, isotopes={133: (132.90544700000001, 1.0)}, valence=1),
    'Cu': element( name='Copper', symbol='Cu', atomicNumber=29, isotopes={65: (64.927793699999995, 0.30830000000000002), 63: (62.929601099999999, 0.69169999999999998)}, valence=1),
    'Db': element( name='Dubnium', symbol='Db', atomicNumber=105, isotopes={262: (262.11415, 1.0)}, valence=0),
    'Dy': element( name='Dysprosium', symbol='Dy', atomicNumber=66, isotopes={160: (159.925194, 0.023400000000000001), 161: (160.92693, 0.18909999999999999), 162: (161.926795, 0.25509999999999999), 163: (162.92872800000001, 0.249), 164: (163.929171, 0.28179999999999999), 156: (155.92427799999999, 0.00059999999999999995), 158: (157.92440500000001, 0.001)}, valence=3),
    'Er': element( name='Erbium', symbol='Er', atomicNumber=68, isotopes={162: (161.928775, 0.0014), 164: (163.92919699999999, 0.0161), 166: (165.93029000000001, 0.33610000000000001), 167: (166.93204499999999, 0.2293), 168: (167.932368, 0.26779999999999998), 170: (169.93546000000001, 0.14929999999999999)}, valence=3),
    'Es': element( name='Einsteinium', symbol='Es', atomicNumber=99, isotopes={252: (252.08296999999999, 1.0)}, valence=3),
    'Eu': element( name='Europium', symbol='Eu', atomicNumber=63, isotopes={153: (152.92122599999999, 0.52190000000000003), 151: (150.91984600000001, 0.47810000000000002)}, valence=2),
    'F': element( name='Fluorine', symbol='F', atomicNumber=9, isotopes={19: (18.998403199999998, 1.0)}, valence=1),
    'Fe': element( name='Iron', symbol='Fe', atomicNumber=26, isotopes={56: (55.934942100000001, 0.91754000000000002), 57: (56.9353987, 0.021190000000000001), 58: (57.933280500000002, 0.00282), 54: (53.939614800000001, 0.058450000000000002)}, valence=2),
    'Fm': element( name='Fermium', symbol='Fm', atomicNumber=100, isotopes={257: (257.095099, 1.0)}, valence=3),
    'Fr': element( name='Francium', symbol='Fr', atomicNumber=87, isotopes={223: (223.0197307, 1.0)}, valence=1),
    'Ga': element( name='Gallium', symbol='Ga', atomicNumber=31, isotopes={69: (68.925580999999994, 0.60107999999999995), 71: (70.924705000000003, 0.39892)}, valence=3),
    'Gd': element( name='Gadolinium', symbol='Gd', atomicNumber=64, isotopes={160: (159.92705100000001, 0.21859999999999999), 152: (151.91978800000001, 0.002), 154: (153.920862, 0.0218), 155: (154.922619, 0.14799999999999999), 156: (155.92212000000001, 0.20469999999999999), 157: (156.923957, 0.1565), 158: (157.92410100000001, 0.24840000000000001)}, valence=3),
    'Ge': element( name='Germanium', symbol='Ge', atomicNumber=32, isotopes={72: (71.922076200000006, 0.27539999999999998), 73: (72.923459399999999, 0.077299999999999994), 74: (73.9211782, 0.36280000000000001), 76: (75.921402700000002, 0.076100000000000001), 70: (69.924250400000005, 0.2084)}, valence=4),
    'H': element( name='Hydrogen', symbol='H', atomicNumber=1, isotopes={1: (1.0078250321, 0.99988500000000002), 2: (2.0141017780000001, 0.000115), 3: (3.0160492675000001, 0.0)}, valence=1),
    'He': element( name='Helium', symbol='He', atomicNumber=2, isotopes={3: (3.0160293096999999, 1.37e-06), 4: (4.0026032496999999, 0.99999863)}, valence=0),
    'Hf': element( name='Hafnium', symbol='Hf', atomicNumber=72, isotopes={174: (173.94004000000001, 0.0016000000000000001), 176: (175.94140179999999, 0.052600000000000001), 177: (176.94322, 0.186), 178: (177.9436977, 0.27279999999999999), 179: (178.9458151, 0.13619999999999999), 180: (179.94654879999999, 0.3508)}, valence=4),
    'Hg': element( name='Mercury', symbol='Hg', atomicNumber=80, isotopes={196: (195.96581499999999, 0.0015), 198: (197.96675200000001, 0.099699999999999997), 199: (198.96826200000001, 0.16869999999999999), 200: (199.968309, 0.23100000000000001), 201: (200.97028499999999, 0.1318), 202: (201.97062600000001, 0.29859999999999998), 204: (203.97347600000001, 0.068699999999999997)}, valence=2),
    'Ho': element( name='Holmium', symbol='Ho', atomicNumber=67, isotopes={165: (164.930319, 1.0)}, valence=3),
    'I': element( name='Iodine', symbol='I', atomicNumber=53, isotopes={127: (126.90446799999999, 1.0)}, valence=1),
    'In': element( name='Indium', symbol='In', atomicNumber=49, isotopes={113: (112.904061, 0.042900000000000001), 115: (114.90387800000001, 0.95709999999999995)}, valence=3),
    'Ir': element( name='Iridium', symbol='Ir', atomicNumber=77, isotopes={193: (192.96292399999999, 0.627), 191: (190.96059099999999, 0.373)}, valence=3),
    'K': element( name='Potassium', symbol='K', atomicNumber=19, isotopes={40: (39.963998670000002, 0.000117), 41: (40.96182597, 0.067302000000000001), 39: (38.963706899999998, 0.93258099999999999)}, valence=1),
    'Kr': element( name='Krypton', symbol='Kr', atomicNumber=36, isotopes={78: (77.920385999999993, 0.0035000000000000001), 80: (79.916377999999995, 0.022800000000000001), 82: (81.913484600000004, 0.1158), 83: (82.914135999999999, 0.1149), 84: (83.911507, 0.56999999999999995), 86: (85.910610300000002, 0.17299999999999999)}, valence=0),
    'La': element( name='Lanthanum', symbol='La', atomicNumber=57, isotopes={138: (137.907107, 0.00089999999999999998), 139: (138.90634800000001, 0.99909999999999999)}, valence=3),
    'Li': element( name='Lithium', symbol='Li', atomicNumber=3, isotopes={6: (6.0151222999999998, 0.075899999999999995), 7: (7.0160039999999997, 0.92410000000000003)}, valence=1),
    'Lr': element( name='Lawrencium', symbol='Lr', atomicNumber=103, isotopes={262: (262.10969, 1.0)}, valence=3),
    'Lu': element( name='Lutetium', symbol='Lu', atomicNumber=71, isotopes={176: (175.9426824, 0.025899999999999999), 175: (174.9407679, 0.97409999999999997)}, valence=3),
    'Md': element( name='Mendelevium', symbol='Md', atomicNumber=101, isotopes={256: (256.09404999999998, 0.0), 258: (258.09842500000002, 1.0)}, valence=3),
    'Mg': element( name='Magnesium', symbol='Mg', atomicNumber=12, isotopes={24: (23.985041899999999, 0.78990000000000005), 25: (24.985837020000002, 0.10000000000000001), 26: (25.982593040000001, 0.1101)}, valence=2),
    'Mn': element( name='Manganese', symbol='Mn', atomicNumber=25, isotopes={55: (54.938049599999999, 1.0)}, valence=2),
    'Mo': element( name='Molybdenum', symbol='Mo', atomicNumber=42, isotopes={96: (95.904678899999993, 0.1668), 97: (96.906020999999996, 0.095500000000000002), 98: (97.905407800000006, 0.24129999999999999), 100: (99.907477, 0.096299999999999997), 92: (91.906809999999993, 0.1484), 94: (93.905087600000002, 0.092499999999999999), 95: (94.905841499999994, 0.15920000000000001)}, valence=6),
    'Mt': element( name='Meitnerium', symbol='Mt', atomicNumber=109, isotopes={268: (268.13882000000001, 1.0)}, valence=0),
    'N': element( name='Nitrogen', symbol='N', atomicNumber=7, isotopes={14: (14.0030740052, 0.99631999999999998), 15: (15.000108898400001, 0.0036800000000000001)}, valence=3),
    'Na': element( name='Sodium', symbol='Na', atomicNumber=11, isotopes={23: (22.989769670000001, 1.0)}, valence=1),
    'Nb': element( name='Niobium', symbol='Nb', atomicNumber=41, isotopes={93: (92.906377500000005, 1.0)}, valence=5),
    'Nd': element( name='Neodymium', symbol='Nd', atomicNumber=60, isotopes={142: (141.90771899999999, 0.27200000000000002), 143: (142.90980999999999, 0.122), 144: (143.91008299999999, 0.23799999999999999), 145: (144.91256899999999, 0.083000000000000004), 146: (145.91311200000001, 0.17199999999999999), 148: (147.916889, 0.057000000000000002), 150: (149.92088699999999, 0.056000000000000001)}, valence=3),
    'Ne': element( name='Neon', symbol='Ne', atomicNumber=10, isotopes={20: (19.992440175900001, 0.90480000000000005), 21: (20.993846739999999, 0.0027000000000000001), 22: (21.991385510000001, 0.092499999999999999)}, valence=0),
    'Ni': element( name='Nickel', symbol='Ni', atomicNumber=28, isotopes={64: (63.927969599999997, 0.0092560000000000003), 58: (57.935347899999996, 0.68076899999999996), 60: (59.930790600000002, 0.26223099999999999), 61: (60.9310604, 0.011398999999999999), 62: (61.928348800000002, 0.036345000000000002)}, valence=2),
    'No': element( name='Nobelium', symbol='No', atomicNumber=102, isotopes={259: (259.10102000000001, 1.0)}, valence=2),
    'Np': element( name='Neptunium', symbol='Np', atomicNumber=93, isotopes={237: (237.04816729999999, 1.0), 239: (239.05293140000001, 0.0)}, valence=3),
    'O': element( name='Oxygen', symbol='O', atomicNumber=8, isotopes={16: (15.9949146221, 0.99756999999999996), 17: (16.999131500000001, 0.00038000000000000002), 18: (17.999160400000001, 0.0020500000000000002)}, valence=2),
    'Os': element( name='Osmium', symbol='Os', atomicNumber=76, isotopes={192: (191.961479, 0.4078), 184: (183.95249100000001, 0.00020000000000000001), 186: (185.95383799999999, 0.015900000000000001), 187: (186.95574790000001, 0.019599999999999999), 188: (187.95583600000001, 0.13239999999999999), 189: (188.95814490000001, 0.1615), 190: (189.95844500000001, 0.2626)}, valence=3),
    'P': element( name='Phosphorus', symbol='P', atomicNumber=15, isotopes={31: (30.973761509999999, 1.0)}, valence=3),
    'Pa': element( name='Protactinium', symbol='Pa', atomicNumber=91, isotopes={231: (231.0358789, 1.0)}, valence=4),
    'Pb': element( name='Lead', symbol='Pb', atomicNumber=82, isotopes={208: (207.97663600000001, 0.52400000000000002), 204: (203.973029, 0.014), 206: (205.97444899999999, 0.24099999999999999), 207: (206.97588099999999, 0.221)}, valence=4),
    'Pd': element( name='Palladium', symbol='Pd', atomicNumber=46, isotopes={102: (101.905608, 0.010200000000000001), 104: (103.90403499999999, 0.1114), 105: (104.905084, 0.2233), 106: (105.90348299999999, 0.27329999999999999), 108: (107.90389399999999, 0.2646), 110: (109.905152, 0.1172)}, valence=2),
    'Pm': element( name='Promethium', symbol='Pm', atomicNumber=61, isotopes={145: (144.912744, 1.0), 147: (146.91513399999999, 0.0)}, valence=3),
    'Po': element( name='Polonium', symbol='Po', atomicNumber=84, isotopes={209: (208.982416, 1.0), 210: (209.982857, 0.0)}, valence=2),
    'Pr': element( name='Praseodymium', symbol='Pr', atomicNumber=59, isotopes={141: (140.90764799999999, 1.0)}, valence=3),
    'Pt': element( name='Platinum', symbol='Pt', atomicNumber=78, isotopes={192: (191.96103500000001, 0.0078200000000000006), 194: (193.96266399999999, 0.32967000000000002), 195: (194.96477400000001, 0.33832000000000001), 196: (195.964935, 0.25241999999999998), 198: (197.96787599999999, 0.071629999999999999), 190: (189.95993000000001, 0.00013999999999999999)}, valence=2),
    'Pu': element( name='Plutonium', symbol='Pu', atomicNumber=94, isotopes={238: (238.04955340000001, 0.0), 239: (239.0521565, 0.0), 240: (240.0538075, 0.0), 241: (241.05684529999999, 0.0), 242: (242.05873679999999, 0.0), 244: (244.064198, 1.0)}, valence=3),
    'Ra': element( name='Radium', symbol='Ra', atomicNumber=88, isotopes={224: (224.02020200000001, 0.0), 226: (226.02540260000001, 1.0), 228: (228.03106410000001, 0.0), 223: (223.018497, 0.0)}, valence=2),
    'Rb': element( name='Rubidium', symbol='Rb', atomicNumber=37, isotopes={85: (84.911789299999995, 0.72170000000000001), 87: (86.909183499999997, 0.27829999999999999)}, valence=1),
    'Re': element( name='Rhenium', symbol='Re', atomicNumber=75, isotopes={185: (184.95295569999999, 0.374), 187: (186.9557508, 0.626)}, valence=4),
    'Rf': element( name='Rutherfordium', symbol='Rf', atomicNumber=104, isotopes={261: (261.10874999999999, 1.0)}, valence=0),
    'Rh': element( name='Rhodium', symbol='Rh', atomicNumber=45, isotopes={103: (102.90550399999999, 1.0)}, valence=3),
    'Rn': element( name='Radon', symbol='Rn', atomicNumber=86, isotopes={211: (210.99058500000001, 0.0), 220: (220.01138409999999, 0.0), 222: (222.01757050000001, 1.0)}, valence=0),
    'Ru': element( name='Ruthenium', symbol='Ru', atomicNumber=44, isotopes={96: (95.907597999999993, 0.055399999999999998), 98: (97.905287000000001, 0.018700000000000001), 99: (98.9059393, 0.12759999999999999), 100: (99.904219699999999, 0.126), 101: (100.9055822, 0.1706), 102: (101.9043495, 0.3155), 104: (103.90543, 0.1862)}, valence=3),
    'S': element( name='Sulfur', symbol='S', atomicNumber=16, isotopes={32: (31.972070689999999, 0.94930000000000003), 33: (32.971458499999997, 0.0076), 34: (33.967866829999998, 0.042900000000000001), 36: (35.967080879999997, 0.00020000000000000001)}, valence=2),
    'Sb': element( name='Antimony', symbol='Sb', atomicNumber=51, isotopes={121: (120.903818, 0.57210000000000005), 123: (122.90421569999999, 0.4279)}, valence=5),
    'Sc': element( name='Scandium', symbol='Sc', atomicNumber=21, isotopes={45: (44.955910199999998, 1.0)}, valence=3),
    'Se': element( name='Selenium', symbol='Se', atomicNumber=34, isotopes={74: (73.922476599999996, 0.0088999999999999999), 76: (75.919214100000005, 0.093700000000000006), 77: (76.919914599999998, 0.076300000000000007), 78: (77.917309500000002, 0.23769999999999999), 80: (79.916521799999998, 0.49609999999999999), 82: (81.916700000000006, 0.087300000000000003)}, valence=2),
    'Sg': element( name='Seaborgium', symbol='Sg', atomicNumber=106, isotopes={266: (266.12193000000002, 1.0)}, valence=0),
    'Si': element( name='Silicon', symbol='Si', atomicNumber=14, isotopes={28: (27.976926532699999, 0.92229700000000003), 29: (28.976494720000002, 0.046831999999999999), 30: (29.973770219999999, 0.030872)}, valence=4),
    'Sm': element( name='Samarium', symbol='Sm', atomicNumber=62, isotopes={144: (143.91199499999999, 0.030700000000000002), 147: (146.91489300000001, 0.14990000000000001), 148: (147.914818, 0.1124), 149: (148.91718, 0.13819999999999999), 150: (149.917271, 0.073800000000000004), 152: (151.91972799999999, 0.26750000000000002), 154: (153.92220499999999, 0.22750000000000001)}, valence=2),
    'Sn': element( name='Tin', symbol='Sn', atomicNumber=50, isotopes={112: (111.904821, 0.0097000000000000003), 114: (113.902782, 0.0066), 115: (114.903346, 0.0033999999999999998), 116: (115.90174399999999, 0.1454), 117: (116.90295399999999, 0.076799999999999993), 118: (117.901606, 0.2422), 119: (118.90330899999999, 0.085900000000000004), 120: (119.9021966, 0.32579999999999998), 122: (121.9034401, 0.046300000000000001), 124: (123.9052746, 0.0579)}, valence=4),
    'Sr': element( name='Strontium', symbol='Sr', atomicNumber=38, isotopes={88: (87.905614299999996, 0.82579999999999998), 84: (83.913425000000004, 0.0055999999999999999), 86: (85.909262400000003, 0.098599999999999993), 87: (86.908879299999995, 0.070000000000000007)}, valence=2),
    'Ta': element( name='Tantalum', symbol='Ta', atomicNumber=73, isotopes={180: (179.94746599999999, 0.00012), 181: (180.94799599999999, 0.99987999999999999)}, valence=5),
    'Tb': element( name='Terbium', symbol='Tb', atomicNumber=65, isotopes={159: (158.925343, 1.0)}, valence=3),
    'Tc': element( name='Technetium', symbol='Tc', atomicNumber=43, isotopes={97: (96.906364999999994, 0.0), 98: (97.907216000000005, 1.0), 99: (98.906254599999997, 0.0)}, valence=4),
    'Te': element( name='Tellurium', symbol='Te', atomicNumber=52, isotopes={128: (127.9044614, 0.31740000000000002), 130: (129.90622279999999, 0.34079999999999999), 120: (119.90402, 0.00089999999999999998), 122: (121.90304709999999, 0.025499999999999998), 123: (122.904273, 0.0088999999999999999), 124: (123.90281950000001, 0.047399999999999998), 125: (124.90442470000001, 0.070699999999999999), 126: (125.9033055, 0.18840000000000001)}, valence=2),
    'Th': element( name='Thorium', symbol='Th', atomicNumber=90, isotopes={232: (232.0380504, 1.0), 230: (230.0331266, 2.3203809999999998)}, valence=4),
    'Ti': element( name='Titanium', symbol='Ti', atomicNumber=22, isotopes={48: (47.9479471, 0.73719999999999997), 49: (48.947870799999997, 0.054100000000000002), 50: (49.944792100000001, 0.051799999999999999), 46: (45.9526295, 0.082500000000000004), 47: (46.951763800000002, 0.074399999999999994)}, valence=4),
    'Tl': element( name='Thallium', symbol='Tl', atomicNumber=81, isotopes={203: (202.972329, 0.29524), 205: (204.974412, 0.70476000000000005)}, valence=3),
    'Tm': element( name='Thulium', symbol='Tm', atomicNumber=69, isotopes={169: (168.934211, 1.0)}, valence=3),
    'U': element( name='Uranium', symbol='U', atomicNumber=92, isotopes={233: (233.03962799999999, 2.3802891000000002), 234: (234.04094559999999, 5.5000000000000002e-05), 235: (235.0439231, 0.0071999999999999998), 236: (236.0455619, 0.0), 238: (238.05078259999999, 0.99274499999999999)}, valence=3),
    'V': element( name='Vanadium', symbol='V', atomicNumber=23, isotopes={50: (49.947162800000001, 0.0025000000000000001), 51: (50.943963699999998, 0.99750000000000005)}, valence=5),
    'W': element( name='Tungsten', symbol='W', atomicNumber=74, isotopes={184: (183.95093259999999, 0.30640000000000001), 186: (185.954362, 0.2843), 180: (179.94670600000001, 0.0011999999999999999), 182: (181.948206, 0.26500000000000001), 183: (182.95022449999999, 0.1431)}, valence=6),
    'Xe': element( name='Xenon', symbol='Xe', atomicNumber=54, isotopes={128: (127.90353039999999, 0.019199999999999998), 129: (128.90477949999999, 0.26440000000000002), 130: (129.90350789999999, 0.040800000000000003), 131: (130.9050819, 0.21179999999999999), 132: (131.9041545, 0.26889999999999997), 134: (133.9053945, 0.10440000000000001), 136: (135.90722, 0.088700000000000001), 124: (123.9058958, 0.00089999999999999998), 126: (125.904269, 0.00089999999999999998)}, valence=0),
    'Y': element( name='Yttrium', symbol='Y', atomicNumber=39, isotopes={89: (88.905847899999998, 1.0)}, valence=3),
    'Yb': element( name='Ytterbium', symbol='Yb', atomicNumber=70, isotopes={168: (167.93389400000001, 0.0012999999999999999), 170: (169.93475900000001, 0.0304), 171: (170.93632199999999, 0.14280000000000001), 172: (171.93637770000001, 0.21829999999999999), 173: (172.93820679999999, 0.1613), 174: (173.9388581, 0.31830000000000003), 176: (175.94256799999999, 0.12759999999999999)}, valence=2),
    'Zn': element( name='Zinc', symbol='Zn', atomicNumber=30, isotopes={64: (63.929146600000003, 0.48630000000000001), 66: (65.926036800000006, 0.27900000000000003), 67: (66.927130899999995, 0.041000000000000002), 68: (67.924847600000007, 0.1875), 70: (69.925325000000001, 0.0061999999999999998)}, valence=2),
    'Zr': element( name='Zirconium', symbol='Zr', atomicNumber=40, isotopes={96: (95.908276000000001, 0.028000000000000001), 90: (89.904703699999999, 0.51449999999999996), 91: (90.905645000000007, 0.11219999999999999), 92: (91.905040099999994, 0.17150000000000001), 94: (93.906315800000002, 0.17380000000000001)}, valence=4),
}

monomers = {
    
    # regular amino acids for protein and peptide sequences
    'A': monomer( abbr='A', name='Alanine', formula='C3H5NO', category='_InternalAA'),
    'C': monomer( abbr='C', name='Cysteine', formula='C3H5NOS', category='_InternalAA'),
    'D': monomer( abbr='D', name='Aspartic Acid', formula='C4H5NO3', losses=['H2O'], category='_InternalAA'),
    'E': monomer( abbr='E', name='Glutamic Acid', formula='C5H7NO3', losses=['H2O'], category='_InternalAA'),
    'F': monomer( abbr='F', name='Phenylalanine', formula='C9H9NO', category='_InternalAA'),
    'G': monomer( abbr='G', name='Glycine', formula='C2H3NO', category='_InternalAA'),
    'H': monomer( abbr='H', name='Histidine', formula='C6H7N3O', category='_InternalAA'),
    'I': monomer( abbr='I', name='Isoleucine', formula='C6H11NO', category='_InternalAA'),
    'K': monomer( abbr='K', name='Lysine', formula='C6H12N2O', losses=['NH3'], category='_InternalAA'),
    'L': monomer( abbr='L', name='Leucine', formula='C6H11NO', category='_InternalAA'),
    'M': monomer( abbr='M', name='Methionine', formula='C5H9NSO', category='_InternalAA'),
    'N': monomer( abbr='N', name='Asparagine', formula='C4H6O2N2', losses=['NH3'], category='_InternalAA'),
    'O': monomer( abbr='O', name='Ornithine', formula='C5H10N2O', category='_InternalAA'),
    'P': monomer( abbr='P', name='Proline', formula='C5H7NO', category='_InternalAA'),
    'Q': monomer( abbr='Q', name='Glutamine', formula='C5H8N2O2', losses=['NH3'], category='_InternalAA'),
    'R': monomer( abbr='R', name='Arginine', formula='C6H12N4O', losses=['NH3'], category='_InternalAA'),
    'S': monomer( abbr='S', name='Serine', formula='C3H5NO2', losses=['H2O','H3PO4'], category='_InternalAA'),
    'T': monomer( abbr='T', name='Threonine', formula='C4H7NO2', losses=['H2O','H3PO4'], category='_InternalAA'),
    'V': monomer( abbr='V', name='Valine', formula='C5H9NO', category='_InternalAA'),
    'W': monomer( abbr='W', name='Tryptophan', formula='C11H10N2O', category='_InternalAA'),
    'Y': monomer( abbr='Y', name='Tyrosine', formula='C9H9NO2', losses=['H3PO4'], category='_InternalAA'),
}

enzymes = {
    'Arg-C': enzyme( name='Arg-C', expression='[R][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Asp-N': enzyme( name='Asp-N', expression='[A-Z][D]', nTermFormula='H', cTermFormula='OH', modsBefore=True, modsAfter=False),
    'Bromelain': enzyme( name='Bromelain', expression='[KAY][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'CNBr-HSerLac': enzyme( name='CNBr-HSerLac', expression='[M][A-Z]', nTermFormula='H', cTermFormula='O-1C-1H-3', modsBefore=False, modsAfter=True),
    'Cathepsin B': enzyme( name='Cathepsin B', expression='[R][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Cathepsin D': enzyme( name='Cathepsin D', expression='[LF][^VAG]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Cathepsin G': enzyme( name='Cathepsin G', expression='[YWF][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Chymotrypsin': enzyme( name='Chymotrypsin', expression='[YWFL][^P]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Clostripain': enzyme( name='Clostripain', expression='[R][^P]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Elastase': enzyme( name='Elastase', expression='[AVLIGS][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Glu-C Bic': enzyme( name='Glu-C Bic', expression='[E][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Glu-C Phos': enzyme( name='Glu-C Phos', expression='[ED][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Hydroxylamine': enzyme( name='Hydroxylamine', expression='[N][G]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=False),
    'Lys-C': enzyme( name='Lys-C', expression='[K][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Lys-N': enzyme( name='Lys-N', expression='[A-Z][K]', nTermFormula='H', cTermFormula='OH', modsBefore=True, modsAfter=False),
    'Non-Specific': enzyme( name='Non-Specific', expression='[A-Z][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=True, modsAfter=True),
    'Papain': enzyme( name='Papain', expression='[RK][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Pepsin': enzyme( name='Pepsin', expression='[LF][^VAG]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Proteinase K': enzyme( name='Proteinase K', expression='[YWF][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Subtilisin': enzyme( name='Subtilisin', expression='[^RHK][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Thermolysin': enzyme( name='Thermolysin', expression='[A-Z][LFIVMA]', nTermFormula='H', cTermFormula='OH', modsBefore=True, modsAfter=False),
    'TrypAspN': enzyme( name='TrypAspN', expression='(([KR][^P])|([A-Z][D]))', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=False),
    'TrypChymo': enzyme( name='TrypChymo', expression='[FYWLKR][^P]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Trypsin': enzyme( name='Trypsin', expression='[KR][^P]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
    'Trypsin/P': enzyme( name='Trypsin/P', expression='[KR][A-Z]', nTermFormula='H', cTermFormula='OH', modsBefore=False, modsAfter=True),
}

fragments = {
    'M': fragment( name='M', terminus='M', nTermFilter=False, cTermFilter=False),
    'im': fragment( name='im', terminus='S', nTermFormula='H', cTermFormula='C-1O-1H-1', nTermFilter=False, cTermFilter=False),
    'a': fragment( name='a', terminus='N', cTermFormula='C-1O-1H-1', nTermFilter=True, cTermFilter=True),
    'b': fragment( name='b', terminus='N', cTermFormula='H-1', nTermFilter=True, cTermFilter=True),
    'c': fragment( name='c', terminus='N', cTermFormula='NH2', nTermFilter=False, cTermFilter=True),
    'x': fragment( name='x', terminus='C', nTermFormula='COH-1', nTermFilter=True, cTermFilter=False),
    'y': fragment( name='y', terminus='C', nTermFormula='H', nTermFilter=True, cTermFilter=False),
    'z': fragment( name='z', terminus='C', nTermFormula='N-1H-2', nTermFilter=True, cTermFilter=False),
    'c-ladder': fragment( name='c-ladder', terminus='N', cTermFormula='OH', nTermFilter=True, cTermFilter=True),
    'n-ladder': fragment( name='n-ladder', terminus='C', nTermFormula='H', nTermFilter=True, cTermFilter=False),
    'int-b': fragment( name='int-b', terminus='I', nTermFormula='H', cTermFormula='H-1'),
    'int-a': fragment( name='int-a', terminus='I', nTermFormula='H', cTermFormula='C-1O-1H-1'),
}

modifications = {
    'Acetyl': modification( name='Acetyl', gainFormula='C2H3O', lossFormula='H', aminoSpecifity='KCST', termSpecifity='N', description='Acetylation'),
    'Amide': modification( name='Amide', gainFormula='NH2', lossFormula='OH', aminoSpecifity='', termSpecifity='C', description='Amidation'),
    'Aminotyrosine': modification( name='Aminotyrosine', gainFormula='HN', lossFormula='', aminoSpecifity='Y', termSpecifity='', description='Tyrosine oxidation to 2-aminotyrosine'),
    'Biotin': modification( name='Biotin', gainFormula='H14C10N2O2S', lossFormula='', aminoSpecifity='K', termSpecifity='N', description='Biotinylation'),
    'Boc': modification( name='Boc', gainFormula='C5H9O2', lossFormula='H', aminoSpecifity='K', termSpecifity='N', description='Boc protecting group'),
    'Carbamidomethyl': modification( name='Carbamidomethyl', gainFormula='CH2CONH2', lossFormula='H', aminoSpecifity='CKHDE', termSpecifity='N', description='Iodoacetamide derivative'),
    'Carbamyl': modification( name='Carbamyl', gainFormula='HCNO', lossFormula='', aminoSpecifity='KRCM', termSpecifity='N', description='Carbamylation'),
    'Carboxyethyl': modification( name='Carboxyethyl', gainFormula='H4C3O2', lossFormula='', aminoSpecifity='K', termSpecifity='', description='Carboxyethyl'),
    'Carboxyl': modification( name='Carboxyl', gainFormula='CO2', lossFormula='', aminoSpecifity='WKDEM', termSpecifity='', description='Carboxylation'),
    'Carboxymethyl': modification( name='Carboxymethyl', gainFormula='CH2COOH', lossFormula='H', aminoSpecifity='CKW', termSpecifity='N', description='Iodoacetic acid derivative'),
    'Cation:K': modification( name='Cation:K', gainFormula='K', lossFormula='H', aminoSpecifity='DE', termSpecifity='C', description='Replacement of proton by potassium'),
    'Cation:Na': modification( name='Cation:Na', gainFormula='Na', lossFormula='H', aminoSpecifity='DE', termSpecifity='C', description='Replacement of proton by sodium'),
    'Cyano': modification( name='Cyano', gainFormula='CN', lossFormula='H', aminoSpecifity='C', termSpecifity='', description='Cyano'),
    'Cys->Dha': modification( name='Cys->Dha', gainFormula='', lossFormula='H2S', aminoSpecifity='C', termSpecifity='', description='Dehydroalanine (from Cysteine)'),
    'Cystine': modification( name='Cystine', gainFormula='', lossFormula='H', aminoSpecifity='C', termSpecifity='', description='Half of a disulfide bridge'),
    'Deamidation': modification( name='Deamidation', gainFormula='O', lossFormula='HN', aminoSpecifity='NQRF', termSpecifity='', description='Deamidation'),
    'Dehydrated': modification( name='Dehydrated', gainFormula='', lossFormula='H2O', aminoSpecifity='NQSTYDC', termSpecifity='', description='Dehydration'),
    'Diacylglycerol': modification( name='Diacylglycerol', gainFormula='H68C37O4', lossFormula='', aminoSpecifity='C', termSpecifity='', description='Diacylglycerol'),
    'Dimethyl': modification( name='Dimethyl', gainFormula='C2H6', lossFormula='H2', aminoSpecifity='KRNP', termSpecifity='N', description='Di-Methylation'),
    'Dioxidation': modification( name='Dioxidation', gainFormula='O2H2', lossFormula='H2', aminoSpecifity='PRKMFWYC', termSpecifity='', description='Dihydroxy'),
    'Ethanolyl': modification( name='Ethanolyl', gainFormula='H4C2O', lossFormula='', aminoSpecifity='C', termSpecifity='', description='Ethanolation of Cys'),
    'Ethyl': modification( name='Ethyl', gainFormula='H4C2', lossFormula='', aminoSpecifity='KED', termSpecifity='N', description='Ethylation'),
    'FAD': modification( name='FAD', gainFormula='H31C27N9O15P2', lossFormula='', aminoSpecifity='CHY', termSpecifity='', description='Flavin adenine dinucleotide'),
    'FMNH': modification( name='FMNH', gainFormula='H19C17N4O9P', lossFormula='', aminoSpecifity='CH', termSpecifity='', description='Flavin mononucleotide'),
    'Fluorescein': modification( name='Fluorescein', gainFormula='H14C22NO6', lossFormula='', aminoSpecifity='C', termSpecifity='', description='5-iodoacetamidofluorescein'),
    'Fmoc': modification( name='Fmoc', gainFormula='C15H11O2', lossFormula='H', aminoSpecifity='K', termSpecifity='N', description='Fmoc protecting group'),
    'Formyl': modification( name='Formyl', gainFormula='CHO', lossFormula='H', aminoSpecifity='KST', termSpecifity='N', description='Formylation'),
    'FormylMet': modification( name='FormylMet', gainFormula='H10C6NO2S', lossFormula='', aminoSpecifity='', termSpecifity='N', description='Addition of N-formyl Methionine'),
    'Guanidination': modification( name='Guanidination', gainFormula='CH3N2', lossFormula='H', aminoSpecifity='K', termSpecifity='', description='Homoarginine from Lysine'),
    'Guanidinyl': modification( name='Guanidinyl', gainFormula='H2CN2', lossFormula='', aminoSpecifity='K', termSpecifity='', description='Guanidination'),
    'Heme': modification( name='Heme', gainFormula='H32C34N4O4Fe', lossFormula='', aminoSpecifity='CH', termSpecifity='', description='Heme'),
    'Hep': modification( name='Hep', gainFormula='C7H14O7', lossFormula='H2O', aminoSpecifity='KNQRST', termSpecifity='', description='Heptose'),
    'Hex': modification( name='Hex', gainFormula='C6H12O6', lossFormula='H2O', aminoSpecifity='KNTWCRY', termSpecifity='N', description='Hexose'),
    'HexN': modification( name='HexN', gainFormula='C6H13N1O5', lossFormula='H2O', aminoSpecifity='KNTW', termSpecifity='', description='Hexosamine'),
    'HexNAc': modification( name='HexNAc', gainFormula='C8H15N1O6', lossFormula='H2O', aminoSpecifity='NST', termSpecifity='', description='N-Acetylhexosamine'),
    'Hydroxymethyl': modification( name='Hydroxymethyl', gainFormula='H2CO', lossFormula='', aminoSpecifity='N', termSpecifity='', description='Hydroxymethyl'),
    'Iodo': modification( name='Iodo', gainFormula='I', lossFormula='H', aminoSpecifity='YH', termSpecifity='', description='Iodination'),
    'Label:13C(6)': modification( name='Label:13C(6)', gainFormula='C{13}6', lossFormula='C6', aminoSpecifity='KR', termSpecifity='', description='13C(6) Silac label'),
    'Lipoyl': modification( name='Lipoyl', gainFormula='H12C8OS2', lossFormula='', aminoSpecifity='K', termSpecifity='', description='Lipoyl'),
    'Methyl': modification( name='Methyl', gainFormula='CH3', lossFormula='H', aminoSpecifity='CHKNQRIL', termSpecifity='N', description='Methylation'),
    'Myristoyl': modification( name='Myristoyl', gainFormula='C14H27O', lossFormula='H', aminoSpecifity='GKC', termSpecifity='N', description='Myristoylation'),
    'Nitro': modification( name='Nitro', gainFormula='NO2', lossFormula='H', aminoSpecifity='WY', termSpecifity='', description='Oxidation to nitro'),
    'Oxidation': modification( name='Oxidation', gainFormula='O', lossFormula='', aminoSpecifity='ODKNPFYRMCHWG', termSpecifity='', description='Oxidation or Hydroxylation'),
    'Palmitoyl': modification( name='Palmitoyl', gainFormula='C16H31O', lossFormula='H', aminoSpecifity='CKST', termSpecifity='N', description='Palmitoylation'),
    'Pentose': modification( name='Pentose', gainFormula='C5H10O5', lossFormula='H2O', aminoSpecifity='STD', termSpecifity='', description='Pentose'),
    'Phenylisocyanate': modification( name='Phenylisocyanate', gainFormula='H5C7NO', lossFormula='', aminoSpecifity='', termSpecifity='N', description='Phenyl isocyanate'),
    'Phospho': modification( name='Phospho', gainFormula='H2PO3', lossFormula='H', aminoSpecifity='STYDHCR', termSpecifity='', description='Phosphorylation'),
    'Propionamide': modification( name='Propionamide', gainFormula='C3H6ON', lossFormula='H', aminoSpecifity='C', termSpecifity='', description='Acrylamide adduct'),
    'SeCys': modification( name='SeCys', gainFormula='Se', lossFormula='S', aminoSpecifity='C', termSpecifity='', description='Selenium replaces sulphur in Cysteine'),
    'SeMet': modification( name='SeMet', gainFormula='Se', lossFormula='S', aminoSpecifity='M', termSpecifity='', description='Selenium replaces sulphur in Methionine'),
    'Sulfo': modification( name='Sulfo', gainFormula='HSO3', lossFormula='H', aminoSpecifity='STYC', termSpecifity='', description='O-Sulfonation'),
    'Tyr->Dha': modification( name='Tyr->Dha', gainFormula='', lossFormula='H6C6O', aminoSpecifity='Y', termSpecifity='', description='Dehydroalanine (from Tyrosine)'),
    'dHex': modification( name='dHex', gainFormula='C6H12O5', lossFormula='H2O', aminoSpecifity='ST', termSpecifity='', description='Deoxyhexose, fucose'),
    'pCMB': modification( name='pCMB', gainFormula='C7H5HgO2', lossFormula='H', aminoSpecifity='C', termSpecifity='', description='p-Chloromercurybenzoate'),
    'tButyl': modification( name='tButyl', gainFormula='C4H9', lossFormula='H', aminoSpecifity='CDEHSTY', termSpecifity='', description='tButyl protecting group'),
}


# LOAD FUNCTIONS
# --------------

def loadMonomers(path=os.path.join(blocksdir, 'monomers.xml'), clear=False, replace=False):
    """Parse monomers XML and get data."""
    
    container = {}
    
    # parse XML
    document = xml.dom.minidom.parse(path)
    
    # get monomers
    monomerTags = document.getElementsByTagName('monomer')
    for x, monomerTag in enumerate(monomerTags):
        
        # get basic data
        abbr = monomerTag.getAttribute('abbr')
        name = monomerTag.getAttribute('name')
        category = monomerTag.getAttribute('category')
        formula = monomerTag.getAttribute('formula')
        
        # get losses
        losses = []
        attr = monomerTag.getAttribute('losses')
        if attr:
            losses = attr.split(';')
        
        # add object
        container[abbr] = monomer(
            abbr = abbr,
            formula = formula,
            losses = losses,
            name = name,
            category = category
        )
    
    # update current lib
    if container and clear:
        monomers.clear()
    for key in container:
        if replace or not key in monomers:
            monomers[key] = container[key]
# ----


def loadEnzymes(path=os.path.join(blocksdir, 'enzymes.xml'), clear=False, replace=True):
    """Parse enzymes XML and get data."""
    
    container = {}
    
    # parse XML
    document = xml.dom.minidom.parse(path)
    
    # get enzymes
    enzymeTags = document.getElementsByTagName('enzyme')
    for x, enzymeTag in enumerate(enzymeTags):
        
        # get name
        name = str(enzymeTag.getAttribute('name'))
        
        # get expression
        expressionTags = enzymeTag.getElementsByTagName('expression')
        expression = str(expressionTags[0].childNodes[0].data)
        
        # get formula
        formulaTags = enzymeTag.getElementsByTagName('formula')
        nTermFormula = str(formulaTags[0].getAttribute('nTerm'))
        cTermFormula = str(formulaTags[0].getAttribute('cTerm'))
        
        # allowed modifications
        allowModsTags = enzymeTag.getElementsByTagName('allowMods')
        modsBefore = bool(int(allowModsTags[0].getAttribute('before')))
        modsAfter = bool(int(allowModsTags[0].getAttribute('after')))
        
        # add objects
        container[name] = enzyme(
            name = name,
            expression = expression,
            nTermFormula = nTermFormula,
            cTermFormula = cTermFormula,
            modsBefore = modsBefore,
            modsAfter = modsAfter
        )
    
    # update current lib
    if container and clear:
        enzymes.clear()
    for key in container:
        if replace or not key in enzymes:
            enzymes[key] = container[key]
# ----


def loadModifications(path=os.path.join(blocksdir, 'modifications.xml'), clear=False, replace=True):
    """Parse modifications XML and get data."""
    
    container = {}
    
    # parse XML
    document = xml.dom.minidom.parse(path)
    
    # get modifications
    modificationTags = document.getElementsByTagName('modification')
    for x, modificationTag in enumerate(modificationTags):
        
        # get name
        name = str(modificationTag.getAttribute('name'))
        
        # get formulas
        formulaTags = modificationTag.getElementsByTagName('formula')
        gainFormula = str(formulaTags[0].getAttribute('gain'))
        lossFormula = str(formulaTags[0].getAttribute('loss'))
        
        # get specifity
        specifityTags = modificationTag.getElementsByTagName('specifity')
        aminoSpecifity = str(specifityTags[0].getAttribute('amino'))
        termSpecifity = str(specifityTags[0].getAttribute('terminus'))
        
        # get description
        descriptionTags = modificationTag.getElementsByTagName('description')
        description = _getNodeText(descriptionTags[0])
        
        # add object
        container[name] = modification(
            name = name,
            gainFormula = gainFormula,
            lossFormula = lossFormula,
            aminoSpecifity = aminoSpecifity,
            termSpecifity = termSpecifity,
            description = description
        )
    
    # update current lib
    if container and clear:
        modifications.clear()
    for key in container:
        if replace or not key in modifications:
            modifications[key] = container[key]
# ----


def _getNodeText(node):
    """Get text from node list."""
    
    buff = ''
    for node in node.childNodes:
        if node.nodeType == node.TEXT_NODE:
            buff += node.data
    
    return buff
# ----



# SAVE FUNCTIONS
# --------------

def saveMonomers(path=os.path.join(blocksdir, 'monomers.xml')):
    """Make and save monomers XML."""
    
    # make monomers xml
    buff = '<?xml version="1.0" encoding="utf-8" ?>\n'
    buff += '<mspyMonomers version="1.0">\n'
    
    abbrs = monomers.keys()
    abbrs.sort()
    for abbr in abbrs:
        if monomers[abbr].category != '_InternalAA':
            buff += '  <monomer abbr="%s" name="%s" formula="%s" category="%s" losses="%s" />\n' % (monomers[abbr].abbr, monomers[abbr].name, monomers[abbr].formula, monomers[abbr].category, ';'.join(monomers[abbr].losses))
        
    buff += '</mspyMonomers>'
    
    # save monomers file
    try:
        save = file(path, 'w')
        save.write(buff.encode("utf-8"))
        save.close()
        return True
    except:
        return False
# ----


def saveEnzymes(path=os.path.join(blocksdir, 'enzymes.xml')):
    """Make and save enzymes XML."""
    
    # make enzymes xml
    buff = '<?xml version="1.0" encoding="utf-8" ?>\n'
    buff += '<mspyEnzymes version="1.0">\n'
    
    names = enzymes.keys()
    names.sort()
    for name in names:
        buff += '  <enzyme name="%s">\n' % (_escape(enzymes[name].name))
        buff += '    <expression><![CDATA[%s]]></expression>\n' % (enzymes[name].expression)
        buff += '    <formula nTerm="%s" cTerm="%s" />\n' % (enzymes[name].nTermFormula, enzymes[name].cTermFormula)
        buff += '    <allowMods before="%s" after="%s" />\n' % (int(enzymes[name].modsBefore), int(enzymes[name].modsAfter))
        buff += '  </enzyme>\n'
        
    buff += '</mspyEnzymes>'
    
    # save enzymes file
    try:
        save = file(path, 'w')
        save.write(buff.encode("utf-8"))
        save.close()
        return True
    except:
        return False
# ----


def saveModifications(path=os.path.join(blocksdir, 'modifications.xml')):
    """Make and save modifications XML."""
    
    # make modifications xml
    buff = '<?xml version="1.0" encoding="utf-8" ?>\n'
    buff += '<mspyModifications version="1.0">\n'
    
    names = modifications.keys()
    names.sort()
    for name in names:
        buff += '  <modification name="%s">\n' % (_escape(modifications[name].name))
        buff += '    <description>%s</description>\n' % (_escape(modifications[name].description))
        buff += '    <formula gain="%s" loss="%s" />\n' % (modifications[name].gainFormula, modifications[name].lossFormula)
        buff += '    <specifity amino="%s" terminus="%s" />\n' % (modifications[name].aminoSpecifity, modifications[name].termSpecifity)
        buff += '  </modification>\n'
        
    buff += '</mspyModifications>'
    
    # save modifications file
    try:
        save = file(path, 'w')
        save.write(buff.encode("utf-8"))
        save.close()
        return True
    except:
        return False
# ----


def _escape(text):
    """Clear special characters such as <> etc."""
    
    text = text.strip()
    search = ('&', '"', "'", '<', '>')
    replace = ('&amp;', '&quot;', '&apos;', '&lt;', '&gt;')
    for x, item in enumerate(search):
        text = text.replace(item, replace[x])
        
    return text
# ----


