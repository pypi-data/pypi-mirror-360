<img alt="Shows the CASM logo" src="https://raw.githubusercontent.com/prisms-center/CASMcode_global/main/python/doc/_static/logo.svg" width="600" />

#### libcasm-clexulator

The libcasm-clexulator package is the CASM cluster expansion calculator (clexulator) module. This includes:

- A data structure (`ConfigDoFValues`) for representing degrees of freedom (DoF) in
  a configuration
- Neighbor list generation
- Methods for evaluating cluster expansion basis functions and cluster expansion values
- Methods for evaluating order parameters

This package does not include cluster expansion basis function generation, but uses basis functions that have been generated elsewhere (i.e. `casm bset`) and written as CASM Clexulator source code.


#### Install

    pip install libcasm-clexulator


#### Usage

See the [libcasm docs](https://prisms-center.github.io/CASMcode_pydocs/libcasm/overview/latest/).


#### About CASM

The libcasm-clexulator package is part of the [CASM](https://prisms-center.github.io/CASMcode_docs/) open source software package, which is designed to perform first-principles statistical mechanical studies of multi-component crystalline solids.

CASM is developed by the Van der Ven group, originally at the University of Michigan and currently at the University of California Santa Barbara.

For more information, see the [CASM homepage](https://prisms-center.github.io/CASMcode_docs/).


#### License

GNU Lesser General Public License (LGPL). Please see the file LICENSE for details.

