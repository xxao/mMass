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
import sys
import os
import xml.dom.minidom


# SET VERSION
# -----------

version = '5.5.0'
nightbuild = ''


# SET CONFIG FOLDER
# -----------------

# set config folder for MAC OS X
if sys.platform == 'darwin':
    confdir = 'configs'
    support = os.path.expanduser("~/Library/Application Support/")
    userconf = os.path.join(support,'mMass')
    if os.path.exists(support) and not os.path.exists(userconf):
        try: os.mkdir(userconf)
        except: pass
    if os.path.exists(userconf):
        confdir = userconf

# set config folder for Linux
elif sys.platform.startswith('linux') or sys.platform.startswith('freebsd'):
    confdir = 'configs'
    home = os.path.expanduser("~")
    userconf = os.path.join(home,'.mmass')
    if os.path.exists(home) and not os.path.exists(userconf):
        try: os.mkdir(userconf)
        except: pass
    if os.path.exists(userconf):
        confdir = userconf

# set config folder for Windows
else:
    confdir = os.path.sep
    for folder in os.path.dirname(os.path.realpath(__file__)).split(os.path.sep)[:-1]:
        path = os.path.join(confdir, folder)
        if os.path.isdir(path):
            confdir = path
        if os.path.isfile(path):
            break
    confdir = os.path.join(confdir, 'configs')
    if not os.path.exists(confdir):
        try: os.mkdir(confdir)
        except: pass

if not os.path.exists(confdir):
    raise IOError, "Configuration folder cannot be found!"


# INIT DEFAULT VALUES
# -------------------

internal={
    'canvasXrange': None,
}

main={
    'appWidth': 1050,
    'appHeight': 620,
    'appMaximized': 0,
    'unlockGUI': 0,
    'layout': 'default',
    'documentsWidth': 195,
    'documentsHeight': 195,
    'peaklistWidth': 195,
    'peaklistHeight': 195,
    'mzDigits': 4,
    'intDigits': 0,
    'ppmDigits': 1,
    'chargeDigits': 2,
    'dataPrecision': 32,
    'lastDir': '',
    'lastSeqDir': '',
    'errorUnits': 'Da',
    'printQuality': 5,
    'useServer': 1,
    'serverPort': 65456,
    'reverseScrolling': 0,
    'macListCtrlGeneric': 1,
    'peaklistColumns': ['mz', 'int', 'rel', 'sn', 'z', 'fwhm', 'resol'],
    'cursorInfo': ['mz', 'dist', 'ppm', 'z'],
    'updatesEnabled': 1,
    'updatesChecked': '',
    'updatesCurrent': version,
    'updatesAvailable': version,
    'compassMode': 'Profile',
    'compassFormat': 'mzML',
    'compassDeleteFile': 1,
}

recent=[]

colours=[
    [16,71,185],
    [50,140,0],
    [241,144,0],
    [76,199,197],
    [143,143,21],
    [38,122,255],
    [38,143,73],
    [237,187,0],
    [120,109,255],
    [179,78,0],
    [128,191,189],
    [137,136,68],
    [200,136,18],
    [197,202,61],
    [123,182,255],
    [69,67,138],
    [24,129,131],
    [131,129,131],
    [69,126,198],
    [189,193,123],
    [127,34,0],
    [76,78,76],
    [31,74,145],
    [15,78,75],
    [79,26,81],
]

export={
    'imageWidth': 750,
    'imageHeight': 500,
    'imageUnits': 'px',
    'imageResolution': 72,
    'imageFontsScale': 1,
    'imageDrawingsScale': 1,
    'imageFormat': 'PNG',
    'peaklistColumns': ['mz','int'],
    'peaklistFormat': 'ASCII',
    'peaklistSeparator': 'tab',
    'spectrumSeparator': 'tab',
}

spectrum={
    'xLabel': 'm/z',
    'yLabel': 'a.i.',
    'showGrid': 1,
    'showMinorTicks': 1,
    'showLegend': 1,
    'showPosBars': 1,
    'showGel': 1,
    'showGelLegend': 1,
    'showTracker': 1,
    'showNotations': 1,
    'showLabels': 1,
    'showAllLabels': 1,
    'showTicks': 1,
    'showDataPoints': 1,
    'showCursorImage': 1,
    'posBarSize': 7,
    'gelHeight': 19,
    'autoscale': 1,
    'normalize': 0,
    'overlapLabels': 0,
    'checkLimits': 1,
    'labelAngle': 90,
    'labelCharge': 1,
    'labelGroup': 0,
    'labelBgr': 1,
    'labelFontSize': 10,
    'axisFontSize': 10,
    'tickColour': [255,75,75],
    'tmpSpectrumColour': [255,0,0],
    'notationMarksColour': [0,255,0],
    'notationMaxLength': 40,
    'notationMarks': 1,
    'notationLabels': 0,
    'notationMZ': 0,
}

match={
    'tolerance': 0.2,
    'units': 'Da',
    'ignoreCharge': 0,
    'filterAnnotations': 0,
    'filterMatches': 0,
    'filterUnselected': 0,
    'filterIsotopes': 1,
    'filterUnknown': 0,
}

processing={
    'math':{
        'operation': 'normalize',
        'multiplier': 1,
    },
    'crop':{
        'lowMass': 500,
        'highMass': 5000,
    },
    'baseline':{
        'precision': 15,
        'offset': 0.25,
    },
    'smoothing':{
        'method': 'SG',
        'windowSize': 0.3,
        'cycles': 2,
    },
    'peakpicking':{
        'snThreshold': 3.0,
        'absIntThreshold': 0,
        'relIntThreshold': 0.0,
        'pickingHeight': 0.75,
        'baseline': 1,
        'smoothing': 1,
        'deisotoping': 1,
        'monoisotopic': 0,
        'removeShoulders': 0,
    },
    'deisotoping':{
        'maxCharge': 1,
        'massTolerance': 0.1,
        'intTolerance': 0.5,
        'isotopeShift': 0.0,
        'removeIsotopes': 1,
        'removeUnknown': 1,
        'labelEnvelope': '1st',
        'envelopeIntensity': 'maximum',
        'setAsMonoisotopic': 0,
    },
    'deconvolution':{
        'massType': 0,
        'groupWindow': 0.01,
        'groupPeaks': 1,
        'forceGroupWindow': 0,
    },
    'batch':{
        'swap': 0,
        'math': 0,
        'crop': 0,
        'baseline': 0,
        'smoothing': 0,
        'peakpicking': 0,
        'deisotoping': 0,
        'deconvolution': 0,
    },
}

calibration={
    'fitting': 'quadratic',
    'tolerance': 50,
    'units': 'ppm',
    'statCutOff': 800,
}

sequence={
    'editor':{
        'gridSize': 20,
    },
    'digest':{
        'maxMods': 1,
        'maxCharge': 1,
        'massType': 0,
        'enzyme': 'Trypsin',
        'miscl': 1,
        'lowMass': 500,
        'highMass': 5000,
        'retainPos': 0,
        'allowMods': 0,
        'listTemplateAmino': 'b.S.a [m]',
        'listTemplateCustom': 'b . [ S ] . a [m]',
        'matchTemplateAmino': 'h b.S.a [m]',
        'matchTemplateCustom': ' h b . [ S ] . a [m]',
    },
    'fragment':{
        'maxMods': 1,
        'maxCharge': 1,
        'massType': 1,
        'fragments': ['a','b','y','-NH3','-H2O'],
        'maxLosses': 2,
        'filterFragments': 1,
        'listTemplateAmino': 'b.S.a [m]',
        'listTemplateCustom': 'b . [ S ] . a [m]',
        'matchTemplateAmino': 'f h [m]',
        'matchTemplateCustom': 'f h [m]',
    },
    'search':{
        'mass': 0,
        'maxMods': 1,
        'charge': 1,
        'massType': 0,
        'enzyme': 'Trypsin',
        'semiSpecific': True,
        'tolerance': 0.2,
        'units': 'Da',
        'retainPos': 0,
        'listTemplateAmino': 'b.S.a [m]',
        'listTemplateCustom': 'b . [ S ] . a [m]',
    },
}

massCalculator={
    'ionseriesAgent': 'H',
    'ionseriesAgentCharge': 1,
    'ionseriesPolarity': 1,
    'patternFwhm': 0.1,
    'patternIntensity': 100,
    'patternBaseline': 0,
    'patternShift': 0,
    'patternThreshold': 0.001,
    'patternShowPeaks': 1,
    'patternPeakShape': 'gaussian',
}

massfilter={}

