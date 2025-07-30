# Alexandria

**Alexandria** is a Python package for Bayesian time-series econometrics applications. This is the second official release of the software, which introduces Bayesian vector autorgressions.

From version 0.1, Alexandria offers a range of Bayesian linear regression models:

- maximum likelihood / OLS regression (non-Bayesian)
- simple Bayesian regression
- hierarchical (natural conjugate) Bayesian regression
- independent Bayesian regression with Gibbs sampling
- heteroscedastic Bayesian regression
- autocorrelated Bayesian regression

The current version adds a large number of Bayesian vector autoregression models and applications:

- maximum likelihood (OLS) VAR
- Litterman Minnesota prior
- normal-Wishart prior
- independent prior with Gibbs sampling
- dummy observation prior
- large Bayeisian VAR prior
- Bayesian oxy-SVAR

prior customization:
- constrained coefficients
- dummy extensions (sums-of-coefficients, initial observation,long-run prior)
- stationary priors
- hyperparameter optimization from marginal likelihood

structural identification:
- holesky
- triangular factorization
- restrictions:  sign and zero restrictions on IRFs, narrative on shocks and historical decomposition

applications:
- forecasts
- impulse response function
- forecast error variance decomposition
- historical decomposition
- conditional forecasts (agnostic and sctructural approaches, allowing for hard and soft conditions)


Alexandria is user-friendly and can be used from a simple Graphical User Inteface (GUI). More experienced users can also run the models directly from the Python console by using the model classes and methods.

===============================

**Installing Alexandria**

Alexandria can be installed from pip: 

	pip install alexandria-python

A local installation can also obtain by copy-pasting the folder containing the toolbox programmes. The folder can be downloaded from the project website or Github repo:  
https://alexandria-toolbox.github.io  
https://github.com/alexandria-toolbox  

===============================

**Getting started**

Simple Python example:

	# imports
	from alexandria import NormalWishartBayesianVar
	from alexandria import DataSets
	from alexandria import Graphics
	import numpy as np

	# load ISLM dataset
	ds = DataSets()
	islm_data = ds.load_islm()[:,:4]

	# create and train Bayesian VAR with default settings
	var = NormalWishartBayesianVar(endogenous = islm_data)
	var.estimate()

	# estimate forecasts for the next 4 periods, 60% credibility level
	forecast_estimates = var.forecast(4, 0.6)

	# create graphics of predictions
	gp = Graphics(var)
	gp.forecast_graphics(show=True, save=False)

===============================

**Documentation**

Complete manuals and user guides can be found on the project website and Github repo:  
https://alexandria-toolbox.github.io  
https://github.com/alexandria-toolbox  

===============================

**Contact**

alexandria.toolbox@gmail.com
