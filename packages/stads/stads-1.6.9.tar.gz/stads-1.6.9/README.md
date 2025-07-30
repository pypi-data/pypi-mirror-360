# Adaptive Sampling Algorithm for FIB-SEM and SIMS Imaging

## Abstract

We present an initial prototype of an adaptive sampling algorithm designed for sparse and adaptive scanning in Focused Ion Beam Scanning Electron Microscopy (FIB-SEM) and Secondary Ion Mass Spectrometry (SIMS) imaging. The algorithm leverages temporal coherence in time-dependent secondary electron imaging and spatial/spectral redundancy in hyperspectral imaging to enable efficient image acquisition.

Our approach aims to mitigate beam-induced damage by enabling lower dwell-time (resulting in noisy images) or sparse sampling with post-reconstruction. We evaluate random sampling techniques, including uniform and stratified methods, and compare interpolation strategies—cubic, linear, and nearest neighbour—based on reconstruction fidelity and structural similarity metrics.

---

## Installation

### Install from PyPI

```bash
pip install stads_sampler
```

---

## Usage

### 2. Running Individual Samplers

#### Uniform Sampler

```python
from stads.random_sampler import RandomSampler

mySampler = RandomSampler((1080, 1080), 10)
mySampler.get_coordinates()
```

#### Stratified Sampler

```python
from stads.stratified_sampler import StratifiedSampler

mySampler = StratifiedSampler((1080, 1080), 10)
mySampler.get_coordinates()
```

---

### 3. Running Full Adaptive Sampling Experiment

```python
from stads.stads import AdaptiveSampler

mySampler = AdaptiveSampler(
    (1080, 1080),        # Frame size
    'stratified',        # Initial sampler: 'uniform' or 'stratified'
    'linear',            # Sampling strategy: 'linear', 'exponential', etc.
    50,                  # Total sample budget
    10                   # Initial sampling rate
)

reconstructed_frames, PSNRs, SSIMs = mySampler.run()
```

---

### 4. Running Laboratory Experiments

- **Experiment 1:** Scalability test of adaptive sampler against baseline across increasing number of samples.
- **Experiment 2:** Evaluation of temporal information impact on sampling effectiveness.


#### Adaptive Sampler Test

```python
from stads.experiments import SamplingExperiments

myInstrument = SamplingExperiments((1080, 1080), 10)  # Initialize instrument
myInstrument.run_experiment1()  # Run adaptive sampling scalability test
myInstrument.run_experiment2()  # Run adaptive sampling temporal information effect
```

---

---

## License

This project is licensed under the OPINCHARGE License. See the [LICENSE](LICENSE) file for details.

---

## Contact

**Author:** Akarsh Bharadwaj  
**Email:** akarsh_sudheendra.bharadwaj@dfki.de  
**Repository:** [github.com/bharadwajakarsh/stads_adaptive_sampler](https://github.com/bharadwajakarsh/stads_adaptive_sampler)

