"""Structure learning. Given a set of data samples, estimate a DAG that captures the dependencies between the variables."""
# ------------------------------------
# Name        : structure_learning.py
# Author      : E.Taskesen
# Contact     : erdogant@gmail.com
# Licence     : See licences
# ------------------------------------


# %% Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pgmpy.estimators import ExhaustiveSearch, HillClimbSearch, TreeSearch
from pgmpy.models import NaiveBayes

import lingam

import pgmpy
from packaging import version
if version.parse(pgmpy.__version__)>=version.parse("0.1.13"):
    from pgmpy.estimators import PC as ConstraintBasedEstimator
else:
    from pgmpy.estimators import ConstraintBasedEstimator

import bnlearn


# %% Structure Learning
def fit(df,
        methodtype='hc',
        scoretype='bic',
        black_list=None,
        white_list=None,
        bw_list_method=None,
        max_indegree=None,
        tabu_length=100,
        epsilon=1e-4,
        max_iter=1e6,
        root_node=None,
        class_node=None,
        fixed_edges=None,
        return_all_dags=False,
        params_lingam = {'random_state': None, 'prior_knowledge': None, 'apply_prior_knowledge_softly': False, 'measure': 'pwling'},
        params_pc = {'ci_test': 'chi_square', 'alpha': 0.05},
        n_jobs=-1,
        verbose=3,
        ):
    """Structure learning fit model.

    Search strategies for structure learning
    The search space of DAGs is super-exponential in the number of variables and the above scoring functions allow for local maxima.

    To learn model structure (a DAG) from a data set, there are three broad techniques:
        1. Score-based structure learning: using scoring functions as defined in scoretype and search strategy as defined in methodtype.
        2. Constraint-based structure learning (PC): Using statistics such as chi-square test for strength of edges prior the modeling.
        3. Hybrid structure learning (The combination of both techniques)

    Score-based Structure Learning
    ------------------------------
    This approach performes model selection as an optimization task. It has two building blocks:
    A scoring function sD:->R that maps models to a numerical score, based on how well they fit to a given data set D.
    A search strategy to traverse the search space of possible models M and select a model with optimal score.
    Commonly used scoring functions to measure the fit between model and data are Bayesian Dirichlet scores such as BDeu or K2 and the Bayesian Information Criterion (BIC, also called MDL).
    BDeu is dependent on an equivalent sample size.

    The BDs score is determined by adjusting certain settings based on the size of the dataset and the observed
    variable counts. This adjustment involves using a value called "equivalent sample size" divided by the number of
    parent configurations with observed variable counts. The score-method evaluates how effectively a model can describe the provided dataset.

    The Direct-LiNGAM method or also named 'direct-lingam' is a semi-parametric approach that assumes a linear relationship among observed variables while ensuring that the error terms follow a non-Gaussian distribution, with the constraint that the graph remains acyclic. 
    Or in other words, the lingam-direct method allows you to model continuous and mixed datasets.

    Parameters
    ----------
    df : pd.DataFrame()
        Input dataframe.
    methodtype : str, (default : 'hc')
        String Search strategy for structure_learning.
        # Constraintsearch
        'pc' or 'cs' or 'constraintsearch'
        # Score-Based
        'ex' or 'exhaustivesearch'
        'hc' or 'hillclimbsearch' (default)
        # Score-Based: Requires Root Node
        'cl' or 'chow-liu' (requires setting root_node parameter)
        'nb' or 'naivebayes' (requires <root_node>)
        'tan' (requires <root_node> and <class_node> parameter)
        # Score-Based: For continuous and mixed datasets
        'direct-lingam'
        'ica-lingam'
    scoretype : str, (default : 'bic')
        Scoring function for the search spaces.
            * 'bic'
            * 'k2'
            * 'bdeu'
            * 'bds'
            * 'aic'
    black_list : List or None, (default : None)
        List of edges are black listed.
        In case of filtering on nodes, the nodes black listed nodes are removed from the dataframe. The resulting model will not contain any nodes that are in black_list.
    white_list : List or None, (default : None)
        List of edges are white listed.
        In case of filtering on nodes, the search is limited to those edges. The resulting model will then only contain nodes that are in white_list.
        Works only in case of methodtype='hc' See also paramter: `bw_list_method`
    bw_list_method : list of str or tuple, (default : None)
        A list of edges can be passed as `black_list` or `white_list` to exclude or to limit the search.
            * 'edges' : [('A', 'B'), ('C','D'), (...)] This option is limited to only methodtype='hc'
            * 'nodes' : ['A', 'B', ...] Filter the dataframe based on the nodes for `black_list` or `white_list`. Filtering can be done for every methodtype/scoretype.
    max_indegree : int, (default : None)
        If provided and unequal None, the procedure only searches among models where all nodes have at most max_indegree parents. (only in case of methodtype='hc')
    epsilon: float (default: 1e-4)
        Defines the exit condition. If the improvement in score is less than `epsilon`, the learned model is returned. (only in case of methodtype='hc')
    max_iter: int (default: 1e6)
        The maximum number of iterations allowed. Returns the learned model when the number of iterations is greater than `max_iter`. (only in case of methodtype='hc')
    root_node: String. (only in case of chow-liu, Tree-augmented Naive Bayes (TAN))
        The root node for treeSearch based methods.
    class_node: String
        The class node is required for Tree-augmented Naive Bayes (TAN)
    fixed_edges: iterable, Only in case of HillClimbSearch.
        A list of edges that will always be there in the final learned model. The algorithm will add these edges at the start of the algorithm and will never change it.
    return_all_dags : Bool, (default: False)
        True: Return all possible DAGs. Only in case methodtype='exhaustivesearch'
        False: Do not return DAGs
    params_lingam : dict: {'random_state': None, 'prior_knowledge': None, 'apply_prior_knowledge_softly': False, 'measure': 'pwling'}
        prior_knowledge : array-like, shape (n_features, n_features), optional (default=None)
            Prior knowledge used for causal discovery, where ``n_features`` is the number of features.
        apply_prior_knowledge_softly : boolean, optional (default=False)
            If True, apply prior knowledge softly.
        measure : String: (default='pwling')
            For fast execution with GPU, 'pwling_fast' can be used (culingam is required).
            'pwling', 'kernel', 'pwling_fast'
    params_pc : dict: {'ci_test': 'chi_square', 'alpha': 0.05}
        * 'ci_test': 'chi_square', 'pearsonr', 'g_sq', 'log_likelihood', 'freeman_tuckey', 'modified_log_likelihood', 'neyman', 'cressie_read', 'power_divergence'
        * 'alpha': 0.05
    verbose : int, (default : 3)
        0: None, 1: Error,  2: Warning, 3: Info (default), 4: Debug, 5: Trace

    Returns
    -------
    dict with keys:
        'model' : pgmpy model
        'model_edges' : Edges
        'adjmat' : Adjacency matrix
        'config' : Configurations
        'structure_scores' : Structure scores (the lower the better)

    Examples
    --------
    >>> # Import bnlearn
    >>> import bnlearn as bn
    >>>
    >>> # Load DAG
    >>> model = bn.import_DAG('asia')
    >>>
    >>> # plot ground truth
    >>> G = bn.plot(model)

    Examples
    --------
    >>> # Sampling example
    >>>
    >>> # Load DAG
    >>> model = bn.import_DAG('asia')
    >>> # Sampling
    >>> df = bn.sampling(model, n=10000)
    >>>
    >>> # Structure learning of sampled dataset
    >>> model_sl = bn.structure_learning.fit(df, methodtype='hc', scoretype='bic')
    >>>
    >>> # Compute edge strength using chi-square independence test
    >>> model_sl = bn.independence_test(model_sl, df)
    >>>
    >>> # Plot based on structure learning of sampled data
    >>> bn.plot(model_sl, pos=G['pos'])

    Examples
    --------
    >>> # Compare networks and make plot
    >>> bn.compare_networks(model, model_sl, pos=G['pos'])

    Examples
    --------
    >>> # Model mixed data sets (both discrete and continuous variables)
    >>>
    >>> # Load DAG
    >>> df = bn.import_example(data='auto_mpg')
    >>>
    >>> # Structure learning of sampled dataset
    >>> model = bn.structure_learning.fit(df, methodtype='direct-lingam')
    >>>
    >>> # Compute edge strength using chi-square independence test
    >>> model = bn.independence_test(model_sl, df)
    >>>
    >>> # Plot based on structure learning of sampled data
    >>> bn.plot(model_sl, pos=G['pos'])

    References
    ----------
        * [1] Scutari, Marco. An Empirical-Bayes Score for Discrete Bayesian Networks. Journal of Machine Learning Research, 2016, pp. 438–48
        * [2] Shimizu et al, DirectLiNGAM: A direct method for learning a linear non-Gaussian structural equation model, https://arxiv.org/abs/1101.2489v3

    """
    # Default LiNGAM
    defaults_lingam = {'random_state': None, 'prior_knowledge': None, 'apply_prior_knowledge_softly': False, 'measure': 'pwling'}
    params_lingam = {**defaults_lingam, **params_lingam}
    # Default PC
    defaults_pc = {'ci_test': 'chi_square', 'alpha': 0.05}
    params_pc = {**defaults_pc, **params_pc}

    out = []
    # Set config
    config = {'method': methodtype, 'scoring': scoretype, 'black_list': black_list, 'white_list': white_list, 'bw_list_method': bw_list_method, 'max_indegree': max_indegree, 'tabu_length': tabu_length, 'epsilon': epsilon, 'max_iter': max_iter, 'root_node': root_node, 'class_node': class_node, 'fixed_edges': fixed_edges, 'return_all_dags': return_all_dags, 'n_jobs': n_jobs, 'verbose': verbose}
    # Make some checks
    config = _make_checks(df, config, verbose=verbose)
    # Make sure columns are of type string
    df.columns = df.columns.astype(str)
    # Filter on white_list and black_list
    df = _white_black_list_filter(df, white_list, black_list, bw_list_method=config['bw_list_method'], verbose=verbose)
    # Lets go!
    if config['verbose']>=3: print('[bnlearn] >Computing best DAG using [%s]' %(config['method']))

    # ExhaustiveSearch can be used to compute the score for every DAG and returns the best-scoring one:
    if config['method']=='nb' or config['method']=='naivebayes':
        out = _naivebayes(df,
                          root_node=config['root_node'],
                          estimator_type=None,
                          feature_vars=None,
                          dependent_var=None,
                          n_jobs=config['n_jobs'],
                          verbose=config['verbose'])

    # ExhaustiveSearch can be used to compute the score for every DAG and returns the best-scoring one:
    if config['method']=='ex' or config['method']=='exhaustivesearch':
        out = _exhaustivesearch(df,
                                scoretype=config['scoring'],
                                return_all_dags=config['return_all_dags'],
                                n_jobs=config['n_jobs'],
                                verbose=config['verbose'])

    # HillClimbSearch
    if config['method']=='hc' or config['method']=='hillclimbsearch':
        out = _hillclimbsearch(df,
                               scoretype=config['scoring'],
                               black_list=config['black_list'],
                               white_list=config['white_list'],
                               max_indegree=config['max_indegree'],
                               tabu_length=config['tabu_length'],
                               bw_list_method=bw_list_method,
                               epsilon=config['epsilon'],
                               max_iter=config['max_iter'],
                               fixed_edges=config['fixed_edges'],
                               n_jobs=config['n_jobs'],
                               verbose=config['verbose'],
                               )

    # Constraint-based Structure Learning
    if config['method']=='cs' or config['method']=='constraintsearch' or config['method']=='pc':
        """Constraint-based Structure Learning
        A different, but quite straightforward approach to build a DAG from data is this:
        Identify independencies in the data set using hypothesis tests
        Construct DAG (pattern) according to identified independencies (Conditional) Independence Tests
        Independencies in the data can be identified using chi_square conditional independence tests."""
        out = _constraintsearch(df, n_jobs=config['n_jobs'], significance_level=params_pc['alpha'], ci_test=params_pc['ci_test'], verbose=config['verbose'])

    # TreeSearch-based Structure Learning
    if config['method']=='chow-liu' or config['method']=='tan':
        """TreeSearch based Structure Learning."""
        out = _treesearch(df, config['method'], config['root_node'], class_node=config['class_node'], n_jobs=config['n_jobs'], verbose=config['verbose'])

    # LiNGAM-based Structure Learning
    if config['method']=='direct-lingam' or config['method']=='ica-lingam':
        """LiNGAM-direct Structure Learning."""
        out = _lingam(df, config, n_jobs=config['n_jobs'], verbose=config['verbose'], **params_lingam)
        # return
        return out

    # Store
    out['model_edges'] = list(out['model'].edges())
    out['adjmat'] = bnlearn.dag2adjmat(out['model'])
    out['config'] = config
    out['structure_scores'] = bnlearn.structure_scores(out, df, verbose=verbose)

    # return
    return out