massToFormula={
    'countLimit': 1000,
    'massLimit': 3000,
    'charge': 1,
    'ionization': 'H',
    'tolerance': 1.,
    'units': 'ppm',
    'formulaMin': '',
    'formulaMax': '',
    'autoCHNO': 1,
    'checkPattern': 1,
    'rules': ['HC','NOPSC','NOPS','RDBE', 'RDBEInt'],
    'HCMin': 0.1,
    'HCMax': 3,
    'NCMax': 4,
    'OCMax': 3,
    'PCMax': 2,
    'SCMax': 3,
    'RDBEMin': -1,
    'RDBEMax': 40,
    'PubChemScript':'http://pubchem.ncbi.nlm.nih.gov/search/search.cgi',
    'ChemSpiderScript': 'http://www.chemspider.com/Search.aspx',
    'METLINScript': 'http://metlin.scripps.edu/metabo_list_adv.php',
    'HMDBScript': 'http://www.hmdb.ca/search',
    'LipidMAPSScript': 'http://www.lipidmaps.org/data/structure/LMSDSearch.php',
}

massDefectPlot={
    'xAxis': 'mz',
    'yAxis': 'standard',
    'nominalMass': 'floor',
    'kendrickFormula': 'CH2',
    'relIntCutoff': 0.0,
    'removeIsotopes': 0,
    'ignoreCharge': 1,
    'showNotations': 0,
    'showAllDocuments': 0,
}

compoundsSearch={
    'massType': 0,
    'maxCharge': 1,
    'radicals': 0,
    'adducts':  ['Na','K'],
}

peakDifferences={
    'aminoacids': 1,
    'dipeptides': 0,
    'massType': 0,
    'tolerance': 0.1,
    'consolidate': 0,
}

comparePeaklists={
    'compare': 'peaklists',
    'tolerance': 0.2,
    'units': 'Da',
    'ignoreCharge': 0,
    'ratioCheck': 0,
    'ratioDirection': 1,
    'ratioThreshold': 2,
}

spectrumGenerator={
    'fwhm': 0.1,
    'points': 10,
    'noise': 0,
    'forceFwhm': 0,
    'peakShape': 'gaussian',
    'showPeaks': 1,
    'showOverlay': 0,
    'showFlipped': 0,
}

envelopeFit={
    'loss': 'H',
    'gain': 'H{2}',
    'fit': 'spectrum',
    'scaleMin': 0,
    'scaleMax': 10,
    'charge': 1,
    'fwhm': 0.01,
    'forceFwhm': 0,
    'peakShape': 'gaussian',
    'autoAlign': 1,
    'relThreshold': 0.05,
}

mascot={
    'common':{
        'title':'',
        'userName':'',
        'userEmail':'',
        'server': 'Matrix Science',
        'searchType': 'pmf',
        'filterAnnotations': 0,
        'filterMatches': 0,
        'filterUnselected': 0,
        'filterIsotopes': 1,
        'filterUnknown': 0,
    },
    'pmf':{
        'database': 'SwissProt',
        'taxonomy': 'All entries',
        'enzyme': 'Trypsin',
        'miscleavages': 1,
        'fixedMods': [],
        'variableMods': [],
        'hiddenMods': 0,
        'proteinMass': '',
        'peptideTol': 0.1,
        'peptideTolUnits': 'Da',
        'massType': 'Monoisotopic',
        'charge': '1+',
        'decoy': 0,
        'report': 'AUTO',
    },
    'sq':{
        'database': 'SwissProt',
        'taxonomy': 'All entries',
        'enzyme': 'Trypsin',
        'miscleavages': 1,
        'fixedMods': [],
        'variableMods': [],
        'hiddenMods': 0,
        'peptideTol': 0.1,
        'peptideTolUnits': 'Da',
        'msmsTol': 0.2,
        'msmsTolUnits': 'Da',
        'massType': 'Average',
        'charge': '1+',
        'instrument': 'Default',
        'quantitation': 'None',
        'decoy': 0,
        'report': 'AUTO',
    },
    'mis':{
        'database': 'SwissProt',
        'taxonomy': 'All entries',
        'enzyme': 'Trypsin',
        'miscleavages': 1,
        'fixedMods': [],
        'variableMods': [],
        'hiddenMods': 0,
        'peptideMass': '',
        'peptideTol': 0.1,
        'peptideTolUnits': 'Da',
        'msmsTol': 0.2,
        'msmsTolUnits': 'Da',
        'massType': 'Average',
        'charge': '1+',
        'instrument': 'Default',
        'quantitation': 'None',
        'decoy': 0,
        'errorTolerant': 0,
        'report': 'AUTO',
    },
}

profound={
    'script': 'http://prowl.rockefeller.edu/prowl-cgi/profound.exe',
    'title':'',
    'database': 'NCBI nr',
    'taxonomy': 'All taxa',
    'enzyme': 'Trypsin',
    'miscleavages': 1,
    'fixedMods': [],
    'variableMods': [],
    'proteinMassLow': 0,
    'proteinMassHigh': 300,
    'proteinPILow': 0,
    'proteinPIHigh': 14,
    'peptideTol': 0.1,
    'peptideTolUnits': 'Da',
    'massType': 'Monoisotopic',
    'charge': 'MH+',
    'ranking': 'expect',
    'expectation': 1,
    'candidates': 10,
    'filterAnnotations': 0,
    'filterMatches': 0,
    'filterUnselected': 0,
    'filterIsotopes': 1,
    'filterUnknown': 0,
}

prospector={
    'common':{
        'title':'',
        'script': 'http://prospector.ucsf.edu/prospector/cgi-bin/mssearch.cgi',
        'searchType': 'msfit',
        'filterAnnotations': 0,
        'filterMatches': 0,
        'filterUnselected': 0,
        'filterIsotopes': 1,
        'filterUnknown': 0,
    },
    'msfit':{
        'database': 'SwissProt',
        'taxonomy': 'All',
        'enzyme': 'Trypsin',
        'miscleavages': 1,
        'fixedMods': [],
        'variableMods': [],
        'proteinMassLow': 0,
        'proteinMassHigh': 300,
        'proteinPILow': 0,
        'proteinPIHigh': 14,
        'peptideTol': 0.1,
        'peptideTolUnits': 'Da',
        'massType': 'Monoisotopic',
        'instrument': 'MALDI-TOFTOF',
        'minMatches': 4,
        'maxMods': 1,
        'report': 5,
        'pfactor': 0.4,
    },
    'mstag':{
        'database': 'SwissProt',
        'taxonomy': 'All',
        'enzyme': 'Trypsin',
        'miscleavages': 1,
        'fixedMods': [],
        'variableMods': [],
        'peptideMass': '',
        'peptideTol': 0.1,
        'peptideTolUnits': 'Da',
        'peptideCharge': '1',
        'msmsTol': 0.2,
        'msmsTolUnits': 'Da',
        'massType': 'Monoisotopic',
        'instrument': 'MALDI-TOFTOF',
        'maxMods': 1,
        'report': 5,
    },
}

links={
    'mMassHomepage': 'http://www.mmass.org/',
    'mMassForum': 'http://forum.mmass.org/',
    'mMassTwitter':  'http://www.twitter.com/mmassorg/',
    'mMassCite': 'http://www.mmass.org/donate/papers.php',
    'mMassDonate': 'http://www.mmass.org/donate/',
    'mMassDownload': 'http://www.mmass.org/download/',
    'mMassWhatsNew': 'http://www.mmass.org/download/history.php',
    
    'biomedmstools': 'http://ms.biomed.cas.cz/MSTools/',
    'blast': 'http://www.ebi.ac.uk/Tools/blastall/',
    'clustalw': 'http://www.ebi.ac.uk/Tools/clustalw/',
    'deltamass': 'http://www.abrf.org/index.cfm/dm.home',
    'emblebi': 'http://www.ebi.ac.uk/services/',
    'expasy': 'http://www.expasy.org/',
    'fasta': 'http://www.ebi.ac.uk/Tools/fasta33/',
    'matrixscience': 'http://www.matrixscience.com/',
    'muscle': 'http://phylogenomics.berkeley.edu/cgi-bin/muscle/input_muscle.py',
    'ncbi': 'http://www.ncbi.nlm.nih.gov/Entrez/',
    'pdb': 'http://www.rcsb.org/pdb/',
    'pir': 'http://pir.georgetown.edu/',
    'profound': 'http://prowl.rockefeller.edu/prowl-cgi/profound.exe',
    'prospector': 'http://prospector.ucsf.edu/',
    'unimod': 'http://www.unimod.org/',
    'uniprot': 'http://www.uniprot.org/',
}

