#
# HillRepeats.py - find start and end of a hill repeat given a tab-delimited activity file and start/stop lat/long
#
import sys                      # for argv.sys
import os.path                  # for checking if file exists
from datetime import datetime   # for calculating dates
import configparser as cfg      # for reading config files

date_format = "%H:%M:%S %p"

# activity lines: 0:[time] 1:[lat] 2:[long] 3:[altitude(m)] 4:[distance(m)] 5:[HR(BPM)] 6:[Cadence(RPM)] 7:[Speed(m/s)]
TIME = 0; LAT = 1; LONG = 2; ALT = 3; DIST = 4; HR = 5; CAD = 6; SPEED = 7;


def usage():
    #print("USAGE: python HillRepeats.py <num-repeats> <activity.txt> <start-lat> <start-long> <stop-lat> <stop-long>")
    print("USAGE: python HillRepeats.py <activity.txt> <hill-name>")
    exit(-1)

def calc_column_min_avg_max(split_lines, column_index, start_index, stop_index):
    """
    calculates the min, average and max for the column between the start and stop indices
    :param split_lines: list of activity lines, with the column we want
    :param column_index: index for the column in the activity line, use the UPPERCASE constants above
    :param start_index: the index within split_lines to start calculating
    :param stop_index: the index within split_lines to stop calculating
    :return: min, avg, max (numeric values)
    """

    # print("DEBUG:", column_index, start_index, stop_index)

    # NOTE: we +1 the stop_index b/c range goes up to, but not including, this value, and we want to include it
    col_min = None
    col_max = None
    col_avg = 0
    col_sum = 0
    col_count = stop_index - start_index

    for i in range(start_index, stop_index + 1):

        col_val = split_lines[i][column_index]

        # min must be more than zero, to avoid calculating non-effort values
        if col_val > 0:
            if col_min is None:
                col_min = col_val
            elif col_val < col_min:
                col_min = col_val

        if col_max is None:
            col_max = col_val
        elif col_val > col_max:
            col_max = col_val

        col_sum += col_val

    col_avg = col_sum / float(col_count)

    return col_min, col_avg, col_max

def find_starts(split_lines, start_lat, start_long):
    """
    returns a list of starting entries with items: [<lat-long-error> <line-index> <line-data>]
    :param split_lines: list of raw lines to search for starting positions
    :param start_lat: latitude value to search for starting positions
    :param start_long: longitude value to search for starting positions
    :return: a list of starts
    """

    # find all possible starts
    found_starts = []

    for i in range(len(split_lines)):

        lat = split_lines[i][LAT]
        long = split_lines[i][LONG]

        start_lat_diff = (lat - start_lat)
        start_long_diff = (long - start_long)
        start_error = abs(start_lat_diff) + abs(start_long_diff)

        # add some possible starts - we always stop before we do a run, so look for zero speed (stop)
        if split_lines[i][SPEED] == float(0):
            if len(found_starts) < 20 and start_error < 0.01:
                new_start = [start_error, i, split_lines[i]]
                found_starts.append(new_start)
                # print("new start:", new_start)
            else:
                for s in found_starts:
                    if start_error < s[0]:
                        # print("removing start:", s)
                        found_starts.remove(s)

                        new_start = [start_error, i, split_lines[i]]
                        found_starts.append(new_start)
                        # print("adding start:", new_start)

                        break

    # remove any starts that are too close together in time, i.e. parked and moved the bike, take the last entry
    good_starts = []

    for i in range(len(found_starts) - 1):
        time0 = datetime.strptime(found_starts[i][2][TIME], date_format)
        time1 = datetime.strptime(found_starts[i + 1][2][TIME], date_format)
        diff = time1 - time0

        # keep starts that are more than 2 minutes apart
        if diff.seconds > 2 * 60:
            good_starts.append(found_starts[i])
        # else:
        #    # previous time is too close, keep the older of the two
        #    good_starts.append(found_starts[i+1])

    # keep the last entry
    good_starts.append(found_starts[len(found_starts) - 1])

    # actual start is the next entry after the detected (zero-speed start)
    better_starts = []
    for s in good_starts:
        gs_error = s[0]
        gs_line = s[1]
        gs_raw = split_lines[gs_line + 1]
        better_starts.append([gs_error, gs_line, gs_raw])

    good_starts = better_starts

    # found starts
    log_message("DEBUG: found good starts")
    for s in good_starts:
        log_message(s)

    return good_starts

