import jellyfish
from rapidfuzz.distance import DamerauLevenshtein


class JaroDamerauLevenshteinMaxSim(object):
    """
    jaro_similarity 有缺陷 以下样例数据会导致分很低
    s1 = "in situ monitoring of semiconductor wafer temperature using infrared interfe rometry"
    s2 = "insitu monitoring of semiconductor wafer temperature using infrared interferometry"
    """

    def get_sim(self, str1: str, str2: str) -> float:
        similarity1 = jellyfish.jaro_similarity(str1, str2)
        if str1.strip() == "" and str2.strip() == "":
            similarity2 = 0
        else:
            similarity2 = 1 - DamerauLevenshtein.normalized_distance(str1, str2)
        return max(similarity1, similarity2)
