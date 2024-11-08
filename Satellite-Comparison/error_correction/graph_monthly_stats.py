import matplotlib.pyplot as plt
import json

from matplotlib.rcsetup import cycler
from mpl_toolkits.axes_grid1 import make_axes_locatable


def graph_year_both_models(stats):
    plt.style.use("ggplot")
    plt.rcParams['axes.facecolor'] = 'w'
    plt.rcParams['axes.edgecolor'] = 'dimgrey'
    plt.rcParams['grid.color'] = 'lightgrey'
    plt.rc("axes", prop_cycle=(cycler('linestyle', ['-', '--', ':', '-.'])))

    file_names = ["RMSE_AvgAir_T", "RMSE_AvgWS", "RMSE_Pluvio_Rain", "RMSE_Press_hPa", "RMSE_RH"]

    label_dict = {
        'merra raw': 'MERRA-2 Pre-Cor',
        'merra mean_bias': 'MERRA-2 MB-Cor',
        'merra lin_reg': 'MERRA-2 LR-Cor',
        'merra random_forest': 'MERRA-2 RF-Cor',
        'era5 raw': 'ERA5-Land Pre-Cor',
        'era5 mean_bias': 'ERA5-Land MB-Cor',
        'era5 lin_reg': 'ERA5-Land LR-Cor',
        'era5 random_forest': 'ERA5-Land RF-Cor'
    }

    i = 0

    for attr, file_name in zip(stats, file_names):
        i += 1
        for model in stats[attr]:
            for data_type in stats[attr][model]:
                y_data = stats[attr][model][data_type]
                x_data = range(12)

                colour = "orange" if model == "merra" else "blue"

                label = label_dict[model + " " + data_type]
                ax = plt.subplot(2, 3, i)
                ax.plot(x_data, y_data, label=label, c=colour)

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ax.set(xticks=range(12), xticklabels=months)

        ax.set_title(attr.replace("Average ", ""))

    plt.legend(bbox_to_anchor=(2.1, 0.95), prop={"size": 15})
    plt.savefig("stats/RMSE" + '.png', bbox_inches='tight')
    plt.show()
    # plt.savefig("stats/" + file_name + '.png')
    plt.clf()


# graph each model separately. That is that each graph is one model
# with 4 types of data on 1 attribute.
def graph_year(stats):
    plt.style.use("ggplot")

    for model in stats:
        for attr in stats[model]:
            if model == "MERRA":
                colour = "orange"
            else:
                colour = "blue"

            plt.rc("axes",
                   prop_cycle=(cycler('linestyle', ['-', '--', ':', '-.', ])))

            for data_type in stats[model][attr]:
                y_data = stats[model][attr][data_type]
                x_data = range(12)

                plt.plot(x_data, y_data, label=data_type, c=colour)

            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            plt.xticks(range(12), months)

            plt.title(attr + " " + model)
            plt.legend()
            # plt.show()
            # plt.savefig("stats/" + attr + model + '.png')
            plt.clf()


def main():
    file3 = open("stats/stats3.json")
    stats3 = json.load(file3)

    # graph_year(stats2)

    file1 = open("stats/stats1.json")
    stats1 = json.load(file1)

    graph_year_both_models(stats3)


main()
