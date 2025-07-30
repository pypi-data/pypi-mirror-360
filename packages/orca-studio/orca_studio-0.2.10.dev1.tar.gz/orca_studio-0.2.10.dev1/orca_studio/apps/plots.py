from typing import Optional

import numpy as np
import plotly.graph_objects as go
import polars as pl


def broadened_absorption_spectrum(
    bar_spectrum: pl.DataFrame,
    fwhm: float,
    energy_column: str = "energy_cm",
    intensity_column: str = "fosc",
    name_column: str = "to_state",
    grid_points: int = 500,
    grid_domain: tuple[float, float] = (0, 60_000),
    intensity_cutoff: float = 0.0,
    intensity_domain: Optional[tuple[float, float]] = None,
) -> go.Figure:
    bar_spectrum = bar_spectrum.filter(pl.col(intensity_column) >= intensity_cutoff)

    grid = np.linspace(*grid_domain, grid_points)
    _gaussians, _grid = apply_gaussian_convolution(
        bar_spectrum,
        fwhm,
        energy_column,
        intensity_column,
        name_column,
        grid=grid,
    )
    _simulated_spectrum_df = compute_total_spectrum(
        _gaussians, _grid, energy_column, intensity_column
    )

    # Create a Plotly figure
    fig = go.Figure()

    # Add individual Gaussian curves as filled areas
    for i, gaussian_df in enumerate(_gaussians):
        state_name = f"State {i}"

        fig.add_trace(
            go.Scatter(
                x=gaussian_df[energy_column],
                y=gaussian_df[intensity_column],
                mode="lines",
                name=str(state_name),
                fill="tozeroy",
                line=dict(width=0),
            )
        )

    # Add the sum as a line
    fig.add_trace(
        go.Scatter(
            x=_simulated_spectrum_df[energy_column],
            y=_simulated_spectrum_df[intensity_column],
            mode="lines",
            name="Total",
            line=dict(width=2, color="black"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=bar_spectrum[energy_column],
            y=bar_spectrum[intensity_column],
            text=bar_spectrum[name_column],
            mode="markers+text",
            textposition="bottom center",
            name="Vertical Transitions",
            marker=dict(size=6, color="black", symbol="circle"),
        )
    )

    # Configure the layout
    layout = dict(
        xaxis=dict(
            title=energy_column,
            range=grid_domain,
        ),
        yaxis=dict(
            title=intensity_column,
            range=intensity_domain,
        ),
        showlegend=True,
    )

    fig.update_layout(layout)

    return fig


def _gaussian(x: np.ndarray, fwhm: float) -> np.ndarray:
    """
    Gaussian function used for spectral broadening.

    Parameters
    ----------
    x : np.ndarray
        Energy/frequency offset relative to center.
    fwhm : float
        Full width at half maximum (FWHM) of the Gaussian.

    Returns
    -------
    np.ndarray
        Gaussian values evaluated at x.
    """
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    if sigma == 0:
        return np.zeros_like(x)
    return np.exp(-(x**2) / (2 * sigma**2))


def apply_gaussian_convolution(
    df: pl.DataFrame,
    fwhm: float,
    energy_column: str = "energy_cm",
    intensity_column: str = "fosc",
    name_column: str = "to_state",
    grid_points: int = 500,
    grid_padding: float = 2.0,
    grid: Optional[np.ndarray] = None,
) -> tuple[list[pl.DataFrame], np.ndarray]:
    """
    Apply Gaussian convolution to spectral transitions.

    Returns a new, broadened dataframe for each transition in the original and the grid used.

    Parameters
    ----------
    df : pl.DataFrame
        Input dataframe with spectral transitions
    fwhm : float
        Full width at half maximum for Gaussian broadening
    grid_points : int
        Number of points in the energy grid
    energy_column : str
        Column name for energy values
    intensity_column : str
        Column name for intensity values
    name_column : str
        Column name for identifiers
    grid_padding : float
        Padding beyond min/max energies in units of fwhm
    grid : np.ndarray, optional
        Predefined energy grid to use instead of creating one

    Returns
    -------
    Tuple[List[pl.DataFrame], np.ndarray]
        List of dataframes with convolved spectra for each transition,
        Common energy grid used for the convolution
    """
    # Create energy grid if not provided
    if grid is None:
        emin = df.select(pl.col(energy_column)).min().item() - grid_padding * fwhm
        emax = df.select(pl.col(energy_column)).max().item() + grid_padding * fwhm
        grid = np.linspace(emin, emax, grid_points)
    assert grid is not None

    # Process each transition
    convolved_dfs = []
    for row in df.iter_rows(named=True):
        # Calculate Gaussian profile for this transition
        energy0 = row[energy_column]
        intensity = row[intensity_column]

        if intensity < 1e-6:
            continue

        y = intensity * _gaussian(grid - energy0, fwhm)

        # Create dataframe for this transition (only where intensity is significant)
        df_line = pl.DataFrame(
            {
                name_column: [row[name_column]] * grid.size,
                energy_column: grid,
                intensity_column: y,
            }
        ).filter(pl.col(intensity_column) > 0)

        convolved_dfs.append(df_line)

    return convolved_dfs, grid


def compute_total_spectrum(
    convolved_spectra: list[pl.DataFrame],
    grid: np.ndarray,
    energy_column: str = "energy_cm",
    intensity_column: str = "fosc",
) -> pl.DataFrame:
    """
    Compute the overall spectrum by summing individual convolved spectra.

    Parameters
    ----------
    convolved_spectra : List[pl.DataFrame]
        List of dataframes with convolved spectra
    grid : np.ndarray
        Common energy grid used for the convolution
    energy_column : str
        Column name for energy values

    Returns
    -------
    pl.DataFrame
        Dataframe with the total spectrum
    """
    # Initialize array to hold summed intensities
    total_intensity = np.zeros_like(grid)

    # Sum up contributions from each transition
    for df in convolved_spectra:
        # Build a mapping from energy to intensity for this spectrum
        # This handles potential filtering in the individual dataframes
        energy_to_intensity = {
            e: i
            for e, i in zip(
                df.select(energy_column).to_numpy().flatten(),
                df.select(intensity_column).to_numpy().flatten(),
            )
        }

        # Add intensity at each grid point
        for i, e in enumerate(grid):
            if e in energy_to_intensity:
                total_intensity[i] += energy_to_intensity[e]

    # Create and return dataframe with total spectrum
    return pl.DataFrame({energy_column: grid, intensity_column: total_intensity})
