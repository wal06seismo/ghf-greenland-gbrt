import sys
from random import randint
from math import sqrt, pi
from ghf_prediction import (
    plt, np, mean_squared_error,
    load_global_gris_data, save_cur_fig, save_np_object,
    split, split_by_distance, train_regressor, error_summary
)

def eval_prediction_multiple(data, tasks):
    return {task: eval_prediction(data, *task) for task in tasks}

def eval_prediction(data, t, radius, center):
    X_train, y_train, X_test, y_test = \
        split(data, center, test_size=t, max_dist=radius)
    assert not X_test.empty

    reg = train_regressor(X_train.drop(['Latitude_1', 'Longitude_1'], axis=1),
                          y_train)
    y_pred = reg.predict(X_test.drop(['Latitude_1', 'Longitude_1'], axis=1))
    return error_summary(y_test, y_pred)

def random_prediction_ctr(data, radius, min_points=100):
    cands = data.loc[(data.Latitude_1 > 45) & (data.Longitude_1 > -100) & (data.Longitude_1 < 50)]
    while True:
        center = cands.sample(n=1)
        center = center.Longitude_1, center.Latitude_1
        test, train = split_by_distance(data, center, radius)
        if len(test) >= min_points:
            return round(center[0], 2), round(center[1], 2)

def plot_performance_analysis(data, test_ratios, radii, colors, ncenters):
    centers = [random_prediction_ctr(data, min(radii)) for _ in range(ncenters)]
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('$t$ (percentage of points in circle to predict)')
    ax1.set_ylabel('$r^2$ (solid lines)')
    ax1.set_title('GBRT performance for different radii')
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0.3, 1)
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Normalized RMSE (dashed lines)')
    ax2.set_xlim(0, 100)

    assert len(radii) == len(colors)
    radii_errors = np.zeros([1,3])
    for radius, color in zip(radii, colors):
        shape = (ncenters, len(test_ratios))
        r2s, rmses = np.zeros(shape), np.zeros(shape)
        for idx_t, t in enumerate(test_ratios):
            for idx_ctr, center in enumerate(centers):
                sys.stderr.write('** t = %.2f, r = %d, center = %s:\n' % (t, radius, repr(center)))
                r2, rmse = eval_prediction(data, t, radius, center)
                sys.stderr.write('-> r2 = %.2f, RMSE=%.2f\n' % (r2, rmse))
                rmses[idx_ctr][idx_t] = rmse
                r2s[idx_ctr][idx_t] = r2

            lngth = len(test_ratios)
            radius_error = np.hstack([test_ratios.reshape(lngth,1),r2s.mean(axis=0).reshape(lngth,1),rmses.mean(axis=0).reshape(lngth,1)])
        
        radii_errors = np.vstack([radii_errors,radius_error])

        print test_ratios
        print r2s.mean(axis=0)
        print rmses.mean(axis=0)
        #for idx in range(ncenters):
            #ax1.plot(test_ratios * 100, r2s[idx], color=color, alpha=.2, lw=1)
            #ax2.plot(test_ratios * 100, rmses[idx], color=color, alpha=.2, lw=1, ls='--')

        kw = {'alpha': .9, 'lw': 2.5, 'marker': 'o', 'color': color}
        ax1.plot(test_ratios * 100, r2s.mean(axis=0), label='%d km' % radius, **kw)
        ax2.plot(test_ratios * 100, rmses.mean(axis=0), label='%d km' % radius, ls='--', **kw)

        save_np_object('error_details.txt', 't, r2, and rmse details', radii_errors[1:,:], delimiter=', ',
                       header='t, r2, rmse', fmt='%10.5f')

    ax1.legend(loc=6, prop={'size':12.5})

def plot_sensitivity_analysis(data, t, radius, noise_amps, ncenters):
    centers = [random_prediction_ctr(data, radius) for _ in range(ncenters)]

    fig, ax = plt.subplots()
    ax.set_xlabel('Relative noise magnitude')
    ax.set_ylabel('RMSE in predicted GHF')
    ax.set_xlim(0, max(noise_amps) * 1.1)
    ax.set_title('GBRT sensitivity to noise in GHF measurements')
    ax.grid(True)

    def _predict(X_train, y_train, X_test, center, noise_amp):
        # If noise ~ N(0, s^2), then mean(|noise|) = s * sqrt(2/pi),
        # cf. https://en.wikipedia.org/wiki/Half-normal_distribution
        # So to get noise with mean(|noise|) / mean(y) = noise_ampl, we need to
        # have noise ~ N(0, s*^2) with s* = mean(y) * noise_ampl * sqrt(pi/2).
        noise = np.mean(y_train) * noise_amp * sqrt(pi / 2) * np.random.randn(len(y_train))
        reg = train_regressor(X_train.drop(['Latitude_1', 'Longitude_1'], axis=1),
                              y_train + noise)
        return reg.predict(X_test.drop(['Latitude_1', 'Longitude_1'], axis=1))

    y0 = []
    rmses = np.zeros((ncenters, len(noise_amps)))
    for idx_ctr, center in enumerate(centers):
        X_train, y_train, X_test, y_test = \
            split(data, center, test_size=t, max_dist=radius)
        sys.stderr.write('** noise_amp = 0, center = %s:\n' % repr(center))
        y0 = _predict(X_train, y_train, X_test, center, 0)
        for idx_noise, noise_amp in enumerate(noise_amps):
            sys.stderr.write('** noise_amp = %.2f, center = %s:\n' % \
                (noise_amp, repr(center)))
            y_pred = _predict(X_train, y_train, X_test, center, noise_amp)
            rmse = sqrt(mean_squared_error(y0, y_pred)) / np.mean(y0)
            sys.stderr.write('-> RMSE=%.2f\n' % rmse)
            rmses[idx_ctr][idx_noise] = rmse

    for idx in range(ncenters):
        ax.plot(noise_amps, rmses[idx], color='k', alpha=.2, lw=1)

    ax.plot(noise_amps, rmses.mean(axis=0), alpha=.9, lw=2.5, marker='o', color='k')

data = load_global_gris_data()
# FIXME artificially forced to 135.0 in source
data.loc[data.GHF == 135.0, 'GHF'] = 0
data.loc[data.GHF == 0, 'GHF'] = np.nan
data.dropna(inplace=True)

ts = np.arange(.1, 1, .05)
radii = np.arange(1200, 2701, 500)
colors = 'rgkb'
ncenters = 10
plot_performance_analysis(data, ts, radii, colors, ncenters)
save_cur_fig('GB_performance.png', title='GBRT performance for different radii')

noise_amps = np.arange(0.02, .25, .02)
radius = 1700
ncenters = 10
t = .9
plot_sensitivity_analysis(data, t, radius, noise_amps, ncenters)
save_cur_fig('GB_sensitivity.png', title='GBRT sensitivity for different noise levels')