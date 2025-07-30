# ℹ️ About

A Python library for modeling, simulation, and optimization of process systems based on ordinary differential equations (ODEs).

The library allows users to define ODE systems through text files or docstrings, solve them using numerical integration, visualize results, and perform parameter optimization against experimental data. It also includes common error metrics for model evaluation.

# 📖 Documentation

You can view the example and the API reference [here](#). Features are being gradually added to the documentation

# 📦 Where to get it

The source code is currently hosted on GitHub at: [kuka_lib](https://github.com/tenoriolms/procmodeling_lib)

Binary installers for the latest released version are available at the Python Package Index (PyPI):

```bash
pip install procmodeling
```

## 🚀 Basic Usage

```python
from procmodeling_lib import edo_functions

# Load system from text file
edo = edo_functions('equations.txt')

# Visualize the system
edo.show_equations()

# Solve the system
edo.solve(t_span=[0, 10], y0=[1.0, 0.0])

# Optimize parameters
edo.optimize(
    data=my_dataframe,
    initial_values_columns=['A', 'B'],
    target_values_columns=['A', 'B'],
    time_column='time',
    bounds={'k1': (0, 1), 'k2': (0, 1)}
)
```

## Built With

This library was built using and inspired by the following amazing open-source projects:

- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [SciPy](https://scipy.org/)
- [Matplotlib](https://matplotlib.org/)
- [tqdm](https://tqdm.github.io/)

Thank you to the authors and contributors of these projects!

*For issues, suggestions, or contributions, feel free to open an issue or pull request.*

