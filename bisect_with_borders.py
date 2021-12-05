import bisect

scores = [45, 99, 76, 67, 80, 95, 82, 55, 100]


def get_score_in_alpha(score_to_translate, borders=(60, 70, 80, 90), score_in_alpha='EDCBA'):
    index = bisect.bisect(borders, score_to_translate)
    return score_in_alpha[index]


for score in scores:
    print(get_score_in_alpha(score))