# %% Make Checks
def _make_checks(df, config, verbose=3):
    assert isinstance(pd.DataFrame(), type(df)), 'df must be of type pd.DataFrame()'
    if not np.isin(config['scoring'], ['bic', 'k2', 'bdeu', 'bds', 'aic']): raise Exception('"scoretype=%s" is invalid.' %(config['scoring']))
    if not np.isin(config['method'], ['ica-lingam', 'direct-lingam', 'naivebayes', 'nb', 'tan', 'cl', 'chow-liu', 'hc', 'ex', 'cs', 'pc', 'exhaustivesearch', 'hillclimbsearch', 'constraintsearch']): raise Exception('"methodtype=%s" is invalid.' %(config['method']))

    if isinstance(config['white_list'], str):
        config['white_list'] = [config['white_list']]
    if isinstance(config['black_list'], str):
        config['black_list'] = [config['black_list']]

    if (config['white_list'] is not None) and len(config['white_list'])==0:
        config['white_list'] = None
    if (config['black_list'] is not None) and len(config['black_list'])==0:
        config['black_list'] = None

    if (config['method']!='hc') and (config['bw_list_method']=='edges'): raise Exception('[bnlearn] >The "bw_list_method=%s" does not work with "methodtype=%s"' %(config['bw_list_method'], config['method']))
    if (config['method']=='tan') and (config['class_node'] is None): raise Exception('[bnlearn] >The treeSearch method TAN requires setting the <class_node> parameter: "%s"' %(str(config['class_node'])))
    if ((config['method']=='nb') | (config['method']=='naivebayes')) and (config['root_node'] is None): raise Exception('[bnlearn] >The <%s> method requires setting the "root_node" parameter: "%s"' %(config['method'], str(config['class_node'])))

    if config['method']=='cl':
        config['method'] = 'chow-liu'
    if config['fixed_edges'] is None:
        config['fixed_edges']=set()

    # Remove this block in future (21-10-2021)
    if config['bw_list_method']=='filter':
        if verbose>=2: print('[bnlearn] >Warning: The parameter bw_list_method="filter" is changed into bw_list_method="nodes". The old naming will be removed in future releases.')
        config['bw_list_method'] = "nodes"
    if config['bw_list_method']=='enforce':
        if verbose>=2: print('[bnlearn] >Warning: The parameter bw_list_method="enforce" is changed into bw_list_method="edges". The old naming will be removed in future releases.')
        config['bw_list_method'] = "edges"
    # End remove block

    # Show warnings
    if (config['bw_list_method'] is None) and ((config['black_list'] is not None) or (config['white_list'] is not None)):
        raise Exception('[bnlearn] >Error: The use of black_list or white_list requires setting bw_list_method.')
    if df.shape[1]>10 and df.shape[1]<15:
        if verbose>=2: print('[bnlearn] >Warning: Computing DAG with %d nodes can take a very long time!' %(df.shape[1]))
    if (config['max_indegree'] is not None) and config['method']!='hc':
        if verbose>=2: print('[bnlearn] >Warning: max_indegree only works in case of methodtype="hc"')
    if (config['class_node'] is not None) and config['method']!='tan':
        if verbose>=2: print('[bnlearn] >Warning: max_indegree only works in case of methodtype="tan"')

    return config


