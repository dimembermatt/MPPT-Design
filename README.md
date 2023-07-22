# :sunny: Sunscatter MPPT-Design - Gen 2 Maximum Power Point Tracker Board

Design and documentation of a custom MPPT for LHR Solar. Created in part with
Professor Alex Hanson's ECE 394J Power Electronics Class.

---

## Repository Structure

- **datasheets** - contains datasheets for major components of the Sunscatter.
- **docs** - contains documentation on how to build, test, and use the Sunscatter.
- **fw** - contains fw that is loaded onto the Sunscatter.
  - **tests** - test programs used to characterize and validate the Sunscatter.
  - **src** - main program used to run the Sunscatter.
  - **inc** - internally developed libraries specific for the Sunscatter.
  - **lib** - third party libraries used by the Sunscatter.
- **hw**
  - **footprints** - project specfic footprint association files for the Sunscatter.
  - **models** - 3d .step files for the PCB 3d viewer.
  - **symbols** - project specific symbol files for the Sunscatter.
  - **vX_Y_Z** - frozen versioning folder for PCB production files.
  - design files
- **sim** - contains a KiCAD project of the bare DC-DC converter of the MPPT, using SPICE parts for simulation.
- **sw** - contains relevant software for operating the automated design pipeline.
  - **design_files**
  - **design_procedures**

---

## Maintainers

The current maintainer of this project is Matthew Yu as of 07/17/2023. His email
is [matthewjkyu@gmail.com](matthewjkyu@gmail.com).

Contributors to the HW and FW encompass many dedicated students, including:

- Jacob Pustilnik
- Pranav Rama
- Sharon Chen

Special thanks to Professor Gary Hallock, who supervised the development and
design of this project.

---

## Versioning

This PCB is on unified version `0.2.0`. Every time the schematic and/or layout
is updated, this version number should go up. We use [semantic
versioning](https://semver.org/) to denote between versions. See the
[changelog](./docs/CHANGELOG.md) for more details.

---

## TODO

### Documentation

### HW

### FW

### SW

### Sim