def find_stops(split_lines, good_starts, stop_lat, stop_long):
    """
    returns a list of stops matched to each start
    :param split_lines: original activity lines
    :param good_starts: list of starts
    :param stop_lat: stop's latitude
    :param stop_long: stop's longitude
    :return: a list of stops
    """

    # keep the first _stop_ after each start
    good_stops = []

    for t in range(len(good_starts)):

        start_counter = good_starts[t][1]
        best_stop_error = 1
        best_stop_counter = 0

        if t < len(good_starts) - 1:
            next_start_counter = good_starts[t + 1][1]
        else:
            # last start, so we can go to the end of the lines, if necessary
            next_start_counter = len(split_lines)

        # assumes stops are sorted numerically, from first to last
        for i in range(len(split_lines)):

            stop_counter = i

            if start_counter < stop_counter < next_start_counter:

                # print("DEBUG: testing after start...")

                lat = split_lines[i][LAT]
                long = split_lines[i][LONG]

                stop_lat_diff = (lat - stop_lat)
                stop_long_diff = (long - stop_long)
                stop_error = abs(stop_lat_diff) + abs(stop_long_diff)

                if stop_error < best_stop_error:
                    best_stop_counter = i
                    best_stop_error = stop_error
                    # print("DEBUG: best_stop_counter", best_stop_counter, "best_stop_error", best_stop_error)

        good_stops.append([best_stop_error, best_stop_counter, split_lines[best_stop_counter]])

    log_message("DEBUG: found good stops")
    for s in good_stops:
        log_message(s)

    return good_stops

def load_hills_from_config(config_filename):
    """
    loads the list of hills from config/hills.ini into a dictionary indexed by the hill name
    :param config: configparser object for the config .ini file
    :return: dictionary of hills
    """

    config = cfg.ConfigParser()
    config.read(config_filename)

    if "hills" in config:
        log_message("DEBUG: hills found in config")

        hills_list = [option for option in config["hills"]]
        hills_dict = {}
        for h in hills_list:
            hill_val_str = config["hills"][h]
            hill_val_list_str = hill_val_str.split(",")
            hill_val_list = []
            for hv in hill_val_list_str:
                hill_val_list.append(num_str_to_float(hv))

            hills_dict[h] = hill_val_list

        return hills_dict
    else:
        log_message("ERROR: no hills found in config?")
        exit(-1)

def load_split_lines(filename):
    """
    returns a list of activity lines, split by tab (\t) into predefined columns
    :param filename: tab-delimited activity file
    :return: list of list of lines
    """
    # verify activity file exists
    if not os.path.isfile(filename):
        log_message("ERROR: activity file not found?")
        exit(-1)

    # source: https://stackoverflow.com/questions/14676265/how-to-read-a-text-file-into-a-list-or-an-array-with-python
    f = open(filename, "r")
    lines = f.read().splitlines()
    f.close()

    # split the lines by delimiter
    split_lines = []

    for ln in lines:

        s = ln.split('\t')

        # drop the header line and any blank lines
        if s[0] == "Time" or s[0] == "":
            pass
        else:
            # convert lat/long to floats
            # convert negative numbers from (xx.xx) to -xx.xx
            c = [s[TIME],
                 num_str_to_float(s[LAT]),
                 num_str_to_float(s[LONG]),
                 num_str_to_float(s[ALT]),
                 num_str_to_float(s[DIST]),
                 num_str_to_float(s[HR]),
                 num_str_to_float(s[CAD]),
                 num_str_to_float(s[SPEED])
                 ]

            split_lines.append(c)

    return split_lines