replacements={
    'sequences':{
        'general':{
            'pattern': '^([A-Z0-9_]+[\.0-9]*)$',
            'url': 'http://www.ncbi.nlm.nih.gov/protein/%s',
        },
        'gi':{
            'pattern': '^gi\|?([0-9]+[\.0-9]*)$',
            'url': 'http://www.ncbi.nlm.nih.gov/protein/%s',
        },
        'gb':{
            'pattern': '^gb\|?([A-Z]{3}[0-9]{5}[\.0-9]*)$',
            'url': 'http://www.ncbi.nlm.nih.gov/protein/%s',
        },
        'sp':{
            'pattern': '^sp\|?([A-Z][A-Z0-9]+)$',
            'url': 'http://www.uniprot.org/uniprot/%s',
        },
        'ref':{
            'pattern': '^ref\|?([A-Z]{2}_[0-9]+[\.0-9]*)$',
            'url': 'http://www.ncbi.nlm.nih.gov/protein/%s',
        },
    },
    'compounds':{
        'PubChemC':{
            'pattern': 'CID([0-9]{1,10})',
            'url': 'http://pubchem.ncbi.nlm.nih.gov/summary/summary.cgi?cid=%s',
        },
        'LipidMaps':{
            'pattern': '(LM[A-Z]{2}[0-9]{4}[0-9A-Z]{2}[0-9]{2})',
            'url': 'http://www.lipidmaps.org/data/LMSDRecord.php?LMID=%s',
        },
        'NORINE':{
            'pattern': '(NOR[0-9]{5})',
            'url': 'http://bioinfo.lifl.fr/norine/result.jsp?ID=%s',
        },
    },
}


# LOAD AND SAVE CONFIG FILE
# -------------------------

def loadConfig(path=os.path.join(confdir, 'config.xml')):
    """Parse config XML and get data."""
    
    # parse XML
    document = xml.dom.minidom.parse(path)
    
    # main
    mainTags = document.getElementsByTagName('main')
    if mainTags:
        _getParams(mainTags[0], main)
        
        if type(main['cursorInfo']) != list:
            main['cursorInfo'] = main['cursorInfo'].split(';')
        
        if type(main['peaklistColumns']) != list:
            main['peaklistColumns'] = main['peaklistColumns'].split(';')
    
    # recent files
    recentTags = document.getElementsByTagName('recent')
    if recentTags:
        pathTags = recentTags[0].getElementsByTagName('path')
        if pathTags:
            del recent[:]
            for pathTag in pathTags:
                recent.append(pathTag.getAttribute('value'))
    
    # colours
    coloursTags = document.getElementsByTagName('colours')
    if coloursTags:
        colourTags = coloursTags[0].getElementsByTagName('colour')
        if colourTags:
            del colours[:]
            for colourTag in colourTags:
                col = colourTag.getAttribute('value')
                colours.append([int(c, 16) for c in (col[0:2], col[2:4], col[4:6])])
    
    # export
    exportTags = document.getElementsByTagName('export')
    if exportTags:
        _getParams(exportTags[0], export)
        
        if type(export['peaklistColumns']) != list:
            export['peaklistColumns'] = export['peaklistColumns'].split(';')
    
    # spectrum
    spectrumTags = document.getElementsByTagName('spectrum')
    if spectrumTags:
        _getParams(spectrumTags[0], spectrum)
        
        if type(spectrum['tickColour']) != list:
            col = spectrum['tickColour']
            spectrum['tickColour'] = [int(c, 16) for c in (col[0:2], col[2:4], col[4:6])]
        
        if type(spectrum['tmpSpectrumColour']) != list:
            col = spectrum['tmpSpectrumColour']
            spectrum['tmpSpectrumColour'] = [int(c, 16) for c in (col[0:2], col[2:4], col[4:6])]
        
        if type(spectrum['notationMarksColour']) != list:
            col = spectrum['notationMarksColour']
            spectrum['notationMarksColour'] = [int(c, 16) for c in (col[0:2], col[2:4], col[4:6])]
    
    # match
    matchTags = document.getElementsByTagName('match')
    if matchTags:
        _getParams(matchTags[0], match)
    
    # processing
    processingTags = document.getElementsByTagName('processing')
    if processingTags:
        
        cropTags = processingTags[0].getElementsByTagName('crop')
        if cropTags:
            _getParams(cropTags[0], processing['crop'])
        
        baselineTags = processingTags[0].getElementsByTagName('baseline')
        if baselineTags:
            _getParams(baselineTags[0], processing['baseline'])
        
        smoothingTags = processingTags[0].getElementsByTagName('smoothing')
        if smoothingTags:
            _getParams(smoothingTags[0], processing['smoothing'])
        
        peakpickingTags = processingTags[0].getElementsByTagName('peakpicking')
        if peakpickingTags:
            _getParams(peakpickingTags[0], processing['peakpicking'])
        
        deisotopingTags = processingTags[0].getElementsByTagName('deisotoping')
        if deisotopingTags:
            _getParams(deisotopingTags[0], processing['deisotoping'])
        
        deconvolutionTags = processingTags[0].getElementsByTagName('deconvolution')
        if deconvolutionTags:
            _getParams(deconvolutionTags[0], processing['deconvolution'])
    
    # calibration
    calibrationTags = document.getElementsByTagName('calibration')
    if calibrationTags:
        _getParams(calibrationTags[0], calibration)
    
    # sequence
    sequenceTags = document.getElementsByTagName('sequence')
    if sequenceTags:
        
        editorTags = sequenceTags[0].getElementsByTagName('editor')
        if editorTags:
            _getParams(editorTags[0], sequence['editor'])
        
        digestTags = sequenceTags[0].getElementsByTagName('digest')
        if digestTags:
            _getParams(digestTags[0], sequence['digest'])
        
        fragmentTags = sequenceTags[0].getElementsByTagName('fragment')
        if fragmentTags:
            _getParams(fragmentTags[0], sequence['fragment'])
        
        searchTags = sequenceTags[0].getElementsByTagName('search')
        if searchTags:
            _getParams(searchTags[0], sequence['search'])
        
        if type(sequence['fragment']['fragments']) != list:
            sequence['fragment']['fragments'] = sequence['fragment']['fragments'].split(';')
    
    # mass calculator
    massCalculatorTags = document.getElementsByTagName('massCalculator')
    if massCalculatorTags:
        _getParams(massCalculatorTags[0], massCalculator)
    
    # mass to formula
    massToFormulaTags = document.getElementsByTagName('massToFormula')
    if massToFormulaTags:
        _getParams(massToFormulaTags[0], massToFormula)
        
        if type(massToFormula['rules']) != list:
            massToFormula['rules'] = massToFormula['rules'].split(';')
    
    # mass defect plot
    massDefectPlotTags = document.getElementsByTagName('massDefectPlot')
    if massDefectPlotTags:
        _getParams(massDefectPlotTags[0], massDefectPlot)
    
    # compounds search
    compoundsSearchTags = document.getElementsByTagName('compoundsSearch')
    if compoundsSearchTags:
        _getParams(compoundsSearchTags[0], compoundsSearch)
        
        if type(compoundsSearch['adducts']) != list:
            compoundsSearch['adducts'] = compoundsSearch['adducts'].split(';')
    
    # peak differences
    peakDifferencesTags = document.getElementsByTagName('peakDifferences')
    if peakDifferencesTags:
        _getParams(peakDifferencesTags[0], peakDifferences)
    
    # compare peaklists
    comparePeaklistsTags = document.getElementsByTagName('comparePeaklists')
    if comparePeaklistsTags:
        _getParams(comparePeaklistsTags[0], comparePeaklists)
    
    # spectrum generator
    spectrumGeneratorTags = document.getElementsByTagName('spectrumGenerator')
    if spectrumGeneratorTags:
        _getParams(spectrumGeneratorTags[0], spectrumGenerator)
    
    # envelope fit
    envelopeFitTags = document.getElementsByTagName('envelopeFit')
    if envelopeFitTags:
        _getParams(envelopeFitTags[0], envelopeFit)
    
    # mascot
    mascotTags = document.getElementsByTagName('mascot')
    if mascotTags:
        
        commonTags = mascotTags[0].getElementsByTagName('common')
        if commonTags:
            _getParams(commonTags[0], mascot['common'])
        
        pmfTags = mascotTags[0].getElementsByTagName('pmf')
        if pmfTags:
            _getParams(pmfTags[0], mascot['pmf'])
        
        sqTags = mascotTags[0].getElementsByTagName('sq')
        if sqTags:
            _getParams(sqTags[0], mascot['sq'])
        
        misTags = mascotTags[0].getElementsByTagName('mis')
        if misTags:
            _getParams(misTags[0], mascot['mis'])
        
        for key in ('pmf', 'sq', 'mis'):
            if type(mascot[key]['fixedMods']) != list:
                mascot[key]['fixedMods'] = mascot[key]['fixedMods'].split(';')
            if type(mascot[key]['variableMods']) != list:
                mascot[key]['variableMods'] = mascot[key]['variableMods'].split(';')
    
    # profound
    profoundTags = document.getElementsByTagName('profound')
    if profoundTags:
        _getParams(profoundTags[0], profound)
        
        if type(profound['fixedMods']) != list:
            profound['fixedMods'] = profound['fixedMods'].split(';')
        if type(profound['variableMods']) != list:
            profound['variableMods'] = profound['variableMods'].split(';')
    
    # prospector
    prospectorTags = document.getElementsByTagName('prospector')
    if prospectorTags:
        
        commonTags = prospectorTags[0].getElementsByTagName('common')
        if commonTags:
            _getParams(commonTags[0], prospector['common'])
        
        msfitTags = prospectorTags[0].getElementsByTagName('msfit')
        if msfitTags:
            _getParams(msfitTags[0], prospector['msfit'])
        
        mstagTags = prospectorTags[0].getElementsByTagName('mstag')
        if mstagTags:
            _getParams(mstagTags[0], prospector['mstag'])
        
        for key in ('msfit', 'mstag'):
            if type(prospector[key]['fixedMods']) != list:
                prospector[key]['fixedMods'] = prospector[key]['fixedMods'].split(';')
            if type(prospector[key]['variableMods']) != list:
                prospector[key]['variableMods'] = prospector[key]['variableMods'].split(';')
    
    # links
    linksTags = document.getElementsByTagName('links')
    if linksTags:
        linkTags = linksTags[0].getElementsByTagName('link')
        for linkTag in linkTags:
            name = linkTag.getAttribute('name')
            value = linkTag.getAttribute('value')
            if name not in ('mMassHomepage', 'mMassForum', 'mMassTwitter', 'mMassCite', 'mMassDonate', 'mMassDownload'):
                links[name] = value
