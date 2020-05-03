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
import os.path
import shutil
import xml.dom.minidom
import copy

# load modules
import config
import mspy


# ENSURE DEFAULT LIBS ARE AVAILABLE AFTER MAC INSTALLATION
# --------------------------------------------------------
if sys.platform == 'darwin':
    for item in ('monomers.xml', 'modifications.xml', 'enzymes.xml', 'presets.xml', 'references.xml', 'compounds.xml', 'mascot.xml'):
        if not os.path.exists(os.path.join(config.confdir, item)):
            try: shutil.copyfile(os.path.join('configs', item), os.path.join(config.confdir, item))
            except: pass


# LOAD USER'S LIBS INTO MSPY
# --------------------------

try: mspy.loadMonomers(os.path.join(config.confdir,'monomers.xml'), clear=False)
except: mspy.saveMonomers(os.path.join(config.confdir,'monomers.xml'))

try: mspy.loadModifications(os.path.join(config.confdir,'modifications.xml'), clear=False)
except: mspy.saveModifications(os.path.join(config.confdir,'modifications.xml'))

try: mspy.loadEnzymes(os.path.join(config.confdir,'enzymes.xml'), clear=False)
except: mspy.saveEnzymes(os.path.join(config.confdir,'enzymes.xml'))


# INIT DEFAULT VALUES
# -------------------

