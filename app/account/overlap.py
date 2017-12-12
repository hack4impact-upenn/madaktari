# gets list of interval start dates and end dates [{start: "XXXX-XX-XX", end: "XXXX-XX-XX"}, {start: "XXXX-XX-XX", ...
# gets list of interval start dates and end dates [{start: "XXXX-XX-XX", end: "XXXX-XX-XX"}, {start: "XXXX-XX-XX", ...


def all_interval_overlap(list1, list2):
    i = 0
    j = 0
    overlap_list = []
    # while i < len(list1) and j < len(list2)
    while i < len(list1) and j < len(list2):
        if smaller_date(list1[i].start_date, list2[j].start_date) == 1:
            which_start = 2
            curr_start = list2[j].start_date
        else:
            which_start = 1
            curr_start = list2[i].start_date
        if smaller_date(list2[i].end_date, list2[j].end_date) == 1:
            which_end = 1
            curr_end = list1[i].end_date
            i += 1
        else:
            which_end = 2
            curr_end = list2[j].end_date
            j += 1
        if which_start != which_end:
            overlap_list.append({'start': curr_start, 'end': curr_end})
    return overlap_list


def smaller_date(date1, date2):
    if date1 < date2:
        return 1
    else:
        return 2