# %% TreeSearch methods
def _naivebayes(df, root_node, estimator_type=None, feature_vars=None, dependent_var=None, n_jobs=-1, verbose=3):
    """Naive Bayesian model.

    Description
    -----------
    Naive Bayes is a special case of Bayesian Model where the only edges in the
    model are from the feature variables to the dependent variable.

    Parameters
    ----------
    df : pandas DataFrame object
        A DataFrame object with column names same as the variable names of network.
    root_node : str
        Parent node of the model.
    estimator_type : TYPE, optional
        Any pgmpy estimator. If nothing is specified, the default ``MaximumLikelihoodEstimator`` would be used.
        * 'MaximumLikelihoodEstimator' (default)
        * 'BayesianEstimator'
    feature_vars: list (array-like)
        A list of variable predictor variables (i.e. the features) in the model.
    dependent_var: hashable object
        The dependent variable (i.e. the variable to be predicted) in the model.
    verbose : int, (default : 3)
        0:None, 1:Error, 2:Warning, 3:Info (default), 4:Debug, 5:Trace

    Returns
    -------
    None.

    References
    ----------
    * https://pgmpy.org/models/naive.html
    * https://pgmpy.org/_modules/pgmpy/models/NaiveBayes.html#NaiveBayes

    """
    if verbose>=4 and n_jobs>0: print('[bnlearn] >n_jobs is not supported for [NaiveBayes]')
    model = NaiveBayes(feature_vars=feature_vars, dependent_var=dependent_var)
    model.fit(df, parent_node=root_node, estimator=estimator_type)

    # Store
    out = {}
    out['model']=model
    # Return
    return(out)


