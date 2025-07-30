# Dense Curves

Simple and efficient implementations of space-filling / Peano / FASS curves.

## Installation

The package is available on pypi:

```python
pip install -U densecurves
```

## Hilbert Curve

### Nomenclature

The Hilbert curve is a finite approximation of a space filling curve.

The curve of order $p$ and rank $n$ is characteristized by:

- $n$ distinct axes, the number of coordinates of its points
- $2 \^ {p}$, the dimension along each axis
- $2 \^ {p n}$ vertexes, the "corners" of its graph

The order of the curve $p$ is often referred to as the "iteration".

The intermediate points between the vertexes are ignored.
Here, the vertexes are represented by integer coordinates.

### Load

```python
import densecurves.hilbert
```

### Compute

Convert a position / distance along the 1D curve to a ND point:

```python
densecurves.hilbert.point(position=42, order=4, rank=2)
# [7, 7]
```

And the reverse operation:

```python
densecurves.hilbert.position(coords=[1, 2, 3], order=4, rank=3)
# 36
```

## Credits

"[Programming the Hilbert curve][paper-hilbert]" by John Skilling.

## License

Licensed under the [aGPLv3](LICENSE.md).

[paper-hilbert]: https://pubs.aip.org/aip/acp/article-abstract/707/1/381/719611/Programming-the-Hilbert-curve