def log_message(msg):
    print(msg)

def num_str_to_float(num_str):
    """
    returns a float, converting any negatives enclosed in parentheses (xx.xx) to -xx.xx
    :param num_str: float number as string
    :return: float version of original numeric string
    """

    trimmed_num_str = num_str.strip()

    # convert (xx.xx) to -xx.xx
    if "(" in trimmed_num_str and ")" in trimmed_num_str:
        neg_num_str = trimmed_num_str.replace("(", "-").replace(")", "")
        trimmed_num_str = neg_num_str

    # convert "-" (single hyphen) or empty string to "0"
    if "-" == trimmed_num_str or "" == trimmed_num_str:
        trimmed_num_str = "0"

    # remove commas
    # HACK:
    # NON-localized version, only works for locales that use comma's as thousands separator, not as decimal separator
    trimmed_num_str = trimmed_num_str.replace(",", "")
    """
    # TODO: use this to test our unit tests during refactoring
    try:
        from locale import atof, setlocale, LC_NUMERIC
        setlocale(LC_NUMERIC, '')
        trimmed_num_str = atof(trimmed_num_str)
    except:
        # HACK:
        # NON-localized version, only works for locales that use comma's as thousands separator, not as decimal separator
        trimmed_num_str = trimmed_num_str.replace(",", "")
        raise("ERROR: failed to remove comma from number in num_str_to_float: " + trimmed_num_str)
    """

    try:
        num_float = float(trimmed_num_str)
    except:
        log_message("ERROR: unable to convert num_str " + num_str + " to float type")
        exit(-1)

    return num_float

def save_interval_csv(activity_file, interval_id, split_lines, int_start, int_stop):
    """
    saves the raw interval data to a CSV file
    :param activity_file: name of the original activity file
    :param interval_id: interval number
    :param split_lines: original activity lines
    :param int_start: starting index for this interval
    :param int_stop: stopping index for this interval
    :return: None
    """

    # NOTE: "w" will overwrite any existing instances
    # TODO: write to an 'intervals' or 'data' directory instead of the same dir that the activity is pulled from
    f = open(activity_file + "_interval_" + str(interval_id) + ".csv", "w")

    # header
    f.write("Time,Latitude,Longitude,Alt.(M),Dist.(M),HR (Bpm),Cadence,Speed\n")

    # +1 b/c range is up to, but not including
    for x in range(int_start, int_stop + 1):
        # remove the leading and trailing square brackets added when converting a list to a string
        # remove the single quotes placed around times
        line = str(split_lines[x]).replace("[", "").replace("]", "").replace("'", "")
        f.write(line + "\n")

    f.close()

