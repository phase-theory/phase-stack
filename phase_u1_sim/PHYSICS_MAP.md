# Physics map

This file maps the package modules to the minimal U(1) phase-functional program.

| Concept | Package object | Operational meaning |
|---|---|---|
| Compact phase field | `theta` arrays | U(1)-valued phase variable on a periodic lattice |
| Phase inconsistency | `U1Model.energy` | Lattice functional `I[theta]` |
| Consistency update | `U1Model.relax` | Gradient-flow relaxation with optional stochastic drive |
| Topological defect | `plaquette_winding` | Integer winding around a lattice plaquette |
| Defect spectrum proxy | `count_vortices` | Total, positive, negative, and net vortex counts |
| Coherence/correlation | `phase_correlation` | Spatial decay of phase alignment |
| Emergent dimension proxy | `spectral_dimension_from_random_walk` | Heat-kernel return-probability estimate |
| Coherent propagating mode | `simulate_linear_wave` | Linearized small-amplitude phase wave dispersion |

## Kill criteria for this implementation

The implementation should be treated as failed if:

1. zero-noise relaxation routinely increases `I[theta]` at small `dt`;
2. periodic random fields do not conserve net winding globally;
3. defect counts are unstable under small perturbations away from branch cuts;
4. the linearized dispersion does not recover `omega ~ c k` at low `k`;
5. the unstrained spectral-dimension baseline does not approach 2 on a 2D lattice.

These failures would invalidate this computational instantiation, not automatically the broader theory.
