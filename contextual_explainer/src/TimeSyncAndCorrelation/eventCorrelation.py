import matplotlib.pyplot as plt


def plot_event_timeframe(features, cps):
    fig, ax = plt.subplots()
    ax.xaxis_date()
    for name, group in df.groupby('name', sort=False):

        group.amin = group['timestamp'].iloc[0] # assume sorted order
        group.amax = group['timestamp'].iloc[1]

        ax.hlines(group.index, dt.date2num(group.amin), dt.date2num(group.amax))

    for key, grp in data.groupby(['Month']):
        ax2.plot(grp['Day'], grp['Temp'], label="Temp in {0:02d}".format(key))
    plt.legend(loc='best')
    plt.show()

    plt.show()

    # Todo: finish this and context api to make the system accessible as a service through REST