def save_summary_tab_txt(activity_file, split_lines, starts, stops):
    """
    save summary totals and calculations from all intervals as individual lines, with a header
    :param activity_file: name of the original activity file
    :param split_lines: original lines from the activity file
    :param starts: list of interval starts
    :param stops: list of interval stops
    :return: None
    """

    # NOTE: "w" will overwrite any existing instances
    # TODO: write to an 'intervals' or 'data' directory instead of the same dir that the activity is pulled from
    f = open(activity_file + "_summary" + ".txt", "w")

    # header
    f.write("interval\t" +
          "duration(mm:ss)\t" +
          "duration(s)\t" +
          "distance(m)\t" +
          "minHR(BPM)\t" +
          "avgHR(BPM)\t" +
          "maxHR(BPM)\t" +
          "minCad(RPM)\t" +
          "avgCad(RPM)\t" +
          "maxCad(RPM)\t" +
          "minSpeed(m/s)\t" +
          "avgSpeed(m/s)\t" +
          "maxSpeed(m/s)\t" +
          "minSpeed(km/h)\t" +
          "avgSpeed(km/h)\t" +
          "maxSpeed(km/h)\n"
          )

    for i in range(len(starts)):

        # duration
        time_stop = datetime.strptime(stops[i][2][TIME], date_format)
        time_start = datetime.strptime(starts[i][2][TIME], date_format)
        int_duration = time_stop - time_start

        # distance
        int_dist = stops[i][2][DIST] - starts[i][2][DIST]

        # calc heart rates
        minHR, avgHR, maxHR = calc_column_min_avg_max(split_lines, HR, starts[i][1], stops[i][1])

        # calc cadence
        minCad, avgCad, maxCad = calc_column_min_avg_max(split_lines, CAD, starts[i][1], stops[i][1])

        # calc speed (m/s)
        minSpeed, avgSpeed, maxSpeed = calc_column_min_avg_max(split_lines, SPEED, starts[i][1], stops[i][1])

        if minSpeed is None: minSpeed = 0
        if avgSpeed is None: avgSpeed = 0
        if maxSpeed is None: maxSpeed = 0

        # calc speed (km/h)
        minSpeed_kmh = (minSpeed * 3600) / 1000
        avgSpeed_kmh = (avgSpeed * 3600) / 1000
        maxSpeed_kmh = (maxSpeed * 3600) / 1000

        f.write("int " + str(i + 1) + "\t" +
              str(int_duration) + "\t" +
              str(int_duration.seconds) + "\t" +
              str(int_dist) + "\t" +
              str(minHR) + "\t" +
              str(avgHR) + "\t" +
              str(maxHR) + "\t" +
              str(minCad) + "\t" +
              str(avgCad) + "\t" +
              str(maxCad) + "\t" +
              str(minSpeed_kmh) + "\t" +
              str(avgSpeed_kmh) + "\t" +
              str(maxSpeed_kmh) + "\n"
              )

    f.close()

def main():

    # check if we have at least N parameters from the command line
    if len(sys.argv) < 3:
        usage()

    #
    # hill coordinates (start latitude, start longitude, stop latitude, stop longitude)
    # values are manually determined and added to the table below
    #
    hills = {
        "ubc": [49.2793093, -123.2404815, 49.2713713, -123.2540545]
    }
    """
    # TODO: load from a config file instead of hardcoded
    config_filename = "../config/hills.ini"
    hills = load_hills_from_config(config_filename)

    if len(hills) <= 0:
        log_message("ERROR: no hills data available")
        exit(-1)
    """

    # TODO: replace hardcoded directories with config file entries
    intervals_output_dir = "../data/intervals/"
    # use the same dir for now
    summary_output_dir = "../data/intervals/"

    #
    # load the command line arguments
    #

    # NOTE: sys.argv[0] is the name of the Python script, not the first cmdline arg
    activity_file = sys.argv[1]
    hill_name = sys.argv[2]

    # we just want the name, not any optional directory
    just_activity_filename = os.path.basename(activity_file)
    log_message("DEBUG: just_activity_filename:" + just_activity_filename)

    # old cmdline interface, replaced with hill name (lower-case)
    #start_lat = float(sys.argv[2])
    #start_long = float(sys.argv[3])
    #stop_lat = float(sys.argv[4])
    #stop_long = float(sys.argv[5])
    start_lat = hills[hill_name][0]
    start_long = hills[hill_name][1]
    stop_lat = hills[hill_name][2]
    stop_long = hills[hill_name][3]

    #
    # load activity file and find intervals
    #

    # debug
    print("DEBUG: loading", activity_file,
          "starting at", start_lat, ",", start_long,
          "stopping at", stop_lat, ",", stop_long)

    # load lines
    split_lines = load_split_lines(activity_file)

    # find starts
    starts = find_starts(split_lines, start_lat, start_long)

    # find stops
    stops = find_stops(split_lines, starts, stop_lat, stop_long)

    #
    # save interval files
    #
    for i in range(len(starts)):
        int_start = starts[i][1]
        int_stop = stops[i][1]
        save_interval_csv(intervals_output_dir + just_activity_filename, i, split_lines, int_start, int_stop)

    #
    # save summary file
    #
    save_summary_tab_txt(summary_output_dir + just_activity_filename, split_lines, starts, stops)


if __name__ == "__main__":
    main()