presets = {
    'operator':{},
    'processing':{
        'ESI-ICR Peptides':{
            'crop':{
                'lowMass': 200,
                'highMass': 4000,
            },
            'baseline':{
                'precision': 15,
                'offset': 0.25,
            },
            'smoothing':{
                'method': 'SG',
                'windowSize': 0.05,
                'cycles': 1,
            },
            'peakpicking':{
                'snThreshold': 4,
                'absIntThreshold': 0,
                'relIntThreshold': 0.001,
                'pickingHeight': 0.9,
                'baseline': 1,
                'smoothing': 0,
                'deisotoping': 1,
                'removeShoulders': 1,
            },
            'deisotoping':{
                'maxCharge': 5,
                'massTolerance': 0.005,
                'intTolerance': 0.5,
                'isotopeShift': 0.0,
                'removeIsotopes': 1,
                'removeUnknown': 1,
                'setAsMonoisotopic': 1,
                'labelEnvelope': '1st',
                'envelopeIntensity': 'maximum',
            },
            'deconvolution':{
                'massType': 0,
                'groupWindow': 0.001,
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
        },
        'MALDI-TOF Peptides':{
            'crop':{
                'lowMass': 750,
                'highMass': 4000,
            },
            'baseline':{
                'precision': 15,
                'offset': 0.25,
            },
            'smoothing':{
                'method': 'SG',
                'windowSize': 0.2,
                'cycles': 2,
            },
            'peakpicking':{
                'snThreshold': 3.5,
                'absIntThreshold': 0,
                'relIntThreshold': 0.005,
                'pickingHeight': 0.75,
                'baseline': 1,
                'smoothing': 1,
                'deisotoping': 1,
                'removeShoulders': 0,
            },
            'deisotoping':{
                'maxCharge': 1,
                'massTolerance': 0.15,
                'intTolerance': 0.5,
                'isotopeShift': 0.0,
                'removeIsotopes': 1,
                'removeUnknown': 1,
                'setAsMonoisotopic': 1,
                'labelEnvelope': '1st',
                'envelopeIntensity': 'maximum',
            },
            'deconvolution':{
                'massType': 0,
                'groupWindow': 0.05,
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
        },
        'MALDI-TOF Proteins 5-20 kDa':{
            'crop':{
                'lowMass': 5000,
                'highMass': 20000,
            },
            'baseline':{
                'precision': 20,
                'offset': 0.25,
            },
            'smoothing':{
                'method': 'MA',
                'windowSize': 5,
                'cycles': 2,
            },
            'peakpicking':{
                'snThreshold': 2.5,
                'absIntThreshold': 0,
                'relIntThreshold': 0.01,
                'pickingHeight': 0.75,
                'baseline': 1,
                'smoothing': 1,
                'deisotoping': 0,
                'removeShoulders': 0,
            },
            'deisotoping':{
                'maxCharge': 1,
                'massTolerance': 0.1,
                'intTolerance': 0.5,
                'isotopeShift': 0.0,
                'removeIsotopes': 0,
                'removeUnknown': 0,
                'setAsMonoisotopic': 0,
                'labelEnvelope': '1st',
                'envelopeIntensity': 'maximum',
            },
            'deconvolution':{
                'massType': 1,
                'groupWindow': 2.5,
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
        },
        'MALDI-TOF PSD':{
            'crop':{
                'lowMass': 0,
                'highMass': 4000,
            },
            'baseline':{
                'precision': 20,
                'offset': 0.25,
            },
            'smoothing':{
                'method': 'SG',
                'windowSize': 0.25,
                'cycles': 2,
            },
            'peakpicking':{
                'snThreshold': 3,
                'absIntThreshold': 0,
                'relIntThreshold': 0.005,
                'pickingHeight': 0.75,
                'baseline': 1,
                'smoothing': 1,
                'deisotoping': 1,
                'removeShoulders': 0,
            },
            'deisotoping':{
                'maxCharge': 1,
                'massTolerance': 0.2,
                'intTolerance': 0.5,
                'isotopeShift': 0.0,
                'removeIsotopes': 1,
                'removeUnknown': 0,
                'setAsMonoisotopic': 1,
                'labelEnvelope': '1st',
                'envelopeIntensity': 'maximum',
            },
            'deconvolution':{
                'massType': 0,
                'groupWindow': 0.1,
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
        },
        'MALDI-ICR Peptides':{
            'crop':{
                'lowMass': 750,
                'highMass': 4000,
            },
            'baseline':{
                'precision': 15,
                'offset': 0.25,
            },
            'smoothing':{
                'method': 'SG',
                'windowSize': 0.05,
                'cycles': 1,
            },
            'peakpicking':{
                'snThreshold': 4,
                'absIntThreshold': 0,
                'relIntThreshold': 0.001,
                'pickingHeight': 0.9,
                'baseline': 1,
                'smoothing': 0,
                'deisotoping': 1,
                'removeShoulders': 1,
            },
            'deisotoping':{
                'maxCharge': 1,
                'massTolerance': 0.02,
                'intTolerance': 0.5,
                'isotopeShift': 0.0,
                'removeIsotopes': 1,
                'removeUnknown': 1,
                'setAsMonoisotopic': 1,
                'labelEnvelope': '1st',
                'envelopeIntensity': 'maximum',
            },
            'deconvolution':{
                'massType': 0,
                'groupWindow': 0.001,
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
        },
        'MALDI-ICR Low Mass':{
            'crop':{
                'lowMass': 200,
                'highMass': 1500,
            },
            'baseline':{
                'precision': 15,
                'offset': 0.25,
            },
            'smoothing':{
                'method': 'SG',
                'windowSize': 0.05,
                'cycles': 1,
            },
            'peakpicking':{
                'snThreshold': 6,
                'absIntThreshold': 0,
                'relIntThreshold': 0.001,
                'pickingHeight': 0.9,
                'baseline': 1,
                'smoothing': 0,
                'deisotoping': 1,
                'removeShoulders': 1,
            },
            'deisotoping':{
                'maxCharge': 1,
                'massTolerance': 0.02,
                'intTolerance': 0.7,
                'isotopeShift': 0.0,
                'removeIsotopes': 1,
                'removeUnknown': 1,
                'setAsMonoisotopic': 1,
                'labelEnvelope': '1st',
                'envelopeIntensity': 'maximum',
            },
            'deconvolution':{
                'massType': 0,
                'groupWindow': 0.001,
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
        },
    },
    'modifications':{
        '-None-':[],
        'Carbamidomethyl (C)':[
            ['Carbamidomethyl', 'C', 'f'],
        ],
        'Oxidation (MW)':[
            ['Oxidation', 'M', 'v'],
            ['Oxidation', 'W', 'v'],
        ],
        'N-Formyl Met':[
            ['FormylMet', 0, 'v']
        ],
    },
    'fragments':{
        '-None-':[],
        'CID':['b','y','-NH3','-H2O'],
        'ECD/ETD':['c','y'],
        'ISD':['a','c','y'],
        'PSD':['a','b','y','-NH3','-H2O','im'],
        'Ladder-N':['n-ladder'],
        'Ladder-C':['c-ladder'],
    },
}

references = {
    'Trypsin (Porcine) - MALDI Pos Mo':[
        ('Trypsin (108-115) [M+H]+', 842.5094),
        ('Trypsin (209-216) [M+H]+', 906.5044),
        ('Trypsin (1-8) [M+H]+', 952.3894),
        ('Trypsin (148-157) [M+H]+', 1006.4874),
        ('Trypsin (98-107) [M+H]+', 1045.5637),
        ('Trypsin (134-147) [M+H]+', 1469.7305),
        ('Trypsin (58-72) [M+H]+', 1713.8084),
        ('Trypsin (217-231) [M+H]+', 1736.8425),
        ('Trypsin (116-133) [M+H]+', 1768.7993),
        ('Trypsin (62-77) [M+H]+', 1774.8975),
        ('Trypsin (58-76) [M+H]+', 2083.0096),
        ('Trypsin (158-178) [M+H]+', 2158.0307),
        ('Trypsin (58-77) [M+H]+', 2211.1040),
        ('Trypsin (78-97) [M+H]+', 2283.1802),
        ('Trypsin (179-208) [M+H]+', 3013.3237),
    ],
    'HCCA Clusters - MALDI Pos Mo':[
        ('HCCA [M+H-H2O]+', 172.039304),
        ('HCCA [M+H]+', 190.049869),
        ('HCCA [M+Na-H2O]+', 194.021249),
        ('HCCA [M+Na]+', 212.031814),
        ('HCCA [M+K-H2O]+', 209.995186),
        ('HCCA [M+K]+', 228.005751),
        ('HCCA [2M+H-H2O]+', 361.081897),
        ('HCCA [2M+H]+', 379.092462),
        ('HCCA [2M+Na-H2O]+', 383.063842),
        ('HCCA [2M+Na]+', 401.074407),
        ('HCCA [2M+K-H2O]+', 399.037779),
        ('HCCA [2M+K]+', 417.048344),
        ('HCCA [2M+K+Na-H2O]+', 422.027),
        ('HCCA [3M+H-H2O]+', 550.12449),
        ('HCCA [3M+H]+', 568.135055),
        ('HCCA [3M+Na-H2O]+', 572.106435),
        ('HCCA [3M+Na]+', 590.117),
        ('HCCA [3M+K-H2O]+', 588.080372),
        ('HCCA [3M+K]+', 606.090937),
        ('HCCA [3M+K+Na-H2O]+', 611.069593),
        ('HCCA [4M+H-H2O]+', 739.167083),
        ('HCCA [4M+H]+', 757.177648),
        ('HCCA [4M+Na-H2O]+', 761.149028),
        ('HCCA [4M+Na]+', 779.159593),
        ('HCCA [4M+K-H2O]+', 777.122965),
        ('HCCA [4M+K]+', 795.13353),
        ('HCCA [4M+K+Na-H2O]+', 800.112186),
        ('HCCA [5M+H-H2O]+', 928.209676),
        ('HCCA [5M+H]+', 946.220241),
        ('HCCA [5M+Na-H2O]+', 950.191621),
        ('HCCA [5M+Na]+', 968.202186),
        ('HCCA [5M+K-H2O]+', 966.165558),
        ('HCCA [5M+K]+', 984.176123),
        ('HCCA [5M+K+Na-H2O]+', 989.154779),
        ('HCCA [6M+H-H2O]+', 1117.252269),
        ('HCCA [6M+H]+', 1135.262834),
        ('HCCA [6M+Na-H2O]+', 1139.234214),
        ('HCCA [6M+Na]+', 1157.244779),
        ('HCCA [6M+K-H2O]+', 1155.208151),
        ('HCCA [6M+K]+', 1173.218716),
        ('HCCA [6M+K+Na-H2O]+', 1178.197372),
        ('HCCA [7M+H-H2O]+', 1306.294862),
        ('HCCA [7M+H]+', 1324.305427),
        ('HCCA [7M+Na-H2O]+', 1328.276807),
        ('HCCA [7M+Na]+', 1346.287372),
        ('HCCA [7M+K-H2O]+', 1344.250744),
        ('HCCA [7M+K]+', 1362.261309),
        ('HCCA [7M+K+Na-H2O]+', 1367.239965),
    ],
    'DHB Clusters - MALDI Pos Mo':[
        ('DHB [M+H-H2O]+', 137.02332),
        ('DHB [M+H]+', 155.033885),
        ('DHB [M+Na-H2O]+', 159.005265),
        ('DHB [M+Na]+', 177.01583),
        ('DHB [M+K-H2O]+', 174.979202),
        ('DHB [M+K]+', 192.989767),
        ('DHB [2M+H-2H2O]+', 273.039364),
        ('DHB [2M+H-H2O]+', 291.049929),
        ('DHB [2M+H]+', 309.060494),
        ('DHB [2M+Na-2H2O]+', 295.021309),
        ('DHB [2M+Na-H2O]+', 313.031874),
        ('DHB [2M+Na]+', 331.042439),
        ('DHB [2M+K-H2O]+', 329.005811),
        ('DHB [2M+K]+', 347.016376),
        ('DHB [2M+K+Na-H2O]+', 351.995032),
        ('DHB [3M+H-3H2O]+', 409.055408),
        ('DHB [3M+H-H2O]+', 445.076538),
        ('DHB [3M+H]+', 463.087103),
        ('DHB [3M+Na-3H2O]+', 431.037353),
        ('DHB [3M+Na-H2O]+', 467.058483),
        ('DHB [3M+Na]+', 485.069048),
        ('DHB [3M+K-H2O]+', 483.03242),
        ('DHB [3M+K]+', 501.042985),
        ('DHB [3M+K+Na-H2O]+', 506.021641),
        ('DHB [4M+H-4H2O]+', 545.071452),
        ('DHB [4M+H-H2O]+', 599.103147),
        ('DHB [4M+H]+', 617.113712),
        ('DHB [4M+Na-4H2O]+', 567.053397),
        ('DHB [4M+Na-H2O]+', 621.085092),
        ('DHB [4M+Na]+', 639.095657),
        ('DHB [4M+K-H2O]+', 637.059029),
        ('DHB [4M+K]+', 655.069594),
        ('DHB [4M+K+Na-H2O]+', 660.04825),
        ('DHB [5M+H-5H2O]+', 681.087496),
        ('DHB [5M+H-H2O]+', 753.129756),
        ('DHB [5M+H]+', 771.140321),
        ('DHB [5M+Na-H2O]+', 775.111701),
        ('DHB [5M+Na]+', 793.122266),
        ('DHB [5M+K-H2O]+', 791.085638),
        ('DHB [5M+K]+', 809.096203),
        ('DHB [5M+K+Na-H2O]+', 814.074859),
        ('DHB [6M+H-6H2O]+', 817.103540),
        ('DHB [6M+H-H2O]+', 907.156365),
        ('DHB [6M+H]+', 925.16693),
        ('DHB [6M+Na-H2O]+', 929.13831),
        ('DHB [6M+Na]+', 947.148875),
        ('DHB [6M+K-H2O]+', 945.112247),
        ('DHB [6M+K]+', 963.122812),
        ('DHB [6M+K+Na-H2O]+', 968.101468),
        ('DHB [7M+H-7H2O]+', 953.119584),
        ('DHB [7M+H-H2O]+', 1061.182974),
        ('DHB [7M+H]+', 1079.193539),
        ('DHB [7M+Na-H2O]+', 1083.164919),
        ('DHB [7M+Na]+', 1101.175484),
        ('DHB [7M+K-H2O]+', 1099.138856),
        ('DHB [7M+K]+', 1117.149421),
        ('DHB [7M+K+Na-H2O]+', 1122.128077),
    ],
    'In-Gel (Trypsin) - MALDI Pos Mo':[
        ('Keratin 10 [M+H]+', 1165.5853),
        ('Keratin 1/II [M+H]+', 1179.6010),
        ('Keratin 1/II [M+H]+', 1300.5302),
        ('Keratin 1/II [M+H]+', 1716.8517),
        ('Keratin 1/II [M+H]+', 1993.9767),
        ('Keratin 1 [M+H]+', 2383.9520),
        ('Keratin 10 [M+H]+', 2825.4056),
        ('Trypsin (108-115) [M+H]+', 842.5094),
        ('Trypsin (209-216) [M+H]+', 906.5044),
        ('Trypsin (1-8) [M+H]+', 952.3894),
        ('Trypsin (148-157) [M+H]+', 1006.4874),
        ('Trypsin (98-107) [M+H]+', 1045.5637),
        ('Trypsin (134-147) [M+H]+', 1469.7305),
        ('Trypsin (58-72) [M+H]+', 1713.8084),
        ('Trypsin (217-231) [M+H]+', 1736.8425),
        ('Trypsin (116-133) [M+H]+', 1768.7993),
        ('Trypsin (62-77) [M+H]+', 1774.8975),
        ('Trypsin (58-76) [M+H]+', 2083.0096),
        ('Trypsin (158-178) [M+H]+', 2158.0307),
        ('Trypsin (58-77) [M+H]+', 2211.1040),
        ('Trypsin (78-97) [M+H]+', 2283.1802),
        ('Trypsin (179-208) [M+H]+', 3013.3237),
    ],
}

compounds = {}

mascot = {
    'Matrix Science':{
            'protocol': 'http',
            'host': 'www.matrixscience.com',
            'path': '/',
            'search': 'cgi/nph-mascot.exe',
            'results': 'cgi/master_results.pl',
            'export': 'cgi/export_dat_2.pl',
            'params': 'cgi/get_params.pl',
    },
}


# LOAD FUNCTIONS
# --------------

def loadPresets(path=os.path.join(config.confdir, 'presets.xml'), clear=True, replace=True):
    """Parse processing presets XML and get data."""
    
    container = {}
    
    # parse XML
    document = xml.dom.minidom.parse(path)
    
    # get operator presets
    operatorTags = document.getElementsByTagName('operator')
    if operatorTags:
        presetsTags = operatorTags[0].getElementsByTagName('presets')
        if presetsTags:
            container['operator'] = {}
            
            for presetsTag in presetsTags:
                name = presetsTag.getAttribute('name')
                container['operator'][name] = {'operator':'', 'contact':'', 'institution':'', 'instrument':''}
                _getParams(presetsTag, container['operator'][name])
    
    # get processing presets
    processingTags = document.getElementsByTagName('processing')
    if processingTags:
        presetsTags = processingTags[0].getElementsByTagName('presets')
        if presetsTags:
            container['processing'] = {}
            
            for presetsTag in presetsTags:
                name = presetsTag.getAttribute('name')
                container['processing'][name] = copy.deepcopy(config.processing)
                
                cropTags = presetsTag.getElementsByTagName('crop')
                if cropTags:
                    _getParams(cropTags[0], container['processing'][name]['crop'])
                
                baselineTags = presetsTag.getElementsByTagName('baseline')
                if baselineTags:
                    _getParams(baselineTags[0], container['processing'][name]['baseline'])
                
                smoothingTags = presetsTag.getElementsByTagName('smoothing')
                if smoothingTags:
                    _getParams(smoothingTags[0], container['processing'][name]['smoothing'])
                
                peakpickingTags = presetsTag.getElementsByTagName('peakpicking')
                if peakpickingTags:
                    _getParams(peakpickingTags[0], container['processing'][name]['peakpicking'])
                
                deisotopingTags = presetsTag.getElementsByTagName('deisotoping')
                if deisotopingTags:
                    _getParams(deisotopingTags[0], container['processing'][name]['deisotoping'])
                
                deconvolutionTags = presetsTag.getElementsByTagName('deconvolution')
                if deconvolutionTags:
                    _getParams(deconvolutionTags[0], container['processing'][name]['deconvolution'])
                
                batchTags = presetsTag.getElementsByTagName('batch')
                if batchTags:
                    _getParams(batchTags[0], container['processing'][name]['batch'])
    
    # get modifications presets
    modificationsTags = document.getElementsByTagName('modifications')
    if modificationsTags:
        presetsTags = modificationsTags[0].getElementsByTagName('presets')
        if presetsTags:
            container['modifications'] = {}
            
            for presetsTag in presetsTags:
                name = presetsTag.getAttribute('name')
                container['modifications'][name] = []
                
                modificationTags = presetsTag.getElementsByTagName('modification')
                for modificationTag in modificationTags:
                    modName = modificationTag.getAttribute('name')
                    modPosition = modificationTag.getAttribute('position')
                    modType = modificationTag.getAttribute('type')
                    container['modifications'][name].append([modName, modPosition, modType])
    
    # get fragments presets
    fragmentsTags = document.getElementsByTagName('fragments')
    if fragmentsTags:
        presetsTags = fragmentsTags[0].getElementsByTagName('presets')
        if presetsTags:
            container['fragments'] = {}
            
            for presetsTag in presetsTags:
                name = presetsTag.getAttribute('name')
                container['fragments'][name] = []
                
                fragmentTags = presetsTag.getElementsByTagName('fragment')
                for fragmentTag in fragmentTags:
                    fragName = fragmentTag.getAttribute('name')
                    container['fragments'][name].append(fragName)
    
    # update current lib
    for group in container:
        if container[group] and clear:
            presets[group].clear()
        for key in container[group]:
            if replace or not key in presets[group]:
                presets[group][key] = container[group][key]
# ----


def loadReferences(path=os.path.join(config.confdir, 'references.xml'), clear=True):
    """Parse calibration references XML and get data."""
    
    container = {}
    
    # parse XML
    document = xml.dom.minidom.parse(path)
    
    # get references
    groupTags = document.getElementsByTagName('group')
    if groupTags:
        for groupTag in groupTags:
            groupName = groupTag.getAttribute('name')
            container[groupName] = []
            
            referenceTags = groupTag.getElementsByTagName('reference')
            if referenceTags:
                for referenceTag in referenceTags:
                    name = referenceTag.getAttribute('name')
                    mass = referenceTag.getAttribute('mass')
                    container[groupName].append((name, float(mass)))
    
    # update current lib
    if container and clear:
        references.clear()
    for group in container:
        references[group] = container[group]
# ----


def loadCompounds(path=os.path.join(config.confdir, 'compounds.xml'), clear=True):
    """Parse compounds XML and get data."""
    
    container = {}
    
    # parse XML
    document = xml.dom.minidom.parse(path)
    
    # get references
    groupTags = document.getElementsByTagName('group')
    if groupTags:
        for groupTag in groupTags:
            groupName = groupTag.getAttribute('name')
            container[groupName] = {}
            
            compoundTags = groupTag.getElementsByTagName('compound')
            if compoundTags:
                for compoundTag in compoundTags:
                    try:
                        name = compoundTag.getAttribute('name')
                        compound = mspy.compound(compoundTag.getAttribute('formula'))
                        compound.description = _getNodeText(compoundTag)
                        container[groupName][name] = compound
                    except:
                        pass
    
    # update current lib
    if container and clear:
        compounds.clear()
    for group in container:
        compounds[group] = container[group]
# ----


def loadMascot(path=os.path.join(config.confdir, 'mascot.xml'), clear=True, replace=True):
    """Parse mascot servers XML and get data."""
    
    container = {}
    
    # parse XML
    document = xml.dom.minidom.parse(path)
    
    # get references
    serverTags = document.getElementsByTagName('server')
    if serverTags:
        for serverTag in serverTags:
            name = serverTag.getAttribute('name')
            container[name] = {
                'protocol': 'http',
                'host': '',
                'path': '/',
                'search': 'cgi/nph-mascot.exe',
                'results': 'cgi/master_results.pl',
                'export': 'cgi/export_dat_2.pl',
                'params': 'cgi/get_params.pl',
            }
            _getParams(serverTag, container[name])
    
    # update current lib
    if container and clear:
        mascot.clear()
    for server in container:
        mascot[server] = container[server]
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

def savePresets(path=os.path.join(config.confdir, 'presets.xml')):
    """Make and save presets XML."""
    
    buff = '<?xml version="1.0" encoding="utf-8" ?>\n'
    buff += '<mMassPresets version="1.0">\n\n'
    
    # operator presets
    buff += '  <operator>\n\n'
    for name in sorted(presets['operator'].keys()):
        item = presets['operator'][name]
        buff += '    <presets name="%s">\n' % (_escape(name))
        buff += '      <param name="operator" value="%s" type="unicode" />\n' % (_escape(item['operator']))
        buff += '      <param name="contact" value="%s" type="unicode" />\n' % (_escape(item['contact']))
        buff += '      <param name="institution" value="%s" type="unicode" />\n' % (_escape(item['institution']))
        buff += '      <param name="instrument" value="%s" type="unicode" />\n' % (_escape(item['instrument']))
        buff += '    </presets>\n\n'
    buff += '  </operator>\n\n'
    
    # processing presets
    buff += '  <processing>\n\n'
    for name in sorted(presets['processing'].keys()):
        item = presets['processing'][name]
        buff += '    <presets name="%s">\n' % (_escape(name))
        buff += '      <crop>\n'
        buff += '        <param name="lowMass" value="%d" type="int" />\n' % (item['crop']['lowMass'])
        buff += '        <param name="highMass" value="%d" type="int" />\n' % (item['crop']['highMass'])
        buff += '      </crop>\n'
        buff += '      <baseline>\n'
        buff += '        <param name="precision" value="%d" type="int" />\n' % (item['baseline']['precision'])
        buff += '        <param name="offset" value="%f" type="float" />\n' % (item['baseline']['offset'])
        buff += '      </baseline>\n'
        buff += '      <smoothing>\n'
        buff += '        <param name="method" value="%s" type="str" />\n' % (item['smoothing']['method'])
        buff += '        <param name="windowSize" value="%f" type="float" />\n' % (item['smoothing']['windowSize'])
        buff += '        <param name="cycles" value="%d" type="int" />\n' % (item['smoothing']['cycles'])
        buff += '      </smoothing>\n'
        buff += '      <peakpicking>\n'
        buff += '        <param name="snThreshold" value="%f" type="float" />\n' % (item['peakpicking']['snThreshold'])
        buff += '        <param name="absIntThreshold" value="%f" type="float" />\n' % (item['peakpicking']['absIntThreshold'])
        buff += '        <param name="relIntThreshold" value="%f" type="float" />\n' % (item['peakpicking']['relIntThreshold'])
        buff += '        <param name="pickingHeight" value="%f" type="float" />\n' % (item['peakpicking']['pickingHeight'])
        buff += '        <param name="baseline" value="%d" type="int" />\n' % (bool(item['peakpicking']['baseline']))
        buff += '        <param name="smoothing" value="%d" type="int" />\n' % (bool(item['peakpicking']['smoothing']))
        buff += '        <param name="deisotoping" value="%d" type="int" />\n' % (bool(item['peakpicking']['deisotoping']))
        buff += '        <param name="removeShoulders" value="%d" type="int" />\n' % (bool(item['peakpicking']['removeShoulders']))
        buff += '      </peakpicking>\n'
        buff += '      <deisotoping>\n'
        buff += '        <param name="maxCharge" value="%d" type="int" />\n' % (item['deisotoping']['maxCharge'])
        buff += '        <param name="massTolerance" value="%f" type="float" />\n' % (item['deisotoping']['massTolerance'])
        buff += '        <param name="intTolerance" value="%f" type="float" />\n' % (item['deisotoping']['intTolerance'])
        buff += '        <param name="isotopeShift" value="%f" type="float" />\n' % (item['deisotoping']['isotopeShift'])
        buff += '        <param name="removeIsotopes" value="%d" type="int" />\n' % (bool(item['deisotoping']['removeIsotopes']))
        buff += '        <param name="removeUnknown" value="%d" type="int" />\n' % (bool(item['deisotoping']['removeUnknown']))
        buff += '        <param name="labelEnvelope" value="%s" type="str" />\n' % (item['deisotoping']['labelEnvelope'])
        buff += '        <param name="envelopeIntensity" value="%s" type="str" />\n' % (item['deisotoping']['envelopeIntensity'])
        buff += '        <param name="setAsMonoisotopic" value="%d" type="int" />\n' % (bool(item['deisotoping']['setAsMonoisotopic']))
        buff += '      </deisotoping>\n'
        buff += '      <deconvolution>\n'
        buff += '        <param name="massType" value="%d" type="int" />\n' % (item['deconvolution']['massType'])
        buff += '        <param name="groupWindow" value="%f" type="float" />\n' % (item['deconvolution']['groupWindow'])
        buff += '        <param name="groupPeaks" value="%d" type="int" />\n' % (bool(item['deconvolution']['groupPeaks']))
        buff += '        <param name="forceGroupWindow" value="%d" type="int" />\n' % (bool(item['deconvolution']['forceGroupWindow']))
        buff += '      </deconvolution>\n'
        buff += '      <batch>\n'
        buff += '        <param name="swap" value="%d" type="int" />\n' % (bool(item['batch']['swap']))
        buff += '        <param name="math" value="%d" type="int" />\n' % (bool(item['batch']['math']))
        buff += '        <param name="crop" value="%d" type="int" />\n' % (bool(item['batch']['crop']))
        buff += '        <param name="baseline" value="%d" type="int" />\n' % (bool(item['batch']['baseline']))
        buff += '        <param name="smoothing" value="%d" type="int" />\n' % (bool(item['batch']['smoothing']))
        buff += '        <param name="peakpicking" value="%d" type="int" />\n' % (bool(item['batch']['peakpicking']))
        buff += '        <param name="deisotoping" value="%d" type="int" />\n' % (bool(item['batch']['deisotoping']))
        buff += '        <param name="deconvolution" value="%d" type="int" />\n' % (bool(item['batch']['deconvolution']))
        buff += '      </batch>\n'
        buff += '    </presets>\n\n'
    buff += '  </processing>\n\n'
    
    # modifications presets
    buff += '  <modifications>\n\n'
    for name in sorted(presets['modifications'].keys()):
        buff += '    <presets name="%s">\n' % (_escape(name))
        for mod in presets['modifications'][name]:
            buff += '      <modification name="%s" position="%s" type="%s" />\n' % (mod[0], mod[1], mod[2])
        buff += '    </presets>\n\n'
    buff += '  </modifications>\n\n'
    
    # fragments presets
    buff += '  <fragments>\n\n'
    for name in sorted(presets['fragments'].keys()):
        buff += '    <presets name="%s">\n' % (_escape(name))
        for fragment in presets['fragments'][name]:
            buff += '      <fragment name="%s" />\n' % (fragment)
        buff += '    </presets>\n\n'
    buff += '  </fragments>\n\n'
    
    buff += '</mMassPresets>'
    
    # save config file
    try:
        save = file(path, 'w')
        save.write(buff.encode("utf-8"))
        save.close()
        return True
    except:
        return False
# ----


def saveReferences(path=os.path.join(config.confdir, 'references.xml')):
    """Make and save calibration references XML."""
    
    buff = '<?xml version="1.0" encoding="utf-8" ?>\n'
    buff += '<mMassReferenceMasses version="1.0">\n\n'
    
    for group in sorted(references.keys()):
        buff += '  <group name="%s">\n' % (_escape(group))
        for ref in references[group]:
            buff += '    <reference name="%s" mass="%f" />\n' % (_escape(ref[0]), ref[1])
        buff += '  </group>\n\n'
    
    buff += '</mMassReferenceMasses>'
    
    # save config file
    try:
        save = file(path, 'w')
        save.write(buff.encode("utf-8"))
        save.close()
        return True
    except:
        return False
# ----


def saveCompounds(path=os.path.join(config.confdir, 'compounds.xml')):
    """Make and save compounds XML."""
    
    buff = '<?xml version="1.0" encoding="utf-8" ?>\n'
    buff += '<mMassCompounds version="1.0">\n\n'
    
    for group in sorted(compounds.keys()):
        buff += '  <group name="%s">\n' % (_escape(group))
        for name, compound in sorted(compounds[group].items()):
            buff += '    <compound name="%s" formula="%s">%s</compound>\n' % (_escape(name), compound.expression, _escape(compound.description))
        buff += '  </group>\n\n'
    
    buff += '</mMassCompounds>'
    
    # save config file
    try:
        save = file(path, 'w')
        save.write(buff.encode("utf-8"))
        save.close()
        return True
    except:
        return False
# ----


def saveMascot(path=os.path.join(config.confdir, 'mascot.xml')):
    """Make and save mascot servers XML."""
    
    buff = '<?xml version="1.0" encoding="utf-8" ?>\n'
    buff += '<mMassMascot version="1.0">\n\n'
    
    for name in sorted(mascot.keys()):
        buff += '   <server name="%s">\n' % (_escape(name))
        buff += '     <param name="protocol" value="%s" type="unicode" />\n' % (_escape(mascot[name]['protocol']))
        buff += '     <param name="host" value="%s" type="unicode" />\n' % (_escape(mascot[name]['host']))
        buff += '     <param name="path" value="%s" type="unicode" />\n' % (_escape(mascot[name]['path']))
        buff += '     <param name="search" value="%s" type="unicode" />\n' % (_escape(mascot[name]['search']))
        buff += '     <param name="results" value="%s" type="unicode" />\n' % (_escape(mascot[name]['results']))
        buff += '     <param name="export" value="%s" type="unicode" />\n' % (_escape(mascot[name]['export']))
        buff += '     <param name="params" value="%s" type="unicode" />\n' % (_escape(mascot[name]['params']))
        buff += '   </server>\n\n'
    
    buff += '</mMassMascot>'
    
    # save config file
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



# LOAD LIBS
# ---------

try: loadPresets()
except: savePresets()

try: loadReferences()
except: saveReferences()

try: loadCompounds()
except: saveCompounds()

try: loadMascot()
except: saveMascot()
