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

# load decision tree
print "Loading DecisionTree..."
with open('electrons_toTMVA.pkl', 'rb') as fid:
    dt = cPickle.load(fid)

n_nodes = dt.tree_.node_count
children_left = dt.tree_.children_left
children_right = dt.tree_.children_right
feature = dt.tree_.feature
threshold = dt.tree_.threshold
value = dt.tree_.value

print feature[0]
print value[0]
print threshold[0]

NodePurityLimit = 0.5

def build_xml_tree(node_id, node_pos, parent_depth, parent_elementTree):

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
        build_xml_tree(children_left[node_id], "l", node_depth, node_elementTree)
        build_xml_tree(children_right[node_id], "r", node_depth, node_elementTree)
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


BinaryTree = ET.Element("BinaryTree")
build_xml_tree(0, "s", -1, BinaryTree)

tree = ET.ElementTree(BinaryTree)
tree.write("filename.xml")


# Save to file fpr, tpr
#np.savez('output_fullsim_v3_electrons_fpr_tpr_10per.npz', 
#    fpr=fpr, tpr=tpr)