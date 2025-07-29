import os
import sys
import numpy as np
import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for tests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qixuema.plot_utils import plot_frequency_distribution


class TestPlotFrequencyDistribution:
    """Test cases for plot_frequency_distribution function."""

    def test_discrete_plot_returns_axes(self):
        data = [1, 2, 2, 3]
        ax = plot_frequency_distribution(data)
        # Should return an Axes with one bar per unique value
        assert hasattr(ax, 'patches')
        assert len(ax.patches) == 3

    def test_histogram_bins(self):
        data = np.linspace(0, 1, 100)
        ax = plot_frequency_distribution(data, discrete=False, bins=5)
        # Expect number of bars equals bins
        assert len(ax.patches) == 5

    def test_save_path(self):
        data = [1, 1, 2]
        path = "test/results/test_plot_frequency_distribution.png"
        plot_frequency_distribution(data, save_path=path, show_grid=False)
        # File should be created
        assert os.path.exists(path)

    @pytest.mark.parametrize("relative", [False, True])
    def test_relative_option(self, relative):
        data = [0, 0, 1, 1]
        path = f"test/results/test_plot_frequency_distribution_relative_{relative}.png"
        ax = plot_frequency_distribution(data, relative=relative, save_path=path, show_grid=False)
        heights = sorted([round(bar.get_height(), 2) for bar in ax.patches])
        if relative:
            assert heights == [0.5, 0.5]
        else:
            assert heights == [2, 2]

    def test_invalid_input_raises(self):
        with pytest.raises(Exception):
            plot_frequency_distribution(None)
