from array import array

import numpy as np
import matplotlib.pyplot as plt

from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import classification_report, roc_auc_score, roc_curve

from sklearn import tree
import cPickle

import xml.etree.cElementTree as ET
import sys

# load decision tree
with open('electrons_v5_VeryTightLH_20per.pkl', 'rb') as fid:
#with open('muons_v5_Tight_20per.pkl', 'rb') as fid:
    bdt = cPickle.load(fid)

clf = bdt

if clf.n_classes_ != 2:
    sys.exit("Error: Number of classes in sklearn classifier is not equal 2.")

# Order of variables must be _exactly_ as in the training numpy array
var_list = [ 
                ('m_el_pt', 'F'),
                ('m_el_eta', 'F'), 
                ('m_el_sigd0PV', 'F'), 
                ('m_el_z0SinTheta', 'F'), 
                ('m_el_etcone20Dpt', 'F'), 
                ('m_el_ptcone20Dpt', 'F')
            ]

# Parameters
#  - Node purity 
NodePurityLimit = 0.5

#  Run-time parameters
NTrees = clf.n_estimators

def build_xml_tree(dt, node_id, node_pos, parent_depth, parent_elementTree):

    n_nodes = dt.tree_.node_count
    children_left = dt.tree_.children_left
    children_right = dt.tree_.children_right
    feature = dt.tree_.feature
    threshold = dt.tree_.threshold
    value = dt.tree_.value

    if (children_left[node_id] != children_right[node_id]):    
        # intermediate node
        node_depth = parent_depth + 1

        # node parameters
        pos = "s" if node_id == 0 else node_pos
        depth = str(node_depth)
        IVar = str(feature[node_id])
        Cut = str(threshold[node_id])

        node_elementTree = ET.SubElement(parent_elementTree, "Node", pos=pos, depth=depth, NCoef="0", IVar=IVar, 
            Cut=Cut, cType="1", res="0.0e+01", rms="0.0e+00", purity="0.0e+00", nType="0")
        build_xml_tree(dt, children_left[node_id], "l", node_depth, node_elementTree)
        build_xml_tree(dt, children_right[node_id], "r", node_depth, node_elementTree)
    else:
        # leaf node
        node_depth = parent_depth + 1

        # node parameters
        pos = "s" if node_id == 0 else node_pos
        depth = node_depth
        IVar = -1

        global NodePurityLimit
        sig = value[node_id][0][1]
        bkg = value[node_id][0][0]
        total = float(sig + bkg)
        purity = float(sig)/total
        nType = 1 if purity >= NodePurityLimit else -1

        node_elementTree = ET.SubElement(parent_elementTree, "Node", pos=pos, depth=str(depth), NCoef="0", IVar=str(IVar), 
            Cut="0.0e+00", cType="1", res="0.0e+01", rms="0.0e+00", purity=str(purity), nType=str(nType))


#<MethodSetup Method="BDT::BDT">
# <GeneralInfo>
#   <Info name="Creator" value="musthero"/>
#   <Info name="AnalysisType" value="Classification"/>
# <Options>
#   <Option name="NodePurityLimit" modified="No">5.000000e-01</Option>
#<Weights NTrees="2" AnalysisType="0">
#-------------


# <MethodSetup>
MethodSetup = ET.Element("MethodSetup", Method="BDT::BDT")

#<Variables>
Variables = ET.SubElement(MethodSetup, "Variables", NVar=str(len(var_list)))
for ind, val in enumerate(var_list):
    name = val[0]
    var_type = val[1]
    Variable = ET.SubElement(Variables, "Variable", VarIndex=str(ind), Type=val[1], 
        Expression=name, Label=name, Title=name, Unit="", Internal=name, 
        Min="0.0e+00", Max="0.0e+00")

# <GeneralInfo>
GeneralInfo = ET.SubElement(MethodSetup, "GeneralInfo")
Info_Creator = ET.SubElement(GeneralInfo, "Info", name="Creator", value="Koza4ok (skTMVA)")
Info_AnalysisType = ET.SubElement(GeneralInfo, "Info", name="AnalysisType", value="Classification")

# <Options>
Options = ET.SubElement(MethodSetup, "Options")
Option_NodePurityLimit = ET.SubElement(Options, "Option", name="NodePurityLimit", modified="No").text = str(NodePurityLimit)

# <Weights>
Weights = ET.SubElement(MethodSetup, "Weights", NTrees=str(NTrees), AnalysisType="0")

for idx, dt in enumerate(clf.estimators_):
    tree_weight = clf.estimator_weights_[idx]
    # <BinaryTree type="DecisionTree" boostWeight="9.2106320437773737e-01" itree="0">
    BinaryTree = ET.SubElement(Weights, "BinaryTree", type="DecisionTree", boostWeight=str(tree_weight), itree=str(idx))
    build_xml_tree(dt, 0, "s", -1, BinaryTree)


tree = ET.ElementTree(MethodSetup)
tree.write("SKLearn_BDT_muons.weights.xml")


# Save to file fpr, tpr
#np.savez('output_fullsim_v3_electrons_fpr_tpr_10per.npz', 
#    fpr=fpr, tpr=tpr)