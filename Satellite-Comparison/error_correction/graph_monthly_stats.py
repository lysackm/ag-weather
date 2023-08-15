import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import json

from matplotlib import cycler


def graph_year_both_models(stats):
    colours = ["tab:orange", "peru", "tomato", "darkred", "tab:blue", "steelblue", "turquoise", "navy"]
    plt.style.use("ggplot")
    plt.rc("axes",
           prop_cycle=(cycler('color', colours) + cycler('linestyle', ['-', '--', ':', '-.', '-', '--', ':', '-.'])))

    for attr in stats:
        for model in stats[attr]:
            for data_type in stats[attr][model]:
                y_data = stats[attr][model][data_type]
                x_data = range(12)

                plt.plot(x_data, y_data, label=model + " " + data_type)

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        plt.xticks(range(12), months)

        plt.title(attr)
        plt.savefig("stats/" + attr + model + '.png')
        plt.clf()


def graph_year(stats):
    colours_merra = ["tab:orange", "peru", "tomato", "darkred"]
    colours_era5 = ["tab:blue", "steelblue", "turquoise", "navy"]
    plt.style.use("ggplot")

    for model in stats:
        for attr in stats[model]:
            if model == "MERRA":
                colours = colours_merra
            else:
                colours = colours_era5

            plt.rc("axes",
                   prop_cycle=(cycler('color', colours) + cycler('linestyle',
                                                                      ['-', '--', ':', '-.', ])))

            for data_type in stats[model][attr]:
                y_data = stats[model][attr][data_type]
                x_data = range(12)

                plt.plot(x_data, y_data, label=data_type)

            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            plt.xticks(range(12), months)

            plt.title(attr + " " + model)
            plt.legend()
            # plt.show()
            plt.savefig("stats/" + attr + model + '.png')
            plt.clf()


def main():
    file2 = open("stats/stats2.json")
    stats2 = json.load(file2)

    graph_year(stats2)

    file1 = open("stats/stats1.json")
    stats1 = json.load(file1)

    graph_year_both_models(stats1)


main()