# %% white_list and black_list
def _white_black_list_filter(df, white_list, black_list, bw_list_method='edges', verbose=3):
    if bw_list_method=='nodes':
        # Keep only variables that are in white_list.
        if white_list is not None:
            if verbose>=3: print('[bnlearn] >Filter variables (nodes) on white_list..')
            white_list = [x.lower() for x in white_list]
            Iloc = np.isin(df.columns.str.lower(), white_list)
            df = df.loc[:, Iloc]

        # Exclude variables that are in black_list.
        if black_list is not None:
            if verbose>=3: print('[bnlearn] >Filter variables (nodes) on black_list..')
            black_list = [x.lower() for x in black_list]
            Iloc = ~np.isin(df.columns.str.lower(), black_list)
            df = df.loc[:, Iloc]

        if (white_list is not None) or (black_list is not None):
            if verbose>=3: print('[bnlearn] >Number of features after white/black listing: %d' %(df.shape[1]))
        if df.shape[1]<=1: raise Exception('[bnlearn] >Error: [%d] variables are remaining. A minimum of 2 would be nice.' %(df.shape[1]))
    return df


# %% TreeSearch methods
def _treesearch(df, estimator_type, root_node, class_node=None, n_jobs=-1, verbose=3):
    """Tree search methods.

    Description
    -----------
    The TreeSearch methods Chow-liu and TAN (Tree-augmented Naive Bayes)
    searches for DAGs with attempts to find a model with optimal score.

    """
    out={}
    est = TreeSearch(df, root_node=root_node, n_jobs=n_jobs)
    model = est.estimate(estimator_type=estimator_type, class_node=class_node)

    # Store
    out['model']=model
    # Return
    return(out)


