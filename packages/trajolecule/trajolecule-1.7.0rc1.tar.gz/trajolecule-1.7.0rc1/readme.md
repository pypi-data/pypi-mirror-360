
# trajolecule: protein trajectory viewer

This viewer allows easy exploration of MD trajectories:

- hop through frames or 2d matrix view 
- easy bookmarking of specific views, frames and details
- pocket discovery tool
- ligand table against a conformation
- contact map
- inter-atomic distance plots
- port mapping for remote vm's

It also prioritises fast loading, mainly by skipping solvent
atoms as a default. Other viewers will be better for publication quality images.

It uses the jolecule javascript protein/DNA
viewer. 

## Installation

uv is the best tool to install python tooling.

Note: on Mac, there may be a slow initial startup time as Rosetta transpiles some x86 libraries to ARM

1. installing with uv to make `trajolecule` globally available:

       >> uv tool install trajolecule

2. using uv to run `trajolecule` in an isolated environment (not in the global path):

       >> uvx trajolecule

3. if you want to stay in the pip ecososystem, you can install `trajolecule` using pipx:

       >> pipx install trajolecule

4. or if you want to install `trajolecule` in your current environment:

       >> pip install trajolecule


## Examples

Once installed, check out the command-line options by running the command:

       >> trajolecule

I suggest downloading the examples to play with all the different
modes: https://github.com/boscoh/trajolecule/tree/main/examples

## Developing trajolecule

trajolecule has two components

- back-end server which is a Python fastapi backend server 
  that reads trajectories and serves it over a local port
- front-end client that runs in the browser and displays
  free-energy surfaces and proteins

## Building the trajolecule client in development mode

### Installing javascript deps

First you must install the dependencies in rseed/rseed/jolecule/vue:

    npm install

Then you must install the jolecule js repo somewhere in your system (not in the
rseed directory).

In /path/to/jolecule:

    npm link

Then in trajolecule/client:

    npm link jolecule

Once linked, we can build the client:

    npm run build

Then you need to run the build script, that will copy the client into
`sever/client`:

    ./build.sh


# Release Notes
- 1.7.0rc1
  - renamed to trajolecule
  - uv pyproject
  - file save fixes
  - ligands mode works well
- 1.6.11
  - more bug fixes
- 1.6.10
  - bug fixes for loading frames
- 1.6.9
  - multiple matrix
- 1.6.8
  - always strips water by default
- 1.6.7
  - autodetect sparse versus dense matrix
- 1.6.6
  - defaults to rshow.matrix.yaml
  - handles uploads of matrix json or plain matrix double list
  - popups on left adjusts
  - autodetects sparse versus full matrix in fes
- 1.6.5
  - consolidate with easytraj 0.2.5 and foamdb 0.4.0
- 1.6.4
  - import cleanup
  - logging
  - easytrajh5 0.2.3
- 1.6.3
  - import bus
- 1.6.2
  - alphaspace toggle bug
  - easytrajh5 bus
- 1.6
  - dep to easytrajh5
  - file_mode a/r detect
  - ensemble view
  - slideshow
- 1.5.2
  - distance plots
- 1.5
  - ligand focus
  - LRU fixed
  - select_min_frame
- 1.4
  - dry_topology streaming
  - reworked async calls
  - Alphaspace Radius UX - pockets panel
  - refactored Vue components
  - Vuex for state
  - hydrogen on/off option
  - profiling logging output
- 1.3.4
  - logging
- 1.3.3
  - removed FES remapper
- 1.3.2
  - deprecated FreeEnergySurface
- 1.3.1
  - removed foamdb as dep (creates pip install issues)
- 1.3
  - AS Communities
  - compatible with RSeed 2.2
- 1.2
    - frames in url query
- 1.1
  - alphaspace frame bug fix
- 1.0
  - first release

# TODO
- remove ensemble
- fix home page
