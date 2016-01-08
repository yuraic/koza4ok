import cPickle

from skTMVA import convert_bdt_sklearn_tmva

# load decision tree
bdt_path = '/Users/musthero/Documents/Yura/Applications/tmva_local/electrons_v5_VeryTightLH_20per.pkl'
with open(bdt_path, 'rb') as fid:
    bdt = cPickle.load(fid)

# specify input variable list
var_list = [ 
                ('m_el_pt', 'F'),
                ('m_el_eta', 'F'), 
                ('m_el_sigd0PV', 'F'), 
                ('m_el_z0SinTheta', 'F'), 
                ('m_el_etcone20Dpt', 'F'), 
                ('m_el_ptcone20Dpt', 'F')
            ]

# specify output TMVA xml-file
tmva_outfile_xml = 'SKLearn_BDT_electons.weights.xml'

# save scikit-learn trained BDT classifier to TMVA xml-file
convert_bdt_sklearn_tmva(bdt, var_list, tmva_outfile_xml)