# %% Constraint-based Structure Learning
def _constraintsearch(df, significance_level=0.05, ci_test='chi_square', n_jobs=-1, verbose=3):
    """Contrain search.

    PC PDAG construction is only guaranteed to work under the assumption that the
    identified set of independencies is *faithful*, i.e. there exists a DAG that
    exactly corresponds to it. Spurious dependencies in the data set can cause
    the reported independencies to violate faithfulness. It can happen that the
    estimated PDAG does not have any faithful completions (i.e. edge orientations
    that do not introduce new v-structures). In that case a warning is issued.

    test_conditional_independence() returns a tripel (chi_square, p_value, sufficient_data),
    consisting in the computed chi_square test statistic, the p_value of the test, and a heuristig
    flag that indicates if the sample size was sufficient.
    The p_value is the probability of observing the computed chi_square statistic (or an even higher chi_square value),
    given the null hypothesis that X and Y are independent given Zs.
    This can be used to make independence judgements, at a given level of significance.

    DAG (pattern) construction
    With a method for independence testing at hand, we can construct a DAG from the data set in three steps:
        1. Construct an undirected skeleton - `estimate_skeleton()`
        2. Orient compelled edges to obtain partially directed acyclid graph (PDAG; I-equivalence class of DAGs) - `skeleton_to_pdag()`
        3. Extend DAG pattern to a DAG by conservatively orienting the remaining edges in some way - `pdag_to_dag()`

    ci_test:
        "chi_square"
        "independence_match"
        "pearsonr"
        "g_sq"
        "log_likelihood"
        "freeman_tuckey"
        "modified_log_likelihood"
        "neyman"
        "cressie_read"
        "power_divergence"

    """
    if verbose>=4 and n_jobs>0: print('[bnlearn] >n_jobs is not supported for [constraintsearch]')
    if verbose>=3: print(f'[bnlearn] >Build skeleton with [{ci_test}] and alpha={significance_level}')
    out = {}
    # Set search algorithm
    model = ConstraintBasedEstimator(df)

    # Estimate using chi_square
    skel, seperating_sets = model.build_skeleton(significance_level=significance_level, ci_test=ci_test)

    if verbose>=4: print("Undirected edges: ", skel.edges())
    pdag = model.skeleton_to_pdag(skel, seperating_sets)
    if verbose>=4: print("PDAG edges: ", pdag.edges())
    dag = pdag.to_dag()
    if verbose>=4: print("DAG edges: ", dag.edges())

    out['undirected'] = skel
    out['undirected_edges'] = skel.edges()
    out['pdag'] = pdag
    out['pdag_edges'] = pdag.edges()
    out['dag'] = dag
    out['dag_edges'] = dag.edges()

    # Search using "estimate()" method provides a shorthand for the three steps above and directly returns a "BayesianNetwork"
    best_model = model.estimate(significance_level=significance_level)
    out['model'] = best_model

    if verbose>=4: print(best_model.edges())
    return out


