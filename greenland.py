#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module produces GHF prediction and associated maps for Greenland. Main
functions are:
- plot_training_GHF(train_lons, train_lats, train_ghfs),
- plot_gaussian_prescribed_GHF(lons, lats, ghfs),
- plot_prediction_points(lons, lats, ghfs),
- plot_prediction(lons, lats, ghfs),
- plot_prediction_interpolated(lons, lats, ghfs)

If run as main, runs all above using data provided in global and gris data sets
(cf. `util.greenland_train_test_sets`).
"""
from mpl_toolkits.basemap import Basemap
from circles import equi
from util import (
    plt,
    np,
    save_cur_fig,
    train_gbrt,
    train_linear,
    plot_values_on_map,
    plot_values_on_map_pcolormesh,
    plot_values_on_map_pcolormesh_interp,
    plot_test_pred_linregress,
    plot_values_histogram,
    MAX_ICE_CORE_DIST,
    greenland_train_test_sets,
    fill_in_greenland_GHF,
    load_gris_data,
    GREENLAND,
    SPECTRAL_CMAP,
)
GREENLAND_BASEMAP_ARGS = {
    'lon_0': -41.5,
    'lat_0': 72,
    'lat_ts': 71,
    'width': 1600000,
    'height': 2650000,
    'resolution': 'l',
    'projection': 'stere'
}

def _mark_ice_cores(m, lons, lats, ghfs):
    colorbar_args = {'location': 'right', 'pad': '5%'}
    scatter_args = {'marker': 's', 's': 45, 'lw': 1, 'cmap': SPECTRAL_CMAP, 'edgecolor':'white'}
    plot_values_on_map(m, lons, lats, ghfs,
                       parallel_step=5., meridian_step=10.,
                       colorbar_args=colorbar_args, scatter_args=scatter_args)

def _mark_ice_core_gaussians(m, cores):
    for _, core in cores.iterrows():
        equi(m, core['lon'], core['lat'], MAX_ICE_CORE_DIST,
             lw=2, linestyle='-', color='black', alpha=.3)


def plot_training_GHF(lons, lats, ghfs):
    """ Plots all global training data on a map centered at Greenland
        and restricted to NA-WE and marks the circles used to prescribe GHF
        around GrIS ice cores. Ice core coordinates and radii are read from
        `util.GREENLAND`.

        Args:
            lons: one-dimensional list (native, numpy, or pandas) of longitudes.
            lons: similar, latitudes.
            ghfs: similar, GHF values.
    """
    m = Basemap(width=6500000, height=6500000, projection='aeqd', lon_0=-37.64, lat_0=72.58)
    _mark_ice_core_gaussians(m, GREENLAND)

    # plot all known GHF values
    colorbar_args = {'location': 'bottom', 'pad': '10%'}
    scatter_args = {'marker': 'o', 's': 15, 'lw': 0, 'cmap': SPECTRAL_CMAP}
    plot_values_on_map(m, lons, lats, ghfs,
                       parallel_step=5., meridian_step=15.,
                       colorbar_args=colorbar_args, scatter_args=scatter_args)


def plot_gaussian_prescribed_GHF(lons, lats, ghfs):
    """ Plots prescribed GHF values around GrIS ice cores and marks each
        individual ice core. All given (lon, lat, ghf) values are plotted but
        the map is restricted to Greenland alone. Ice core coordinates and
        radii are read from `util.GREENLAND`.

        Args:
            lons: one-dimensional list (native, numpy, or pandas) of longitudes.
            lons: similar, latitudes.
            ghfs: similar, GHF values.
    """
    args = GREENLAND_BASEMAP_ARGS.copy()
    args['height'] = 2800000
    args['lat_0'] = 71.5

    m = Basemap(**args)
    _mark_ice_cores(m, GREENLAND.lon.as_matrix(), GREENLAND.lat.as_matrix(),
                    GREENLAND.ghf.as_matrix())
    _mark_ice_core_gaussians(m, GREENLAND)

    # plot all known GHFs, only prescribed Greenland values being visible in
    # the frame defined by GREENLAND_BASEMAP_ARGS.
    colorbar_args = {'location': 'right', 'pad': '5%'}
    scatter_args = {'marker': 'o', 's': 18, 'lw': 0, 'cmap': SPECTRAL_CMAP}
    plot_values_on_map(m, lons, lats, ghfs, parallel_step=5., meridian_step=10.,
                       colorbar_args=colorbar_args, scatter_args=scatter_args)


def plot_prediction_points(lons, lats, ghfs):
    """ Plots predicted GHF values as colored points on a map of Greenland.

        Args:
            lons: one-dimensional list (native, numpy, or pandas) of longitudes.
            lons: similar, latitudes.
            ghfs: similar, GHF values.
    """
    m = Basemap(**GREENLAND_BASEMAP_ARGS)
    seismic_cmap = plt.get_cmap('seismic', 20)
    scatter_args = {'marker': 'o', 's': 20, 'lw': 0, 'cmap': SPECTRAL_CMAP}
    colorbar_args = {'location': 'right', 'pad': '5%'}
    plot_values_on_map(m, lons, lats, ghfs, parallel_step=5., meridian_step=10.,
                       colorbar_args=colorbar_args, scatter_args=scatter_args)


def plot_prediction(lons, lats, ghfs):
    """ Plots predicted GHF values as a pseudocolor plot for Greenland.

        Args:
            lons: one-dimensional list (native, numpy, or pandas) of longitudes.
            lons: similar, latitudes.
            ghfs: similar, GHF values.
    """
    m = Basemap(**GREENLAND_BASEMAP_ARGS)
    pcolor_args = {'cmap': SPECTRAL_CMAP}
    colorbar_args = {'location': 'right', 'pad': '5%'}
    plot_values_on_map_pcolormesh(m, lons, lats, ghfs,
                                  parallel_step=5., meridian_step=10.,
                                  colorbar_args=colorbar_args,
                                  pcolor_args=pcolor_args)


def plot_prediction_interpolated(lons, lats, ghfs):
    """ Plots predicted GHF values as an interpolated pseudocolor plot for
        Greenland.

        Args:
            lons: one-dimensional list (native, numpy, or pandas) of longitudes.
            lons: similar, latitudes.
            ghfs: similar, GHF values.
    """
    m = Basemap(**GREENLAND_BASEMAP_ARGS)
    _mark_ice_cores(m, GREENLAND.lon.as_matrix(), GREENLAND.lat.as_matrix(),
                    GREENLAND.ghf.as_matrix())
    pcolor_args = {'cmap': SPECTRAL_CMAP}
    colorbar_args = {'location': 'right', 'pad': '5%'}
    plot_values_on_map_pcolormesh_interp(m, lons, lats, ghfs,
                                         parallel_step=5., meridian_step=10.,
                                         colorbar_args=colorbar_args,
                                         pcolor_args=pcolor_args)


    m.drawparallels(np.arange(-80., 81., 5.), labels=[1, 0, 0, 0], fontsize=10, color='#c6c6c6')
    m.drawmeridians(np.arange(-180., 181., 10.), labels=[0, 0, 0, 1], fontsize=10, color='#c6c6c6')

    m.drawcoastlines(color='grey', linewidth=0.5)
    m.drawmapboundary(color='grey')


if __name__ == '__main__':
    X_train, y_train, X_test = greenland_train_test_sets()

    train_lons = X_train.lon.as_matrix()
    train_lats = X_train.lat.as_matrix()
    X_train = X_train.drop(['lat', 'lon'], axis=1)

    test_lons = X_test.lon.as_matrix()
    test_lats = X_test.lat.as_matrix()
    X_test = X_test.drop(['lat', 'lon'], axis=1)

    # -------------------- Plot training data  -------------------------
    plot_training_GHF(train_lons, train_lats, y_train)
    save_cur_fig('greenland_training_GHF.png', title='GHF at training set')

    plot_gaussian_prescribed_GHF(train_lons, train_lats, y_train)
    save_cur_fig('greenland_prescribed_GHF.png',
                 title='Points with prescribed GHF \n around GHF measurements (mW m$^{-2}$)')

    # -------------------- Plot predicted results ----------------------
    reg = train_gbrt(X_train, y_train)
    y_pred = reg.predict(X_test)

    plot_prediction_points(test_lons, test_lats, y_pred)
    save_cur_fig('greenland_prediction_points.png',
                 title='GHF predicted for Greenland (mW m$^{-2}$)')

    plot_prediction(test_lons, test_lats, y_pred)
    save_cur_fig('greenland_prediction.png',
                 title='GHF predicted for Greenland (mW m$^{-2}$)')

    lons = np.hstack([train_lons, test_lons])
    lats = np.hstack([train_lats, test_lats])
    ghfs = np.hstack([y_train, y_pred])

    plot_prediction_interpolated(lons, lats, ghfs)
    save_cur_fig('greenland_prediction_interpolated.png',
                 title='GHF predicted for Greenland (mW m$^{-2}$)')

    # --------------------- Plot GHF histograms --------------------------
    plot_values_histogram(y_pred)
    save_cur_fig('hist_greenland.png', title='GHF predicted in Greenland')

    plot_values_histogram(y_train)
    save_cur_fig('hist_global.png', title='GHF global measurement')

    # ---------------- Save GHF of Greenland to XYZ format---------------
    data_gris = load_gris_data()
    gris_known, _   = fill_in_greenland_GHF(data_gris)
    gris_known_lats = gris_known.lat.as_matrix()
    gris_known_lons = gris_known.lon.as_matrix()
    gris_known_ghfs = gris_known.GHF.as_matrix()

    xyz_known = np.asarray([gris_known_lats, gris_known_lons, gris_known_ghfs])
    xyz_pred  = np.asarray([test_lats, test_lons, y_pred])

    xyz = np.hstack([xyz_pred, xyz_known])
    header = 'lat, lon, ghf'
    np.savetxt('./greenland_predictions/gris-ghf-xyz-NGRIP-135.csv',
                   xyz.T, delimiter=',', header=header, fmt='%10.5f')