# ----


def saveConfig(path=os.path.join(confdir, 'config.xml')):
    """Make and save config XML."""
    
    buff = '<?xml version="1.0" encoding="utf-8" ?>\n'
    buff += '<mMassConfig version="1.0">\n\n'
    
    # main
    buff += '  <main>\n'
    buff += '    <param name="appWidth" value="%d" type="int" />\n' % (main['appWidth'])
    buff += '    <param name="appHeight" value="%d" type="int" />\n' % (main['appHeight'])
    buff += '    <param name="appMaximized" value="%d" type="int" />\n' % (bool(main['appMaximized']))
    buff += '    <param name="layout" value="%s" type="str" />\n' % (_escape(main['layout']))
    buff += '    <param name="documentsWidth" value="%d" type="int" />\n' % (main['documentsWidth'])
    buff += '    <param name="documentsHeight" value="%d" type="int" />\n' % (main['documentsHeight'])
    buff += '    <param name="peaklistWidth" value="%d" type="int" />\n' % (main['peaklistWidth'])
    buff += '    <param name="peaklistHeight" value="%d" type="int" />\n' % (main['peaklistHeight'])
    buff += '    <param name="reverseScrolling" value="%d" type="int" />\n' % (bool(main['reverseScrolling']))
    buff += '    <param name="macListCtrlGeneric" value="%d" type="int" />\n' % (bool(main['macListCtrlGeneric']))
    buff += '    <param name="cursorInfo" value="%s" type="str" />\n' % (';'.join(main['cursorInfo']))
    buff += '    <param name="peaklistColumns" value="%s" type="str" />\n' % (';'.join(main['peaklistColumns']))
    buff += '    <param name="mzDigits" value="%d" type="int" />\n' % (main['mzDigits'])
    buff += '    <param name="intDigits" value="%d" type="int" />\n' % (main['intDigits'])
    buff += '    <param name="ppmDigits" value="%d" type="int" />\n' % (main['ppmDigits'])
    buff += '    <param name="chargeDigits" value="%d" type="int" />\n' % (main['chargeDigits'])
    buff += '    <param name="lastDir" value="%s" type="unicode" />\n' % (_escape(main['lastDir']))
    buff += '    <param name="lastSeqDir" value="%s" type="unicode" />\n' % (_escape(main['lastSeqDir']))
    buff += '    <param name="errorUnits" value="%s" type="str" />\n' % (main['errorUnits'])
    buff += '    <param name="printQuality" value="%d" type="int" />\n' % (main['printQuality'])
    buff += '    <param name="useServer" value="%d" type="int" />\n' % (bool(main['useServer']))
    buff += '    <param name="serverPort" value="%d" type="int" />\n' % (main['serverPort'])
    buff += '    <param name="updatesEnabled" value="%d" type="int" />\n' % (bool(main['updatesEnabled']))
    buff += '    <param name="updatesChecked" value="%s" type="str" />\n' % (main['updatesChecked'])
    buff += '    <param name="updatesCurrent" value="%s" type="str" />\n' % (main['updatesCurrent'])
    buff += '    <param name="updatesAvailable" value="%s" type="str" />\n' % (main['updatesAvailable'])
    buff += '    <param name="compassMode" value="%s" type="str" />\n' % (main['compassMode'])
    buff += '    <param name="compassFormat" value="%s" type="str" />\n' % (main['compassFormat'])
    buff += '    <param name="compassDeleteFile" value="%d" type="int" />\n' % (bool(main['compassDeleteFile']))
    buff += '  </main>\n\n'
    
    # recent files
    buff += '  <recent>\n'
    for item in recent:
        buff += '    <path value="%s" />\n' % (_escape(item))
    buff += '  </recent>\n\n'
    
    # colours
    buff += '  <colours>\n'
    for item in colours:
        buff += '    <colour value="%02x%02x%02x" />\n' % tuple(item)
    buff += '  </colours>\n\n'
    
    # export
    buff += '  <export>\n'
    buff += '    <param name="imageWidth" value="%.1f" type="float" />\n' % (export['imageWidth'])
    buff += '    <param name="imageHeight" value="%.1f" type="float" />\n' % (export['imageHeight'])
    buff += '    <param name="imageUnits" value="%s" type="str" />\n' % (export['imageUnits'])
    buff += '    <param name="imageResolution" value="%d" type="int" />\n' % (export['imageResolution'])
    buff += '    <param name="imageFontsScale" value="%d" type="int" />\n' % (export['imageFontsScale'])
    buff += '    <param name="imageDrawingsScale" value="%d" type="int" />\n' % (export['imageDrawingsScale'])
    buff += '    <param name="imageFormat" value="%s" type="str" />\n' % (export['imageFormat'])
    buff += '    <param name="peaklistColumns" value="%s" type="str" />\n' % (';'.join(export['peaklistColumns']))
    buff += '    <param name="peaklistFormat" value="%s" type="str" />\n' % (export['peaklistFormat'])
    buff += '    <param name="peaklistSeparator" value="%s" type="str" />\n' % (export['peaklistSeparator'])
    buff += '    <param name="spectrumSeparator" value="%s" type="str" />\n' % (export['spectrumSeparator'])
    buff += '  </export>\n\n'
    
    # spectrum
    buff += '  <spectrum>\n'
    buff += '    <param name="xLabel" value="%s" type="unicode" />\n' % (_escape(spectrum['xLabel']))
    buff += '    <param name="yLabel" value="%s" type="unicode" />\n' % (_escape(spectrum['yLabel']))
    buff += '    <param name="showGrid" value="%d" type="int" />\n' % (bool(spectrum['showGrid']))
    buff += '    <param name="showMinorTicks" value="%d" type="int" />\n' % (bool(spectrum['showMinorTicks']))
    buff += '    <param name="showLegend" value="%d" type="int" />\n' % (bool(spectrum['showLegend']))
    buff += '    <param name="showPosBars" value="%d" type="int" />\n' % (bool(spectrum['showPosBars']))
    buff += '    <param name="showGel" value="%d" type="int" />\n' % (bool(spectrum['showGel']))
    buff += '    <param name="showGelLegend" value="%d" type="int" />\n' % (bool(spectrum['showGelLegend']))
    buff += '    <param name="showTracker" value="%d" type="int" />\n' % (bool(spectrum['showTracker']))
    buff += '    <param name="showNotations" value="%d" type="int" />\n' % (bool(spectrum['showNotations']))
    buff += '    <param name="showDataPoints" value="%d" type="int" />\n' % (bool(spectrum['showDataPoints']))
    buff += '    <param name="showLabels" value="%d" type="int" />\n' % (bool(spectrum['showLabels']))
    buff += '    <param name="showAllLabels" value="%d" type="int" />\n' % (bool(spectrum['showAllLabels']))
    buff += '    <param name="showTicks" value="%d" type="int" />\n' % (bool(spectrum['showTicks']))
    buff += '    <param name="showCursorImage" value="%d" type="int" />\n' % (bool(spectrum['showCursorImage']))
    buff += '    <param name="posBarSize" value="%d" type="int" />\n' % (spectrum['posBarSize'])
    buff += '    <param name="gelHeight" value="%d" type="int" />\n' % (spectrum['gelHeight'])
    buff += '    <param name="autoscale" value="%d" type="int" />\n' % (bool(spectrum['autoscale']))
    buff += '    <param name="overlapLabels" value="%d" type="int" />\n' % (bool(spectrum['overlapLabels']))
    buff += '    <param name="checkLimits" value="%d" type="int" />\n' % (bool(spectrum['checkLimits']))
    buff += '    <param name="labelAngle" value="%d" type="int" />\n' % (spectrum['labelAngle'])
    buff += '    <param name="labelCharge" value="%d" type="int" />\n' % (bool(spectrum['labelCharge']))
    buff += '    <param name="labelGroup" value="%d" type="int" />\n' % (bool(spectrum['labelGroup']))
    buff += '    <param name="labelBgr" value="%d" type="int" />\n' % (bool(spectrum['labelBgr']))
    buff += '    <param name="labelFontSize" value="%d" type="int" />\n' % (spectrum['labelFontSize'])
    buff += '    <param name="axisFontSize" value="%d" type="int" />\n' % (spectrum['axisFontSize'])
    buff += '    <param name="tickColour" value="%02x%02x%02x" type="str" />\n' % tuple(spectrum['tickColour'])
    buff += '    <param name="tmpSpectrumColour" value="%02x%02x%02x" type="str" />\n' % tuple(spectrum['tmpSpectrumColour'])
    buff += '    <param name="notationMarksColour" value="%02x%02x%02x" type="str" />\n' % tuple(spectrum['notationMarksColour'])
    buff += '    <param name="notationMaxLength" value="%d" type="int" />\n' % (spectrum['notationMaxLength'])
    buff += '    <param name="notationMarks" value="%d" type="int" />\n' % (bool(spectrum['notationMarks']))
    buff += '    <param name="notationLabels" value="%d" type="int" />\n' % (bool(spectrum['notationLabels']))
    buff += '    <param name="notationMZ" value="%d" type="int" />\n' % (bool(spectrum['notationMZ']))
    buff += '  </spectrum>\n\n'
    
    # match
    buff += '  <match>\n'
    buff += '    <param name="tolerance" value="%f" type="float" />\n' % (match['tolerance'])
    buff += '    <param name="units" value="%s" type="str" />\n' % (match['units'])
    buff += '    <param name="ignoreCharge" value="%d" type="int" />\n' % (bool(match['ignoreCharge']))
    buff += '    <param name="filterAnnotations" value="%d" type="int" />\n' % (bool(match['filterAnnotations']))
    buff += '    <param name="filterMatches" value="%d" type="int" />\n' % (bool(match['filterMatches']))
    buff += '    <param name="filterUnselected" value="%d" type="int" />\n' % (bool(match['filterUnselected']))
    buff += '    <param name="filterIsotopes" value="%d" type="int" />\n' % (bool(match['filterIsotopes']))
    buff += '    <param name="filterUnknown" value="%d" type="int" />\n' % (bool(match['filterUnknown']))
    buff += '  </match>\n\n'
    
    # processing
    buff += '  <processing>\n'
    buff += '    <crop>\n'
    buff += '      <param name="lowMass" value="%d" type="int" />\n' % (processing['crop']['lowMass'])
    buff += '      <param name="highMass" value="%d" type="int" />\n' % (processing['crop']['highMass'])
    buff += '    </crop>\n'
    buff += '    <baseline>\n'
    buff += '      <param name="precision" value="%d" type="int" />\n' % (processing['baseline']['precision'])
    buff += '      <param name="offset" value="%f" type="float" />\n' % (processing['baseline']['offset'])
    buff += '    </baseline>\n'
    buff += '    <smoothing>\n'
    buff += '      <param name="method" value="%s" type="str" />\n' % (processing['smoothing']['method'])
    buff += '      <param name="windowSize" value="%f" type="float" />\n' % (processing['smoothing']['windowSize'])
    buff += '      <param name="cycles" value="%d" type="int" />\n' % (processing['smoothing']['cycles'])
    buff += '    </smoothing>\n'
    buff += '    <peakpicking>\n'
    buff += '      <param name="snThreshold" value="%f" type="float" />\n' % (processing['peakpicking']['snThreshold'])
    buff += '      <param name="absIntThreshold" value="%f" type="float" />\n' % (processing['peakpicking']['absIntThreshold'])
    buff += '      <param name="relIntThreshold" value="%f" type="float" />\n' % (processing['peakpicking']['relIntThreshold'])
    buff += '      <param name="pickingHeight" value="%f" type="float" />\n' % (processing['peakpicking']['pickingHeight'])
    buff += '      <param name="baseline" value="%d" type="int" />\n' % (bool(processing['peakpicking']['baseline']))
    buff += '      <param name="smoothing" value="%d" type="int" />\n' % (bool(processing['peakpicking']['smoothing']))
    buff += '      <param name="deisotoping" value="%d" type="int" />\n' % (bool(processing['peakpicking']['deisotoping']))
    buff += '      <param name="removeShoulders" value="%d" type="int" />\n' % (bool(processing['peakpicking']['removeShoulders']))
    buff += '    </peakpicking>\n'
    buff += '    <deisotoping>\n'
    buff += '      <param name="maxCharge" value="%d" type="int" />\n' % (processing['deisotoping']['maxCharge'])
    buff += '      <param name="massTolerance" value="%f" type="float" />\n' % (processing['deisotoping']['massTolerance'])
    buff += '      <param name="intTolerance" value="%f" type="float" />\n' % (processing['deisotoping']['intTolerance'])
    buff += '      <param name="removeIsotopes" value="%d" type="int" />\n' % (bool(processing['deisotoping']['removeIsotopes']))
    buff += '      <param name="removeUnknown" value="%d" type="int" />\n' % (bool(processing['deisotoping']['removeUnknown']))
    buff += '      <param name="labelEnvelope" value="%s" type="str" />\n' % (processing['deisotoping']['labelEnvelope'])
    buff += '      <param name="envelopeIntensity" value="%s" type="str" />\n' % (processing['deisotoping']['envelopeIntensity'])
    buff += '      <param name="setAsMonoisotopic" value="%d" type="int" />\n' % (bool(processing['deisotoping']['setAsMonoisotopic']))
    buff += '    </deisotoping>\n'
    buff += '    <deconvolution>\n'
    buff += '      <param name="massType" value="%d" type="int" />\n' % (processing['deconvolution']['massType'])
    buff += '      <param name="groupWindow" value="%f" type="float" />\n' % (processing['deconvolution']['groupWindow'])
    buff += '      <param name="groupPeaks" value="%d" type="int" />\n' % (bool(processing['deconvolution']['groupPeaks']))
    buff += '      <param name="forceGroupWindow" value="%d" type="int" />\n' % (bool(processing['deconvolution']['forceGroupWindow']))
    buff += '    </deconvolution>\n'
    buff += '    <batch>\n'
    buff += '      <param name="math" value="%d" type="int" />\n' % (bool(processing['batch']['math']))
    buff += '      <param name="crop" value="%d" type="int" />\n' % (bool(processing['batch']['crop']))
    buff += '      <param name="baseline" value="%d" type="int" />\n' % (bool(processing['batch']['baseline']))
    buff += '      <param name="smoothing" value="%d" type="int" />\n' % (bool(processing['batch']['smoothing']))
    buff += '      <param name="peakpicking" value="%d" type="int" />\n' % (bool(processing['batch']['peakpicking']))
    buff += '      <param name="deisotoping" value="%d" type="int" />\n' % (bool(processing['batch']['deisotoping']))
    buff += '      <param name="deconvolution" value="%d" type="int" />\n' % (bool(processing['batch']['deconvolution']))
    buff += '    </batch>\n'
    buff += '  </processing>\n\n'
    
    # calibration
    buff += '  <calibration>\n'
    buff += '    <param name="fitting" value="%s" type="str" />\n' % (calibration['fitting'])
    buff += '    <param name="tolerance" value="%f" type="float" />\n' % (calibration['tolerance'])
    buff += '    <param name="units" value="%s" type="str" />\n' % (calibration['units'])
    buff += '    <param name="statCutOff" value="%d" type="int" />\n' % (calibration['statCutOff'])
    buff += '  </calibration>\n\n'
    
    # sequence
    buff += '  <sequence>\n'
    buff += '    <editor>\n'
    buff += '      <param name="gridSize" value="%d" type="int" />\n' % (sequence['editor']['gridSize'])
    buff += '    </editor>\n'
    buff += '    <digest>\n'
    buff += '      <param name="maxMods" value="%d" type="int" />\n' % (sequence['digest']['maxMods'])
    buff += '      <param name="maxCharge" value="%d" type="int" />\n' % (sequence['digest']['maxCharge'])
    buff += '      <param name="massType" value="%d" type="int" />\n' % (sequence['digest']['massType'])
    buff += '      <param name="enzyme" value="%s" type="unicode" />\n' % (_escape(sequence['digest']['enzyme']))
    buff += '      <param name="miscl" value="%d" type="int" />\n' % (sequence['digest']['miscl'])
    buff += '      <param name="lowMass" value="%d" type="int" />\n' % (sequence['digest']['lowMass'])
    buff += '      <param name="highMass" value="%d" type="int" />\n' % (sequence['digest']['highMass'])
    buff += '      <param name="retainPos" value="%d" type="int" />\n' % (bool(sequence['digest']['retainPos']))
    buff += '      <param name="allowMods" value="%d" type="int" />\n' % (bool(sequence['digest']['allowMods']))
    buff += '    </digest>\n'
    buff += '    <fragment>\n'
    buff += '      <param name="maxMods" value="%d" type="int" />\n' % (sequence['fragment']['maxMods'])
    buff += '      <param name="maxCharge" value="%d" type="int" />\n' % (sequence['fragment']['maxCharge'])
    buff += '      <param name="massType" value="%d" type="int" />\n' % (sequence['fragment']['massType'])
    buff += '      <param name="fragments" value="%s" type="str" />\n' % (';'.join(sequence['fragment']['fragments']))
    buff += '      <param name="maxLosses" value="%d" type="int" />\n' % (sequence['fragment']['maxLosses'])
    buff += '      <param name="filterFragments" value="%d" type="int" />\n' % (bool(sequence['fragment']['filterFragments']))
    buff += '    </fragment>\n'
    buff += '    <search>\n'
    buff += '      <param name="maxMods" value="%d" type="int" />\n' % (sequence['search']['maxMods'])
    buff += '      <param name="charge" value="%d" type="int" />\n' % (sequence['search']['charge'])
    buff += '      <param name="massType" value="%d" type="int" />\n' % (sequence['search']['massType'])
    buff += '      <param name="enzyme" value="%s" type="unicode" />\n' % (_escape(sequence['search']['enzyme']))
    buff += '      <param name="semiSpecific" value="%d" type="int" />\n' % (bool(sequence['search']['semiSpecific']))
    buff += '      <param name="tolerance" value="%f" type="float" />\n' % (sequence['search']['tolerance'])
    buff += '      <param name="units" value="%s" type="str" />\n' % (sequence['search']['units'])
    buff += '      <param name="retainPos" value="%d" type="int" />\n' % (bool(sequence['search']['retainPos']))
    buff += '    </search>\n'
    buff += '  </sequence>\n\n'
    
    # mass calculator
    buff += '  <massCalculator>\n'
    buff += '    <param name="ionseriesAgent" value="%s" type="str" />\n' % (massCalculator['ionseriesAgent'])
    buff += '    <param name="ionseriesAgentCharge" value="%d" type="int" />\n' % (massCalculator['ionseriesAgentCharge'])
    buff += '    <param name="ionseriesPolarity" value="%d" type="int" />\n' % (massCalculator['ionseriesPolarity'])
    buff += '    <param name="patternFwhm" value="%f" type="float" />\n' % (massCalculator['patternFwhm'])
    buff += '    <param name="patternThreshold" value="%f" type="float" />\n' % (massCalculator['patternThreshold'])
    buff += '    <param name="patternShowPeaks" value="%d" type="int" />\n' % (bool(massCalculator['patternShowPeaks']))
    buff += '    <param name="patternPeakShape" value="%s" type="unicode" />\n' % (_escape(massCalculator['patternPeakShape']))
    buff += '  </massCalculator>\n\n'
    
    # mass to formula
    buff += '  <massToFormula>\n'
    buff += '    <param name="countLimit" value="%d" type="int" />\n' % (massToFormula['countLimit'])
    buff += '    <param name="massLimit" value="%d" type="int" />\n' % (massToFormula['massLimit'])
    buff += '    <param name="charge" value="%d" type="int" />\n' % (massToFormula['charge'])
    buff += '    <param name="ionization" value="%s" type="str" />\n' % (massToFormula['ionization'])
    buff += '    <param name="tolerance" value="%f" type="float" />\n' % (massToFormula['tolerance'])
    buff += '    <param name="units" value="%s" type="str" />\n' % (massToFormula['units'])
    buff += '    <param name="formulaMin" value="%s" type="str" />\n' % (massToFormula['formulaMin'])
    buff += '    <param name="formulaMax" value="%s" type="str" />\n' % (massToFormula['formulaMax'])
    buff += '    <param name="autoCHNO" value="%d" type="int" />\n' % (bool(massToFormula['autoCHNO']))
    buff += '    <param name="checkPattern" value="%d" type="int" />\n' % (bool(massToFormula['checkPattern']))
    buff += '    <param name="rules" value="%s" type="str" />\n' % (';'.join(massToFormula['rules']))
    buff += '    <param name="HCMin" value="%f" type="float" />\n' % (massToFormula['HCMin'])
    buff += '    <param name="HCMax" value="%f" type="float" />\n' % (massToFormula['HCMax'])
    buff += '    <param name="NCMax" value="%f" type="float" />\n' % (massToFormula['NCMax'])
    buff += '    <param name="OCMax" value="%f" type="float" />\n' % (massToFormula['OCMax'])
    buff += '    <param name="PCMax" value="%f" type="float" />\n' % (massToFormula['PCMax'])
    buff += '    <param name="SCMax" value="%f" type="float" />\n' % (massToFormula['SCMax'])
    buff += '    <param name="RDBEMin" value="%f" type="float" />\n' % (massToFormula['RDBEMin'])
    buff += '    <param name="RDBEMax" value="%f" type="float" />\n' % (massToFormula['RDBEMax'])
    buff += '  </massToFormula>\n\n'
    
    # mass defect plot
    buff += '  <massDefectPlot>\n'
    buff += '    <param name="yAxis" value="%s" type="str" />\n' % (massDefectPlot['yAxis'])
    buff += '    <param name="nominalMass" value="%s" type="str" />\n' % (massDefectPlot['nominalMass'])
    buff += '    <param name="kendrickFormula" value="%s" type="str" />\n' % (massDefectPlot['kendrickFormula'])
    buff += '    <param name="relIntCutoff" value="%f" type="float" />\n' % (massDefectPlot['relIntCutoff'])
    buff += '    <param name="removeIsotopes" value="%d" type="int" />\n' % (bool(massDefectPlot['removeIsotopes']))
    buff += '    <param name="ignoreCharge" value="%d" type="int" />\n' % (bool(massDefectPlot['ignoreCharge']))
    buff += '    <param name="showNotations" value="%d" type="int" />\n' % (bool(massDefectPlot['showNotations']))
    buff += '  </massDefectPlot>\n\n'
    
    # compounds search
    buff += '  <compoundsSearch>\n'
    buff += '    <param name="massType" value="%d" type="int" />\n' % (compoundsSearch['massType'])
    buff += '    <param name="maxCharge" value="%d" type="int" />\n' % (compoundsSearch['maxCharge'])
    buff += '    <param name="radicals" value="%d" type="int" />\n' % (bool(compoundsSearch['radicals']))
    buff += '    <param name="adducts" value="%s" type="str" />\n' % (';'.join(compoundsSearch['adducts']))
    buff += '  </compoundsSearch>\n\n'
    
    # peak differences
    buff += '  <peakDifferences>\n'
    buff += '    <param name="aminoacids" value="%d" type="int" />\n' % (bool(peakDifferences['aminoacids']))
    buff += '    <param name="dipeptides" value="%d" type="int" />\n' % (bool(peakDifferences['dipeptides']))
    buff += '    <param name="tolerance" value="%f" type="float" />\n' % (peakDifferences['tolerance'])
    buff += '    <param name="massType" value="%d" type="int" />\n' % (peakDifferences['massType'])
    buff += '    <param name="consolidate" value="%d" type="int" />\n' % (bool(peakDifferences['consolidate']))
    buff += '  </peakDifferences>\n\n'
    
    # compare peaklists
    buff += '  <comparePeaklists>\n'
    buff += '    <param name="tolerance" value="%f" type="float" />\n' % (comparePeaklists['tolerance'])
    buff += '    <param name="units" value="%s" type="str" />\n' % (comparePeaklists['units'])
    buff += '    <param name="ignoreCharge" value="%d" type="int" />\n' % (bool(comparePeaklists['ignoreCharge']))
    buff += '    <param name="ratioCheck" value="%d" type="int" />\n' % (bool(comparePeaklists['ratioCheck']))
    buff += '    <param name="ratioDirection" value="%d" type="int" />\n' % (comparePeaklists['ratioDirection'])
    buff += '    <param name="ratioThreshold" value="%f" type="float" />\n' % (comparePeaklists['ratioThreshold'])
    buff += '  </comparePeaklists>\n\n'
    
    # spectrum generator
    buff += '  <spectrumGenerator>\n'
    buff += '    <param name="fwhm" value="%f" type="float" />\n' % (spectrumGenerator['fwhm'])
    buff += '    <param name="points" value="%d" type="int" />\n' % (spectrumGenerator['points'])
    buff += '    <param name="noise" value="%f" type="float" />\n' % (spectrumGenerator['noise'])
    buff += '    <param name="forceFwhm" value="%d" type="int" />\n' % (bool(spectrumGenerator['forceFwhm']))
    buff += '    <param name="peakShape" value="%s" type="unicode" />\n' % (_escape(spectrumGenerator['peakShape']))
    buff += '    <param name="showPeaks" value="%d" type="int" />\n' % (bool(spectrumGenerator['showPeaks']))
    buff += '    <param name="showOverlay" value="%d" type="int" />\n' % (bool(spectrumGenerator['showOverlay']))
    buff += '  </spectrumGenerator>\n\n'
    
    # envelope fit
    buff += '  <envelopeFit>\n'
    buff += '    <param name="fit" value="%s" type="str" />\n' % (envelopeFit['fit'])
    buff += '    <param name="fwhm" value="%f" type="float" />\n' % (envelopeFit['fwhm'])
    buff += '    <param name="forceFwhm" value="%d" type="int" />\n' % (bool(envelopeFit['forceFwhm']))
    buff += '    <param name="peakShape" value="%s" type="unicode" />\n' % (_escape(envelopeFit['peakShape']))
    buff += '    <param name="autoAlign" value="%d" type="int" />\n' % (bool(envelopeFit['autoAlign']))
    buff += '    <param name="relThreshold" value="%f" type="float" />\n' % (envelopeFit['relThreshold'])
    buff += '  </envelopeFit>\n\n'
    
    # mascot
    buff += '  <mascot>\n'
    buff += '    <common>\n'
    buff += '      <param name="server" value="%s" type="unicode" />\n' % (_escape(mascot['common']['server']))
    buff += '      <param name="searchType" value="%s" type="str" />\n' % (mascot['common']['searchType'])
    buff += '      <param name="userName" value="%s" type="unicode" />\n' % (_escape(mascot['common']['userName']))
    buff += '      <param name="userEmail" value="%s" type="unicode" />\n' % (_escape(mascot['common']['userEmail']))
    buff += '      <param name="filterAnnotations" value="%d" type="int" />\n' % (bool(mascot['common']['filterAnnotations']))
    buff += '      <param name="filterMatches" value="%d" type="int" />\n' % (bool(mascot['common']['filterMatches']))
    buff += '      <param name="filterUnselected" value="%d" type="int" />\n' % (bool(mascot['common']['filterUnselected']))
    buff += '      <param name="filterIsotopes" value="%d" type="int" />\n' % (bool(mascot['common']['filterIsotopes']))
    buff += '      <param name="filterUnknown" value="%d" type="int" />\n' % (bool(mascot['common']['filterUnknown']))
    buff += '    </common>\n'
    buff += '    <pmf>\n'
    buff += '      <param name="database" value="%s" type="unicode" />\n' % (mascot['pmf']['database'])
    buff += '      <param name="taxonomy" value="%s" type="unicode" />\n' % (mascot['pmf']['taxonomy'])
    buff += '      <param name="enzyme" value="%s" type="unicode" />\n' % (mascot['pmf']['enzyme'])
    buff += '      <param name="miscleavages" value="%s" type="unicode" />\n' % (mascot['pmf']['miscleavages'])
    buff += '      <param name="fixedMods" value="%s" type="unicode" />\n' % (';'.join(mascot['pmf']['fixedMods']))
    buff += '      <param name="variableMods" value="%s" type="unicode" />\n' % (';'.join(mascot['pmf']['variableMods']))
    buff += '      <param name="hiddenMods" value="%d" type="int" />\n' % (bool(mascot['pmf']['hiddenMods']))
    buff += '      <param name="proteinMass" value="%s" type="unicode" />\n' % (mascot['pmf']['proteinMass'])
    buff += '      <param name="peptideTol" value="%s" type="unicode" />\n' % (mascot['pmf']['peptideTol'])
    buff += '      <param name="peptideTolUnits" value="%s" type="unicode" />\n' % (mascot['pmf']['peptideTolUnits'])
    buff += '      <param name="massType" value="%s" type="unicode" />\n' % (mascot['pmf']['massType'])
    buff += '      <param name="charge" value="%s" type="unicode" />\n' % (mascot['pmf']['charge'])
    buff += '      <param name="decoy" value="%d" type="int" />\n' % (bool(mascot['pmf']['decoy']))
    buff += '      <param name="report" value="%s" type="unicode" />\n' % (mascot['pmf']['report'])
    buff += '    </pmf>\n'
    buff += '    <sq>\n'
    buff += '      <param name="database" value="%s" type="unicode" />\n' % (mascot['sq']['database'])
    buff += '      <param name="taxonomy" value="%s" type="unicode" />\n' % (mascot['sq']['taxonomy'])
    buff += '      <param name="enzyme" value="%s" type="unicode" />\n' % (mascot['sq']['enzyme'])
    buff += '      <param name="miscleavages" value="%s" type="unicode" />\n' % (mascot['sq']['miscleavages'])
    buff += '      <param name="fixedMods" value="%s" type="unicode" />\n' % (';'.join(mascot['sq']['fixedMods']))
    buff += '      <param name="variableMods" value="%s" type="unicode" />\n' % (';'.join(mascot['sq']['variableMods']))
    buff += '      <param name="hiddenMods" value="%d" type="int" />\n' % (bool(mascot['sq']['hiddenMods']))
    buff += '      <param name="peptideTol" value="%s" type="unicode" />\n' % (mascot['sq']['peptideTol'])
    buff += '      <param name="peptideTolUnits" value="%s" type="unicode" />\n' % (mascot['sq']['peptideTolUnits'])
    buff += '      <param name="msmsTol" value="%s" type="unicode" />\n' % (mascot['sq']['msmsTol'])
    buff += '      <param name="msmsTolUnits" value="%s" type="unicode" />\n' % (mascot['sq']['msmsTolUnits'])
    buff += '      <param name="massType" value="%s" type="unicode" />\n' % (mascot['sq']['massType'])
    buff += '      <param name="charge" value="%s" type="unicode" />\n' % (mascot['sq']['charge'])
    buff += '      <param name="instrument" value="%s" type="unicode" />\n' % (mascot['sq']['instrument'])
    buff += '      <param name="quantitation" value="%s" type="unicode" />\n' % (mascot['sq']['quantitation'])
    buff += '      <param name="decoy" value="%d" type="int" />\n' % (bool(mascot['sq']['decoy']))
    buff += '      <param name="report" value="%s" type="unicode" />\n' % (mascot['sq']['report'])
    buff += '    </sq>\n'
    buff += '    <mis>\n'
    buff += '      <param name="database" value="%s" type="unicode" />\n' % (mascot['mis']['database'])
    buff += '      <param name="taxonomy" value="%s" type="unicode" />\n' % (mascot['mis']['taxonomy'])
    buff += '      <param name="enzyme" value="%s" type="unicode" />\n' % (mascot['mis']['enzyme'])
    buff += '      <param name="miscleavages" value="%s" type="unicode" />\n' % (mascot['mis']['miscleavages'])
    buff += '      <param name="fixedMods" value="%s" type="unicode" />\n' % (';'.join(mascot['mis']['fixedMods']))
    buff += '      <param name="variableMods" value="%s" type="unicode" />\n' % (';'.join(mascot['mis']['variableMods']))
    buff += '      <param name="hiddenMods" value="%d" type="int" />\n' % (bool(mascot['mis']['hiddenMods']))
    buff += '      <param name="peptideTol" value="%s" type="unicode" />\n' % (mascot['mis']['peptideTol'])
    buff += '      <param name="peptideTolUnits" value="%s" type="unicode" />\n' % (mascot['mis']['peptideTolUnits'])
    buff += '      <param name="msmsTol" value="%s" type="unicode" />\n' % (mascot['mis']['msmsTol'])
    buff += '      <param name="msmsTolUnits" value="%s" type="unicode" />\n' % (mascot['mis']['msmsTolUnits'])
    buff += '      <param name="massType" value="%s" type="unicode" />\n' % (mascot['mis']['massType'])
    buff += '      <param name="charge" value="%s" type="unicode" />\n' % (mascot['mis']['charge'])
    buff += '      <param name="instrument" value="%s" type="unicode" />\n' % (mascot['mis']['instrument'])
    buff += '      <param name="quantitation" value="%s" type="unicode" />\n' % (mascot['mis']['quantitation'])
    buff += '      <param name="errorTolerant" value="%d" type="int" />\n' % (bool(mascot['mis']['errorTolerant']))
    buff += '      <param name="decoy" value="%d" type="int" />\n' % (bool(mascot['mis']['decoy']))
    buff += '      <param name="report" value="%s" type="unicode" />\n' % (mascot['mis']['report'])
    buff += '    </mis>\n'
    buff += '  </mascot>\n\n'
    
    # profound
    buff += '  <profound>\n'
    buff += '    <param name="script" value="%s" type="unicode" />\n' % (_escape(profound['script']))
    buff += '    <param name="database" value="%s" type="unicode" />\n' % (profound['database'])
    buff += '    <param name="taxonomy" value="%s" type="unicode" />\n' % (profound['taxonomy'])
    buff += '    <param name="enzyme" value="%s" type="unicode" />\n' % (profound['enzyme'])
    buff += '    <param name="miscleavages" value="%s" type="unicode" />\n' % (profound['miscleavages'])
    buff += '    <param name="fixedMods" value="%s" type="unicode" />\n' % (';'.join(profound['fixedMods']))
    buff += '    <param name="variableMods" value="%s" type="unicode" />\n' % (';'.join(profound['variableMods']))
    buff += '    <param name="proteinMassLow" value="%f" type="float" />\n' % (profound['proteinMassLow'])
    buff += '    <param name="proteinMassHigh" value="%f" type="float" />\n' % (profound['proteinMassHigh'])
    buff += '    <param name="proteinPILow" value="%d" type="int" />\n' % (profound['proteinPILow'])
    buff += '    <param name="proteinPIHigh" value="%d" type="int" />\n' % (profound['proteinPIHigh'])
    buff += '    <param name="peptideTol" value="%f" type="float" />\n' % (profound['peptideTol'])
    buff += '    <param name="peptideTolUnits" value="%s" type="unicode" />\n' % (profound['peptideTolUnits'])
    buff += '    <param name="massType" value="%s" type="unicode" />\n' % (profound['massType'])
    buff += '    <param name="charge" value="%s" type="unicode" />\n' % (profound['charge'])
    buff += '    <param name="ranking" value="%s" type="unicode" />\n' % (profound['ranking'])
    buff += '    <param name="expectation" value="%f" type="float" />\n' % (profound['expectation'])
    buff += '    <param name="candidates" value="%d" type="int" />\n' % (profound['candidates'])
    buff += '    <param name="filterAnnotations" value="%d" type="int" />\n' % (bool(profound['filterAnnotations']))
    buff += '    <param name="filterMatches" value="%d" type="int" />\n' % (bool(profound['filterMatches']))
    buff += '    <param name="filterUnselected" value="%d" type="int" />\n' % (bool(profound['filterUnselected']))
    buff += '    <param name="filterIsotopes" value="%d" type="int" />\n' % (bool(profound['filterIsotopes']))
    buff += '    <param name="filterUnknown" value="%d" type="int" />\n' % (bool(profound['filterUnknown']))
    buff += '  </profound>\n\n'
    
    # protein prospector
    buff += '  <prospector>\n'
    buff += '    <common>\n'
    buff += '      <param name="script" value="%s" type="unicode" />\n' % (_escape(prospector['common']['script']))
    buff += '      <param name="searchType" value="%s" type="str" />\n' % (prospector['common']['searchType'])
    buff += '      <param name="filterAnnotations" value="%d" type="int" />\n' % (bool(prospector['common']['filterAnnotations']))
    buff += '      <param name="filterMatches" value="%d" type="int" />\n' % (bool(prospector['common']['filterMatches']))
    buff += '      <param name="filterUnselected" value="%d" type="int" />\n' % (bool(prospector['common']['filterUnselected']))
    buff += '      <param name="filterIsotopes" value="%d" type="int" />\n' % (bool(prospector['common']['filterIsotopes']))
    buff += '      <param name="filterUnknown" value="%d" type="int" />\n' % (bool(prospector['common']['filterUnknown']))
    buff += '    </common>\n'
    buff += '    <msfit>\n'
    buff += '      <param name="database" value="%s" type="unicode" />\n' % (prospector['msfit']['database'])
    buff += '      <param name="taxonomy" value="%s" type="unicode" />\n' % (prospector['msfit']['taxonomy'])
    buff += '      <param name="enzyme" value="%s" type="unicode" />\n' % (prospector['msfit']['enzyme'])
    buff += '      <param name="miscleavages" value="%s" type="unicode" />\n' % (prospector['msfit']['miscleavages'])
    buff += '      <param name="fixedMods" value="%s" type="unicode" />\n' % (';'.join(prospector['msfit']['fixedMods']))
    buff += '      <param name="variableMods" value="%s" type="unicode" />\n' % (';'.join(prospector['msfit']['variableMods']))
    buff += '      <param name="proteinMassLow" value="%s" type="unicode" />\n' % (prospector['msfit']['proteinMassLow'])
    buff += '      <param name="proteinMassHigh" value="%s" type="unicode" />\n' % (prospector['msfit']['proteinMassHigh'])
    buff += '      <param name="proteinPILow" value="%s" type="unicode" />\n' % (prospector['msfit']['proteinPILow'])
    buff += '      <param name="proteinPIHigh" value="%s" type="unicode" />\n' % (prospector['msfit']['proteinPIHigh'])
    buff += '      <param name="peptideTol" value="%s" type="unicode" />\n' % (prospector['msfit']['peptideTol'])
    buff += '      <param name="peptideTolUnits" value="%s" type="unicode" />\n' % (prospector['msfit']['peptideTolUnits'])
    buff += '      <param name="massType" value="%s" type="unicode" />\n' % (prospector['msfit']['massType'])
    buff += '      <param name="instrument" value="%s" type="unicode" />\n' % (prospector['msfit']['instrument'])
    buff += '      <param name="minMatches" value="%s" type="unicode" />\n' % (prospector['msfit']['minMatches'])
    buff += '      <param name="maxMods" value="%s" type="unicode" />\n' % (prospector['msfit']['maxMods'])
    buff += '      <param name="report" value="%s" type="unicode" />\n' % (prospector['msfit']['report'])
    buff += '      <param name="pfactor" value="%s" type="unicode" />\n' % (prospector['msfit']['pfactor'])
    buff += '    </msfit>\n'
    buff += '    <mstag>\n'
    buff += '      <param name="database" value="%s" type="unicode" />\n' % (prospector['mstag']['database'])
    buff += '      <param name="taxonomy" value="%s" type="unicode" />\n' % (prospector['mstag']['taxonomy'])
    buff += '      <param name="enzyme" value="%s" type="unicode" />\n' % (prospector['mstag']['enzyme'])
    buff += '      <param name="miscleavages" value="%s" type="unicode" />\n' % (prospector['mstag']['miscleavages'])
    buff += '      <param name="fixedMods" value="%s" type="unicode" />\n' % (';'.join(prospector['mstag']['fixedMods']))
    buff += '      <param name="variableMods" value="%s" type="unicode" />\n' % (';'.join(prospector['mstag']['variableMods']))
    buff += '      <param name="peptideTol" value="%s" type="unicode" />\n' % (prospector['mstag']['peptideTol'])
    buff += '      <param name="peptideTolUnits" value="%s" type="unicode" />\n' % (prospector['mstag']['peptideTolUnits'])
    buff += '      <param name="peptideCharge" value="%s" type="unicode" />\n' % (prospector['mstag']['peptideCharge'])
    buff += '      <param name="msmsTol" value="%s" type="unicode" />\n' % (prospector['mstag']['msmsTol'])
    buff += '      <param name="msmsTolUnits" value="%s" type="unicode" />\n' % (prospector['mstag']['msmsTolUnits'])
    buff += '      <param name="massType" value="%s" type="unicode" />\n' % (prospector['mstag']['massType'])
    buff += '      <param name="instrument" value="%s" type="unicode" />\n' % (prospector['mstag']['instrument'])
    buff += '      <param name="maxMods" value="%s" type="unicode" />\n' % (prospector['mstag']['maxMods'])
    buff += '      <param name="report" value="%s" type="unicode" />\n' % (prospector['mstag']['report'])
    buff += '    </mstag>\n'
    buff += '  </prospector>\n\n'
    
    # links
    buff += '  <links>\n'
    for name in links:
        if name not in ('mMassHomepage', 'mMassForum', 'mMassTwitter', 'mMassCite', 'mMassDonate', 'mMassDownload'):
            buff += '    <link name="%s" value="%s" />\n' % (_escape(name), _escape(links[name]))
    buff += '  </links>\n\n'
    
    buff += '</mMassConfig>'
    
    # save config file
    try:
        save = file(path, 'w')
        save.write(buff.encode("utf-8"))
        save.close()
        return True
    except:
        return False
# ----


def _getParams(sectionTag, section):
    """Get params from nodes."""
    
    if sectionTag:
        paramTags = sectionTag.getElementsByTagName('param')
        if paramTags:
            if paramTags:
                for paramTag in paramTags:
                    name = paramTag.getAttribute('name')
                    value = paramTag.getAttribute('value')
                    valueType = paramTag.getAttribute('type')
                    if name in section:
                        if valueType in ('unicode', 'str', 'float', 'int'):
                            try:
                                section[name] = eval(valueType+'(value)')
                            except:
                                pass
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



try: loadConfig()
except IOError: saveConfig()
