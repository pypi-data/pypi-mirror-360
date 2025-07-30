from typing import List

import numpy as np
import pandas as pd
from checkmarkandcross import image


def aufgabe2_1(df: pd.DataFrame):
    return image(
        len(df) == 25000
        and len(df.columns.values)
    )


def aufgabe2_2(hashtags: pd.Series):
    return image(
        len(hashtags) == 5049
        and len(hashtags[hashtags == 'null;']) == 0
    )


def aufgabe2_3(tags_list: List):
    return image(
        len(tags_list) == 5049
        and ['verzuzbattle'] in tags_list
        and ['wellness', 'prostate', 'Healthy', 'StayHealthy', 'Supplement', 'Behealthy'] in tags_list
    )


def aufgabe2_4(ohe_df: pd.DataFrame):
    return image(
        len(ohe_df) == 5049
        and len(ohe_df.columns.values) == 8031
    )


def aufgabe2_6(count: int):
    return image(count == 48)


def aufgabe4_1(drinks: pd.DataFrame):
    return image(
        len(drinks) == 193
        and set(drinks.columns) == {'beer_servings', 'country', 'spirit_servings', 'total_litres_of_pure_alcohol', 'wine_servings'}
    )


def aufgabe4_2(drinks_ohe: List):
    return image(
        len(drinks_ohe) == 193
        and len(drinks_ohe[0]) == 510
        and all(isinstance(el, np.bool_) for line in drinks_ohe for el in line)
    )


def aufgabe4_4(drinks_ohe: List):
    return image(
        len(drinks_ohe) == 193
        and len(drinks_ohe[0]) == 205
        and all(isinstance(el, np.bool_) for line in drinks_ohe for el in line)
    )