# %% hillclimbsearch
def _hillclimbsearch(df, scoretype='bic', black_list=None, white_list=None, max_indegree=None, tabu_length=100, epsilon=1e-4, max_iter=1e6, bw_list_method='edges', fixed_edges=set(), n_jobs=-1, verbose=3):
    """Heuristic hill climb searches for DAGs, to learn network structure from data. `estimate` attempts to find a model with optimal score.

    Description
    -----------
    Performs local hill climb search to estimates the `DAG` structure
    that has optimal score, according to the scoring method supplied in the constructor.
    Starts at model `start` and proceeds by step-by-step network modifications
    until a local maximum is reached. Only estimates network structure, no parametrization.

    Once more nodes are involved, one needs to switch to heuristic search.
    HillClimbSearch implements a greedy local search that starts from the DAG
    "start" (default: disconnected DAG) and proceeds by iteratively performing
    single-edge manipulations that maximally increase the score.
    The search terminates once a local maximum is found.

    For details on scoring see Koller & Friedman, Probabilistic Graphical Models, Section 18.4.3.3 (page 818).
    If a number `max_indegree` is provided, only modifications that keep the number
    of parents for each node below `max_indegree` are considered. A list of
    edges can optionally be passed as `black_list` or `white_list` to exclude those
    edges or to limit the search.

    """
    if verbose >= 4 and n_jobs > 0: print('[bnlearn] >n_jobs is not supported for [hillclimbsearch]')
    out = {}
    # Set scoring type
    scoring_method = _SetScoringType(df, scoretype, verbose=verbose)
    # Set search algorithm
    model = HillClimbSearch(df)

    # Compute best DAG
    if bw_list_method=='edges':
        if (black_list is not None) or (white_list is not None):
            if verbose >= 3: print('[bnlearn] >Filter edges based on black_list/white_list')
        # best_model = model.estimate()
        best_model = model.estimate(scoring_method=scoring_method, max_indegree=max_indegree, tabu_length=tabu_length, epsilon=epsilon, max_iter=max_iter, black_list=black_list, white_list=white_list, fixed_edges=fixed_edges, show_progress=False)
    else:
        # At this point, variables are readily filtered based on bw_list_method or not (if nothing defined).
        best_model = model.estimate(scoring_method=scoring_method, max_indegree=max_indegree, tabu_length=tabu_length, epsilon=epsilon, max_iter=max_iter, fixed_edges=fixed_edges, show_progress=False)

    # Store
    out['model'] = best_model
    # Return
    return out


