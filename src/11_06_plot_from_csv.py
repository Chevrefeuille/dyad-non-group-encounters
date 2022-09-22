from email import header
from pedestrians_social_binding.utils import *
from pedestrians_social_binding.constants import *

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from parameters import *
from utils import *


if __name__ == "__main__":

    for env_name in ["atc:corridor", "diamor:corridor"]:

        env_name_short = env_name.split(":")[0]

        (
            soc_binding_type,
            soc_binding_names,
            soc_binding_values,
            soc_binding_colors,
        ) = get_social_values(env_name)

        # if "atc" in env_name:
        #     soc_binding_values = [1, 2]

        for alone in ["alone", "not_alone"]:

            fig, ax = plt.subplots()
            for i, v in enumerate(soc_binding_values):
                df = pd.read_csv(
                    f"../data/csv/intrusion/{env_name_short}/{alone}/{env_name_short}_{soc_binding_names[v]}_straight_line_vs_observed_{alone}.csv"
                )
                plt.scatter(df["ro"], df["rp"], c=soc_binding_colors[v], alpha=0.3)
            plt.show()

            fig, ax = plt.subplots()
            for i, v in enumerate(soc_binding_values):
                df = pd.read_csv(
                    f"../data/csv/intrusion/{env_name_short}/{alone}/{env_name_short}_{soc_binding_names[v]}_straight_line_vs_observed_bin_{alone}.csv"
                )
                plt.errorbar(
                    df["ro_bin"], df["mean_rp"], df["ste_rp"], c=soc_binding_colors[v]
                )
            plt.show()
