import sys

import xgboost

from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier

from sklearn import tree

import xml.etree.cElementTree as ET

# Parameters (AdaBoost)
#  - Node purity 
NodePurityLimit = 0.5


def build_xml_tree__AdaBoost(dt, node_id, node_pos, parent_depth, parent_elementTree):

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
        build_xml_tree__AdaBoost(dt, children_left[node_id], "l", node_depth, node_elementTree)
        build_xml_tree__AdaBoost(dt, children_right[node_id], "r", node_depth, node_elementTree)
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

def convert_bdt__AdaBoost(sklearn_bdt_clf, input_var_list, tmva_outfile_xml):

    # classificator
    clf = sklearn_bdt_clf

    if clf.n_classes_ != 2:
        sys.exit("Error: Number of classes in sklearn classifier is not equal 2.")

    # Order of variables must be _exactly_ as in the training numpy array
    # E.g.
    # var_list = [ 
    #            ('m_el_pt', 'F'),
    #            ('m_el_eta', 'F'), 
    #            ('m_el_sigd0PV', 'F'), 
    #            ('m_el_z0SinTheta', 'F'), 
    #            ('m_el_etcone20Dpt', 'F'), 
    #            ('m_el_ptcone20Dpt', 'F')
    #        ]
    var_list = input_var_list

    #  Run-time parameters
    NTrees = clf.n_estimators


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
    Option_BoostType = ET.SubElement(Options, "Option", name="BoostType", modified="Yes").text = "AdaBoost"

    # <Weights>
    Weights = ET.SubElement(MethodSetup, "Weights", NTrees=str(NTrees), AnalysisType="0")

    for idx, dt in enumerate(clf.estimators_):
        tree_weight = clf.estimator_weights_[idx]
        # <BinaryTree type="DecisionTree" boostWeight="9.2106320437773737e-01" itree="0">
        BinaryTree = ET.SubElement(Weights, "BinaryTree", type="DecisionTree", boostWeight=str(tree_weight), itree=str(idx))
        build_xml_tree__AdaBoost(dt, 0, "s", -1, BinaryTree)


    # Create XML-tree structure and save it to file
    tree = ET.ElementTree(MethodSetup)
    tree.write(tmva_outfile_xml)

def build_xml_tree__Grad(dt, node_id, node_pos, parent_depth, parent_elementTree):

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
        build_xml_tree__Grad(dt, children_left[node_id], "l", node_depth, node_elementTree)
        build_xml_tree__Grad(dt, children_right[node_id], "r", node_depth, node_elementTree)
    else:
        # leaf node
        node_depth = parent_depth + 1

        # node parameters
        pos = "s" if node_id == 0 else node_pos
        depth = node_depth
        IVar = -1

        global NodePurityLimit
        sig = value[node_id][0][0]
        #total = float(sig + bkg)
        #purity = float(sig)/total
        #nType = 1 if purity >= NodePurityLimit else -1
        purity = "0.0e+00"

        node_elementTree = ET.SubElement(parent_elementTree, "Node", pos=pos, depth=str(depth), NCoef="0", IVar=str(IVar), 
            Cut="0.0e+00", cType="1", res=str(sig), rms="0.0e+00", purity=str(purity), nType="-99")


def convert_bdt__Grad(sklearn_bdt_clf, input_var_list, tmva_outfile_xml):

    # classificator
    clf = sklearn_bdt_clf

    if clf.loss_.K != 1:
        sys.exit("Error: Only binary classification is supported for regression trees.")

    if clf.n_classes_ != 2:
        sys.exit("Error: Number of classes in sklearn classifier is not equal 2.")

    # Order of variables must be _exactly_ as in the training numpy array
    # E.g.
    # var_list = [ 
    #            ('m_el_pt', 'F'),
    #            ('m_el_eta', 'F'), 
    #            ('m_el_sigd0PV', 'F'), 
    #            ('m_el_z0SinTheta', 'F'), 
    #            ('m_el_etcone20Dpt', 'F'), 
    #            ('m_el_ptcone20Dpt', 'F')
    #        ]
    var_list = input_var_list

    #  Run-time parameters
    NTrees = clf.n_estimators


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
    Option_BoostType = ET.SubElement(Options, "Option", name="BoostType", modified="Yes").text = "Grad"

    # <Weights>
    Weights = ET.SubElement(MethodSetup, "Weights", NTrees=str(NTrees), AnalysisType="1")

    # We support only binary classification
    # from http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html
    # estimators_ : ndarray of DecisionTreeRegressor, shape = [n_estimators, loss_.K]
    #     where loss_.K is 1 for binary classification, otherwise n_classes.
    for idx, dt in enumerate(clf.estimators_[:, 0]):
        # <BinaryTree type="DecisionTree" boostWeight="9.2106320437773737e-01" itree="0">
        BinaryTree = ET.SubElement(Weights, "BinaryTree", type="DecisionTree", boostWeight="1.0e+00", itree=str(idx))
        build_xml_tree__Grad(dt, 0, "s", -1, BinaryTree)


    # Create XML-tree structure and save it to file
    tree = ET.ElementTree(MethodSetup)
    tree.write(tmva_outfile_xml)


def convert_bdt_sklearn_tmva(sklearn_bdt_clf, input_var_list, tmva_outfile_xml):

    # AdaBoost
    if isinstance(sklearn_bdt_clf, AdaBoostClassifier):
        convert_bdt__AdaBoost(sklearn_bdt_clf, input_var_list, tmva_outfile_xml)

    # Gradient Boosting (binary classification only)
    if isinstance(sklearn_bdt_clf, GradientBoostingClassifier):
        convert_bdt__Grad(sklearn_bdt_clf, input_var_list, tmva_outfile_xml)