# %% ExhaustiveSearch
def _exhaustivesearch(df, scoretype='bic', return_all_dags=False, n_jobs=-1, verbose=3):
    """Exhaustivesearch.

    Description
    ------------
    The first property makes exhaustive search intractable for all but very
    small networks, the second prohibits efficient local optimization
    algorithms to always find the optimal structure. Thus, identifiying the
    ideal structure is often not tractable. Despite these bad news, heuristic
    search strategies often yields good results if only few nodes are involved
    (read: less than 5).

    Parameters
    ----------
    df : pandas DataFrame object
        A DataFrame object with column names same as the variable names of network.
    scoretype : str, (default : 'bic')
        Scoring function for the search spaces.
        'bic', 'k2', 'bdeu'
    return_all_dags : Bool, (default: False)
        Return all possible DAGs.
    verbose : int, (default : 3)
        0:None, 1:Error, 2:Warning, 3:Info (default), 4:Debug, 5:Trace

    Returns
    -------
    None.

    """
    if df.shape[1] > 15 and verbose >= 3:
        print('[bnlearn] >Warning: Structure learning with more then 15 nodes is computationally not feasable with exhaustivesearch. Use hillclimbsearch or constraintsearch instead!')  # noqa
    if verbose >= 4 and n_jobs > 0: print('[bnlearn] >n_jobs is not supported for [exhaustivesearch]')

    out = {}
    # Set scoring type
    scoring_method = _SetScoringType(df, scoretype, verbose=verbose)
    # Exhaustive search across all dags
    model = ExhaustiveSearch(df, scoring_method=scoring_method)
    # Compute best DAG
    best_model = model.estimate()
    # Store
    out['model'] = best_model

    # Compute all possible DAGs
    if return_all_dags:
        out['scores'] = []
        out['dag'] = []
        # print("\nAll DAGs by score:")
        for [score, dag] in reversed(model.all_scores()):
            out['scores'].append(score)
            out['dag'].append(dag)
            # print(score, dag.edges())

        plt.plot(out['scores'])
        plt.show()

    return out


# %% Set scoring type
def _SetScoringType(df, scoretype, verbose=3, **kwargs):
    """Set scoring function.

    Parameters
    ----------
    df : pandas DataFrame object
        dataframe object where each column represents one variable.
        (If some values in the data are missing the data cells should be set to `numpy.NaN`.
        Note that pandas converts each column containing `numpy.NaN`s to dtype `float`.)
    scoretype : string
        Name of the scoring type method.
            * bic
            * k2
            * bdue
            * bds
            * aic
    verbose : int, (default : 3)
        0:None, 1:Error, 2:Warning, 3:Info (default), 4:Debug, 5:Trace

    Returns
    -------
    scoring method initialized with parameters.

    References
    ----------
        * [1] Scutari, Marco. An Empirical-Bayes Score for Discrete Bayesian Networks. Journal of Machine Learning Research, 2016, pp. 438–48

    """
    if verbose>=3: print('[bnlearn] >Set scoring type at [%s]' %(scoretype))

    if scoretype=='bic':
        scoring_method = pgmpy.estimators.BicScore(df)
    elif scoretype=='k2':
        scoring_method = pgmpy.estimators.K2Score(df)
    elif scoretype=='bdeu':
        scoring_method = pgmpy.estimators.BDeuScore(df, equivalent_sample_size=5)
    elif scoretype=='bds':
        scoring_method = pgmpy.estimators.BDsScore(df, equivalent_sample_size=5)
    elif scoretype=='aic':
        scoring_method = pgmpy.estimators.AICScore(df)


    return(scoring_method)


