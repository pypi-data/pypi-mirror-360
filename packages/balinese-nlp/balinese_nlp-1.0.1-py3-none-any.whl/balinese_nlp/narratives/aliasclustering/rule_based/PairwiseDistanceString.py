from difflib import SequenceMatcher
from jaro import jaro_winkler_metric
from math import floor, ceil


class PairwiseDistanceString:
    def __init__(self):
        pass

    def _ratcliff_obershelp_algorithm(self, string1, string2):
        return SequenceMatcher(None, string1, string2).ratio()

    def _jaccard_similarity(self, string1, string2):
        set1 = set(string1)
        set2 = set(string2)
        pembilang = len(
            set1.intersection(set2))
        penyebut = len(set1.union(set2))
        jaccard_similarity = (pembilang/penyebut) if penyebut != 0 else 0
        return jaccard_similarity

    def _sorensen_dice_similarity(self, string1, string2):
        set1 = set(string1)
        set2 = set(string2)
        pembilang = 2 * len(set1.intersection(set2))
        penyebut = (len(set1) + len(set2))
        sorensen_dice_similarity = (pembilang/penyebut) if penyebut != 0 else 0
        return sorensen_dice_similarity

    def _jaro_similarity(self, string1, string2):
        s1 = string1
        s2 = string2
        # If the s are equal
        if (s1 == s2):
            return 1.0

        # Length of two s
        len1 = len(s1)
        len2 = len(s2)

        # Maximum distance upto which matching
        # is allowed
        max_dist = floor(max(len1, len2) / 2) - 1

        # Count of matches
        match = 0

        # Hash for matches
        hash_s1 = [0] * len(s1)
        hash_s2 = [0] * len(s2)

        # Traverse through the first
        for i in range(len1):

            # Check if there is any matches
            for j in range(max(0, i - max_dist),
                           min(len2, i + max_dist + 1)):

                # If there is a match
                if (s1[i] == s2[j] and hash_s2[j] == 0):
                    hash_s1[i] = 1
                    hash_s2[j] = 1
                    match += 1
                    break

        # If there is no match
        if (match == 0):
            return 0.0

        # Number of transpositions
        t = 0
        point = 0

        # Count number of occurrences
        # where two characters match but
        # there is a third matched character
        # in between the indices
        for i in range(len1):
            if (hash_s1[i]):

                # Find the next matched character
                # in second
                while (hash_s2[point] == 0):
                    point += 1

                if (s1[i] != s2[point]):
                    t += 1
                point += 1
        t = t//2

        # Return the Jaro Similarity
        return (match / len1 + match / len2 +
                (match - t) / match) / 3.0

    def _jaro_winkler_similarity(self, string1, string2):
        return jaro_winkler_metric(string1, string2)
