import re

SI_units = {
    "-24": (-24, "y", "yocto"),
    "-21": (-21, "z", "zepto"),
    "-18": (-18, "a", "atto"),
    "-15": (-15, "f", "femto"),
    "-12": (-12, "p", "pico"),
    "-9": (-9, "n", "nano"),
    "-6": (-6, "µ", "micro"),
    "-3": (-3, "m", "milli"),
    "-2": (-2, "c", "centi"),
    "-1": (-1, "d", "deci"),
    "0": (0, "", ""),
    "1": (1, "da", "deka"),
    "2": (2, "h", "hecto"),
    "3": (3, "k", "kilo"),
    "6": (6, "M", "mega"),
    "9": (9, "G", "giga"),
    "12": (12, "T", "tera"),
    "15": (15, "P", "peta"),
    "18": (18, "E", "exa"),
    "21": (21, "Z", "zetta"),
    "24": (24, "Y", "yotta"),
    # Binary
    "10": (10, "Ki", "kibi"),
    "20": (20, "Mi", "mebi"),
    "30": (30, "Gi", "gibi"),
    "40": (40, "Ti", "tebi"),
    "50": (50, "Pi", "pebi"),
    "60": (60, "Ei", "exbi"),
    "70": (70, "Zi", "zebi"),
    "80": (80, "Yi", "yobi"),
}

E24 = [ 1, 1.1,.2,.3, 1.5, 1.6, 1.8, 2, 2.2, 2.4, 2.7, 3, 3.3, 3.6,
       3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1,]

LE24 = [ "A","B","C","D","E","F","G","H","J","K","L","M",
         "N","P","Q","R","S","T","U","V","W","X","Y", "Z",]

EIA198 = ["A","B","C","D","E","F","G","H","J","K","a","L",
          "M","N","b","p","d","R","e","S","f","T","U","m","V",
          "W","n","X","t","Y","y","z",]

EIA198v = [1,1.1,1.2,1.3,1.5,1.6,1.8,2,2.2,2.4,2.6,3,3.3,3.5,
           3.6,3.9,4,4.3,4.5,4.7,5,5.1,5.6,6,6.2,6.8,7,7.5,8,8.2,9,9.1,]

E48 = [ 1,1.05,1.1,1.15,1.21,1.27,1.33,1.4,1.47,1.54,1.62,1.69,1.78,1.87,1.96,2.05,
        2.15,2.26,2.37,2.49,2.61,2.74,2.87,3.01,3.16,3.32,3.48,3.65,3.83,4.02,4.22,4.42,
       4.64,4.87,5.11,5.36,5.62,5.9,6.19,6.49,6.81,7.15,7.5,7.87,8.25,8.66,9.09,9.53,]

E96 = [ 1,1.02,1.05,1.07,1.1,1.13,1.15,1.18,1.21,1.24,1.27,1.3,1.33,1.37,1.4,1.43,1.47,
        1.5,1.54,1.58,1.62,1.65,1.69,1.74,1.78,1.82,1.87,1.91,1.96,2,2.05,2.1,2.15,2.21,2.26,
        2.32,2.37,2.43,2.49,2.55,2.61,2.67,2.74,2.8,2.87,2.94,3.01,3.09,3.16,3.24,3.32,3.4,3.48,
        3.57,3.65,3.74,3.83,3.92,4.02,4.12,4.22,4.32,4.42,4.53,4.64,4.75,4.87,4.99,5.11,5.23,
        5.36,5.49,5.62,5.76,5.9,6.04,6.19,6.34,6.49,6.65,6.81,6.98,7.15,7.32,7.5,7.68,7.87,8.06,
        8.25,8.45,8.66,8.87,9.09,9.31,9.53,9.76,]

CAPACITY = [("pF", 1), ("nF", 1000), ("µF", 1000000), ("mF", 1000000000)]


def calculate_values(_tolerance, _mantissa, _multiplier):
    tolerance_val = int(_tolerance) * 0.01
    ohm = _mantissa * 10**_multiplier
    #print("Calc: ",_multiplier)
    if ohm < 1:
        postfix = "mΩ"
        actual_value = ohm
    elif ohm > 999 and ohm < 999999:
        postfix = "kΩ"
        actual_value = ohm / 1000
    elif ohm > 999999:
        postfix = "MΩ"
        actual_value = ohm / 100000
    else:
        postfix = "Ω"
        actual_value = ohm
        if actual_value > 999:
            actual_value = actual_value / 1000

    min_value = format(actual_value * (1 - tolerance_val), ".1f")
    max_value = format(actual_value * (1 + tolerance_val), ".1f")

    return actual_value, min_value, max_value, postfix


def get_multiplier(value):
    if len(value) > 0 and len(value) <= 1:
        return {
            "multipler": "0.1",
            "color": "gold",
            "idx": "2",
        }
    elif len(value) > 1 and len(value) <= 2:
        return {
            "multipler": "1",
            "color": "black",
            "idx": "3",
        }  # idx is the combobox index
    elif len(value) > 2 and len(value) <= 3:
        return {"multipler": "10", "color": "brown", "idx": "4"}
    elif len(value) > 3 and len(value) <= 4:
        return {"multipler": "100", "color": "red", "idx": "5"}
    elif len(value) > 4 and len(value) <= 5:  # 1k
        return {"multipler": "1000", "color": "orange", "idx": "6"}
    elif len(value) > 5 and len(value) <= 6:  # 10k
        return {"multipler": "10000", "color": "yellow", "idx": "7"}
    elif len(value) > 6 and len(value) <= 7:  # 100k
        return {"multipler": "100000", "color": "green", "idx": "8"}
    elif len(value) > 7 and len(value) <= 8:  # 1M
        return {"multipler": "1000000", "color": "blue", "idx": "9"}
    elif len(value) > 8 and len(value) <= 9:  # 10M
        return {"multipler": "10000000", "color": "purple", "idx": "10"}
    elif len(value) > 9 and len(value) <= 10:  # 100M
        return {"multipler": "100000000", "color": "gray", "idx": "11"}
    elif len(value) > 10:  # 1G
        return {"multipler": "1000000000", "color": "white", "idx": "12"}