pyrate4site
===========

Overview
--------

**pyrate4site** is a Python wrapper for the **Rate4Site** software, originally developed by Mayrose et al. (2004). This project allows seamless integration of Rate4Site into Python-based workflows while maintaining the core functionality and structure of the original standalone program.

Rate4Site is used for site-specific evolutionary rate inference, providing valuable insights into protein and DNA sequence evolution.

### Reference:

Mayrose, I., Graur, D., Ben-Tal, N., and Pupko, T. (2004). Comparison of site-specific rate-inference methods: Bayesian methods are superior. _Molecular Biology and Evolution_, 21(9), 1781-1791. \[pdf\] \[abstract\]

Installation
------------

pyrate4site is available as a pip package and can be installed with:

`   pip install pyrate4site   `

Usage
-----

### Basic Example

    from pyrate4site import rate4site  
    res = rate4site("test.msa")  
    print(res)  
    print(type(res))   `

#### Expected Output

    [-0.18588424 -0.16839667 -0.16839667 -0.18588424 -0.14931296 -0.17047765   -0.18309921 -0.12704153 -0.16839667 -0.12704153 -0.13009988 -0.16839667   -0.19979098 -0.12717594 -0.13009988 -0.17047765 -0.13009988 -0.21543511   -0.12704153 ... ]   `

    <class 'numpy.ndarray'>
    
Features
--------

*   Provides a Pythonic interface for running Rate4Site
    
*   Returns results as a NumPy array for easy processing
    
*   Preserves the core structure of the original software
    
*   Compatible with standard sequence alignment file formats
    
*   Easily integrable into bioinformatics pipelines
    

License
-------

This project modifies and wraps around the original Rate4Site software while keeping its structure intact. Users must read and understand the original Rate4Site license terms before using this package. The license terms can be found at:

https://www.tau.ac.il/~itaymay/cp/terms.html

Author
------

pyrate4site is a community-driven project aimed at making Rate4Site more accessible within Python-based bioinformatics environments.