# %%
def _is_independent(model, X, Y, Zs=[], significance_level=0.05):
    return model.test_conditional_independence(X, Y, Zs)[1] >= significance_level


# %%
def _lingam(df,
            config,
            n_jobs=-1,
            verbose=3,
            random_state=None,
            prior_knowledge=None,
            apply_prior_knowledge_softly=False,
            measure='pwling',
            ):
    """Construct a DirectLiNGAM model

    Description
    -----------
    The Direct-LiNGAM method or 'direct-lingam' is a semi-parametric approach that assumes a linear relationship among observed variables while ensuring that the error terms follow a non-Gaussian distribution, with the constraint that the graph remains acyclic. 
    This method involves repeated regression analysis and independence assessments using linear regression with least squares. In each regression, one variable serves as the dependent variable (outcome), while the other acts as the independent variable (predictor). This process is applied to each type of variable.
    When regression analysis is conducted in the correct causal order, the independent variables and error terms will exhibit independence. Conversely, if the regression is performed under an incorrect causal order, the independence of the explanatory variables and error terms is disrupted. By leveraging the dependency properties (where both residuals and explanatory variables share common error terms), it becomes possible to infer the causal order among the variables.
    Furthermore, for a given observed variable, any explanatory variable that remains independent of the residuals, regardless of the other variables considered, can be inferred as the first in the causal hierarchy.
    Or in other words, the lingam-direct method allows you to model continuous and mixed datasets.

    Parameters
    ----------
    random_state : int, optional (default=None)
        ``random_state`` is the seed used by the random number generator.
    prior_knowledge : array-like, shape (n_features, n_features), optional (default=None)
        Prior knowledge used for causal discovery, where ``n_features`` is the number of features.

        The elements of prior knowledge matrix are defined as follows [1]_:

        * ``0`` : :math:`x_i` does not have a directed path to :math:`x_j`
        * ``1`` : :math:`x_i` has a directed path to :math:`x_j`
        * ``-1`` : No prior knowledge is available to know if either of the two cases above (0 or 1) is true.
    apply_prior_knowledge_softly : boolean, optional (default=False)
        If True, apply prior knowledge softly.
    measure : {'pwling', 'kernel', 'pwling_fast'}, optional (default='pwling')
        Measure to evaluate independence: 'pwling' [2]_ or 'kernel' [1]_.
        For fast execution with GPU, 'pwling_fast' can be used (culingam is required).
    """
    out = {}

    # To run causal discovery, we create a DirectLiNGAM object and call the fit method.
    if config['method'] == 'direct-lingam':
        model = lingam.DirectLiNGAM(random_state=random_state, prior_knowledge=prior_knowledge, apply_prior_knowledge_softly=apply_prior_knowledge_softly, measure=measure)
    elif config['method'] == 'ica-lingam':
        model = lingam.ICALiNGAM(random_state=random_state)

    # Fit
    model.fit(df)

    # Also, using the adjacency_matrix_ properties, we can see the adjacency matrix as a result of the causal discovery.
    adjmat = pd.DataFrame(model.adjacency_matrix_.T, columns=df.columns.values, index=df.columns.values)
    adjmat.index.name = 'source'
    adjmat.columns.name = 'target'

    # Compute edges
    # out['model_edges'] = bnlearn.adjmat2vec(adjmat, min_weight=0, rem_weight=0, absolute=True)
    out['model_edges'] = bnlearn.adjmat2vec(adjmat.abs()>0)
    out['model_edges'] = list(zip(out['model_edges']['source'], out['model_edges']['target']))

    # Using the causal_order_ properties,
    # we can see the causal ordering as a result of the causal discovery.
    out['model'] = model
    out['adjmat'] = adjmat
    out['causal_order'] = list(df.columns[model.causal_order_])
    out['structure_scores'] = None
    out['config'] = config

    # Return
    return out
