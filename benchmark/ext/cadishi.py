# Functions from this file are copied from cadishi. See copyright notice below.
#
# Copyright (c) Klaus Reuter, Juergen Koefinger
# See the file AUTHORS.rst for the full list of contributors.
#
# Released under the MIT License, see the file LICENSE.txt.


def _cat_proc_cpuinfo_grep_query_sort_uniq(query):
    """Determine the number of unique lines in /proc/cpuinfo

    Parameters
    ----------
    string : query
        string the lines to be searched for shall begin with

    Returns
    -------
    set
        unique lines in /proc/cpuinfo that begin with query

    May throw an IOError exception in case /proc/cpuinfo does not exist.
    """
    items_seen = set()
    with open("/proc/cpuinfo") as fp:
        for line_raw in fp:
            if line_raw.startswith(query):
                line = line_raw.replace('\t', '').strip('\n')
                items_seen.add(line)
    return items_seen
