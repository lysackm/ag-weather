import matplotlib.pyplot as plt
import json

from matplotlib import cycler


def graph_year_both_models(stats):
    plt.style.use("ggplot")
    plt.rc("axes",
           prop_cycle=(cycler('linestyle', ['-', '--', ':', '-.'])))

    file_names = ["RMSE_AvgAir_T", "RMSE_AvgWS", "RMSE_Pluvio_Rain", "RMSE_Press_hPa", "RMSE_RH", "RMSE_SolarRad"]

    for attr, file_name in zip(stats, file_names):
        for model in stats[attr]:
            for data_type in stats[attr][model]:
                y_data = stats[attr][model][data_type]
                x_data = range(12)

                colour = "orange" if model == "merra" else "blue"

                plt.plot(x_data, y_data, label=model + " " + data_type, c=colour)

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        plt.xticks(range(12), months)

        plt.title(attr)
        plt.savefig("stats/" + file_name + '.png')
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
    file2 = open("stats/stats2.json")
    stats2 = json.load(file2)

    graph_year(stats2)

    file1 = open("stats/stats1.json")
    stats1 = json.load(file1)

    graph_year_both_models(stats1)


main()
