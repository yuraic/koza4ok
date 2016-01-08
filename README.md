# koza4ok

<img width="260px" align="right" hspace="7" vspace="5" src="https://web2.ph.utexas.edu/~ilchenko/img/roc_github.png">

The package contains scikit-learn to TMVA convertor called ```skTMVA```. The idea is to save scikit-learn BDT model to the TMVA xml-file. This allows you to use scikit-learn model directly from TMVA. Once the model is trained and converted, scikit-learn library is not needed anymore! The classification task can be performed with TMVA/ROOT only. This is particularly useful within ATLAS framework where there is no scikit-learn installed. A user can train the classifier with scikit-learn on his laptop and later use in ATLAS framework converted to the TMVA xml-file. 

## Dependencies
- [ROOT](http://root.cern.ch) (with TMVA package)
- [NumPy](http://www.numpy.org/)
- [scikit-learn](http://scikit-learn.org/)


## Installation
Basically just add `koza4ok` root directory to PYTHONPATH, or do this
```
> source setup_koza4ok.sh
```

## skTMVA converter

To convert BDT to TMVA xml-file, use the following method in your <b>python</b> code (see [Examples](https://github.com/yuraic/koza4ok#examples)),
```python
convert_bdt_sklearn_tmva(bdt, [('var1', 'F'), ('var2', 'F')], 'bdt_sklearn_to_tmva_example.xml')
```

where ```bdt``` is your scikit-learn trained model, ```bdt_sklearn_to_tmva_example.xml``` is the output TMVA xml-file. ```'[('var1', 'F'), ('var2', 'F')]'``` is the input variable description for TMVA. It consists of variable names and their basic types (e.g. ```'F'``` is for float). Please note, that ordering here must be same as columns in your numpy array!

Important: at the moment the only supported boosting algorithm is AdaBoost. It's trivial to do but I have not gotten to this just yet.

## Examples

You can play with examples. They don't require to have a dataset. The dataset is generated on-fly - both signal and background follow Gaussian distribution with different mean values (thanks to [root_numpy](http://rootpy.github.io/root_numpy/, I stole this part of the code from them).

So, the example contains two files,

- [examples/bdt_sklearn_to_tmva.py ](https://github.com/yuraic/koza4ok/blob/master/examples/bdt_sklearn_to_tmva.py) - trains BDT with sklearn, converts it to TMVA xml-file, saves originally trained sklearn BDT to pickle file
- [examples/validate_sklearn_to_tmva.py](https://github.com/yuraic/koza4ok/blob/master/examples/validate_sklearn_to_tmva.py) - build two ROC-curves: one from sklearn by extracting BDT from pickle file and another from TMVA by using the reader on the input TMVA xml file from previous stage

To run it, go to ```examples``` folder and execute in the command line,

```
> python bdt_sklearn_to_tmva.py 
> python -i validate_sklearn_to_tmva.py
```

You should notice two files created - ```bdt_sklearn_to_tmva_example.pkl``` and ```bdt_sklearn_to_tmva_example.xml``` - the first one contains trained BDT model whereas the second one is TMVA xml-file. ```validate_sklearn_to_tmva.py``` uses these two files to produce and compare two ROC-curves that are produced by scikit-learn and TMVA correspondingly. If all is okay, the ROC-curves should be drawn one on top of another. The pop-up window will show up with the ROC-curve comparison.

## Contacts

If you have any question, suggestion or comment, please don't hesitate to contact me. My homepage is [https://web2.ph.utexas.edu/~ilchenko/index.html](https://web2.ph.utexas.edu/~ilchenko/index.html)



