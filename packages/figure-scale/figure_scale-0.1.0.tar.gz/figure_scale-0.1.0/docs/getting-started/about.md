# About

The `figure-scale` library is designed to help you create publication-quality figures with precise size control in Matplotlib.
It provides a convenient way to specify figure dimensions in various units (inches, millimeters, centimeters, points, etc.) and ensures consistent sizing across different plotting contexts.

**Key Features:**

- **Multiple unit support**: Specify dimensions in inches, millimeters, centimeters, points, and more, it is extendable by custom user provided units for convenience
- **Flexible sizing**: Define figures using width/height, or width/aspect, or height/aspect
- **Easy integration**: Works seamlessly with matplotlib's existing figure creation methods
- **Context management**: Use as context managers or decorators for localized figure sizing
- **Lightweight**: Minimal dependencies, built on top of Matplotlib only

See also the blog post that inspired this package: [Publication-Quality Plots in Python with Matplotlib](https://www.fschuch.com/en/blog/2025/07/05/publication-quality-plots-in-python-with-matplotlib/). It also covers Localization, Style, Dimensions, and File Format of figures in Matplotlib.
