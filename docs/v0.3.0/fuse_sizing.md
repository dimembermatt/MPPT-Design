# Fuse Sizing

## Process for deriving system requirements

- Determine failure modes.
- Determine critical path components that shall be protected.
- Derive maximum I^{2}T support for each component short of failure.
- Determine nominal minimum fuse I^{2}T spec.

## Failure Modes

Following format: [failure] of [component], supplied by [input].

- Short of upstream power input, supplied by downstream power input.
- Short of downstream power input, supplied by upstream power input.
- Short of input zener diode, supplied by upstream or downstream power inputs.
- Short of input capacitors, supplied by upstream or downstream power inputs.
- Short of output zener diode, supplied by upstream or downstream power inputs.
- Short of output capacitors, supplied by upstream or downstream power inputs.
- Short of TVS diode, supplied by upstream or downstream power inputs.
- Short of low side FET, supplied by upstream or downstream power inputs.
- Short of high side FET, supplied by upstream or downstream power inputs.

In the event of input zener diodes, input capacitors, TVS diode, and low side
FET, downstream power input must be enabled by additional SW failure that
commands high side FET CLOSED or HW failure of high side FET short.  

Likewise, in the event of output zener diode, output capacitors, upstream power
input must be enabled by additional SW failure that commands high side FET
CLOSED or HW failure of high side FET short. 

## Critical path components

- upstream, downstream wires
    - Assume sufficient, need stranding data
    - T_MAX of 100C
- high, low side PCB traces
    - Assume sufficient, need thickness data
    - T_MAX of 100C
- high, low side FET
    - 9mO RDSON
    - T_JMAX of 150C
- inductor
    - 4.0687m, 0.192Ohm
    - T_MAX of 155C (may be less for surrounding components, i.e. bobbin, ferrite)

## Maximum I2T support for each critical path component

- assume typical T_AMB of 60C

### High side, low side PCB traces

- TODO

### High side, low side FETs

- Worst case steady state power dissipation is ~4W from both FETs operating at
  max boost (min VIN, max VOUT)
- With 20cm^2 exposed copper pour on one side, simulated combined thermal
  resistivity is 6C/W (assuming sufficient ambient air circulation)
- Expected steady state temperature rise of 24C (4W * 6C / 1W = 24C), for ambient
  steady state of 84C
- Remaining margin of 66C (150C - 84C = 66C), in the even of hard short across
  one FET, can support 11W dissipation (66C / 6C / 1W = 11W). This is 1222
  I2T (11W / 0.009Ohm = 1222 A^2s), or 35A for 1s (1222A^2s ^0.5 = 35As)
- Rule of thumb(!) derating for fuses is 25-50%, assume max derate of 50%, so
  ~600 I2T.

### Inductor

- Worst case steady state power dissipation is 1.1W operating at MPP VIN, max VOUT
- Need to determine thermal resistivity of wire
  - TODO

### Upstream, downstream wires

- TODO

## Derive nominal minimum I2T

FETs have derated I2T of 600.

## Fuse Selection

- Inrush current (input)
  - 20.2uF
  - 80V max steady state
- Inrush current (output)
  - 38.2uF
  - 150V max steady state
- acceptable inrush current
  - CGA9P3X7T2E225M250KA
    - 0.5O ESR
    - 125C T_MAX
  - A759MS186M2CAAE090
    - 0.20 ESR
    - 125C T_MAX
- Must derive rise time
  - TODO
- Fuse must have blow time longer than worst case inrush current time above
  ampere rating

- 05x20mm cartridge
- Manufacturer of preference: Littelfuse
- Littelfuse 021306.3
  - 600 I2T
  - 9.51mOhm
  - 250 VAC
  - 125C T_MAX
- 6.3A ampere rating
- 10s max blow @ 275% ampere rating
  - Expected blow is 2s (600 A^2s / (6.3A * 2.75)^2 = 2s)
- Worst case operating power loss (<5% boost, VIN~=VOUT at VIN=MPP)
  - ~6.15A -> 6.3A ampere rating
  - 100mV worst case drop at ampere rating 
  - 0.63W * 2 fuses = 1.26W