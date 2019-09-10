import re
import warnings
import pytest

# Converts a string to metadata, given the following conditions
# The string may optionally begin with a date and/or time, terminated with
# '_' if there is additional metadata
#
#  2019-08-25-23-31 ->  {'date': '2019-08-25', 'time': '23:31'}
#  2019-08-25 -> {'date': '2019-08-25'}
#  23-31  -> {'time': '23:31'}
#
# If the time pattern is more than 4 digits, split into pairs by a hyphen,
# the string is kept 'literal' &  the time section is guaranteed to return
# all text up until the first underscore or period.
#
# T his is intended to allow arbitrary precision and the inclusion of time
# zone specifiers, etc
#
# Up to the first period, the string shall then consist of key value pairs,
# with a hyphen separating keys from values and an underscore separating
# pairs from each other
#
#  key1-value1_key2-value2 -> {'key1': 'value1', 'key2': 'value2'}
#
#  All text after the first period is ignored.
# This is to allow non-metadata information in the file.
#
#  You can have 'blank' values
#       key1-_key2-value2  -> {'key1': '', 'key2': 'value2'}
#
#  You can also have 'blank' keys, although I think that's a bad idea
#
# You cannot, however, have both a blank key and value in the same pair
#
#       key1-value1__key2-value2  will throw an exception
#
# You also cannot have multiple values for one key.
# In effect, this means that you cannot have '-' in a value.
#
# The parser does not validate values from the metadata.
# E.g. It will happilly allow hours > 24, non sequential replicates, etc
# It will also happily overwrite keys, so if you have rep_a-rep-b, then
# the dictionary will probably end up being {'rep': 'b'}
#
# The keys 'rstr', 'date', and 'time' are reserved. It will assume you
# know what you're doing and happily overwrite, but will write a warning
# A 'rstr' key will include the raw string


def metastring(mstr):
    # split it into date, time, metadata 'stuff' before first period
    m = re.search(r'(\d{4}-\d{2}-\d{2}){0,1}[-|_]{0,1}(\d{2}-\d{2}[^_\.]*){0,1}_{0,1}([^.]*)', mstr)

    # start off the dictionary with the original string
    expected = {'rstr': mstr}

    # add in the date and time if found
    # date
    if(m.group(1)):
        expected['date'] = m.group(1)

    # time, convert to use a colon if it's a 'simple' timestr
    if(m.group(2)):
        # detect simple time based on length
        if(len(m.group(2)) == 5):
            expected['time'] = re.sub('-', ':', m.group(2))
        else:
            expected['time'] = m.group(2)

    # add in key value pairs by first splitting into pairs, then
    # separating keys and values
    if(m.group(3)):
        for s in m.group(3).split('_'):
            key, value = s.split('-')
            if(key in ["rstr", "date", "time"]):
                warnings.warn(UserWarning("rstr is a reserved key"))
            expected[key] = value
    return(expected)


########################
# Tests
#######################

# full date and time, good key value pairs, no comments or literal time
# The 'base' case simply because this is 99% of what I do
def test_base_case():
    test_str = '2019-04-25-11-30_run-2_reactor-3_rep-a_pxpm-610000_sec-1_num-0003.tif'
    mdata = metastring(test_str)
    expected = {'date': '2019-04-25',
                'time': '11:30',
                'run': '2',
                'reactor': '3',
                'rep': 'a',
                'pxpm': '610000',
                'sec': '1',
                'num': '0003',
                'rstr': test_str}

    assert(expected == mdata)


# It's ok to have a date with no time
def test_no_time():
    test_str = '2019-04-26_run-2_reactor-7_rep-a_pxpm-610000_sec-3_num-0013.tif'
    mdata = metastring(test_str)
    expected = {'date': '2019-04-26',
                'run': '2',
                'reactor': '7',
                'rep': 'a',
                'pxpm': '610000',
                'sec': '3',
                'num': '0013',
                'rstr': test_str}
    assert(expected == mdata)


# Ok to have just a time with no date
def test_no_date():
    test_str = '11-30_run-2_reactor-2_rep-a_pxpm-610000_sec-1_num-0003.tif'
    mdata = metastring(test_str)
    expected = {'time': '11:30',
                'run': '2',
                'reactor': '2',
                'rep': 'a',
                'pxpm': '610000',
                'sec': '1',
                'num': '0003',
                'rstr': test_str}
    assert(expected == mdata)


# Date and time are not required
def test_no_date_time():
    test_str = 'run-2_reactor-7_rep-a_pxpm-610000_sec-3_num-0013.tif'
    mdata = metastring(test_str)
    expected = {'run': '2',
                'reactor': '7',
                'rep': 'a',
                'pxpm': '610000',
                'sec': '3',
                'num': '0013',
                'rstr': test_str}
    assert(expected == mdata)


# Ignore anything after the first period, useful for non-metadata stuff
def test_contains_non_meta():
    test_str = 'run-2_reactor-7_rep-a_pxpm-610000_sec-3.nonmetacomment._num-0013.tif'
    mdata = metastring(test_str)
    expected = {'run': '2',
                'reactor': '7',
                'rep': 'a',
                'pxpm': '610000',
                'sec': '3',
                'rstr': test_str}
    assert(expected == mdata)


# Some things may only need a date and/or time to be relevant
def test_just_date_andor_time():
    test_str = '2019-05-26.tif'
    mdata = metastring(test_str)
    expected = {'date': '2019-05-26', 'rstr': test_str}
    assert(expected == mdata)

    test_str = '2019-05-26_.tif'
    mdata = metastring(test_str)
    expected = {'date': '2019-05-26', 'rstr': test_str}
    assert(expected == mdata)

    test_str = '2019-05-26-21-20.tif'
    mdata = metastring(test_str)
    expected = {'date': '2019-05-26', 'time': '21:20', 'rstr': test_str}
    assert(expected == mdata)

    test_str = '2019-05-26-21-20_.tif'
    mdata = metastring(test_str)
    expected = {'date': '2019-05-26', 'time': '21:20', 'rstr': test_str}
    assert(expected == mdata)

    test_str = '21-20.tif'
    mdata = metastring(test_str)
    expected = {'time': '21:20', 'rstr': test_str}
    assert(expected == mdata)

    test_str = '21-20_.tif'
    mdata = metastring(test_str)
    expected = {'time': '21:20', 'rstr': test_str}
    assert(expected == mdata)


# Extended time stamps allow for seconds, milliseconds, timezone
def test_extended_time_stamp():
    test_str = '2019-05-25-23-20-24-EST_reactor-2.tif'
    mdata = metastring(test_str)
    expected = {'date': '2019-05-25',
                'time': '23-20-24-EST',
                'reactor': '2',
                'rstr': test_str}
    assert(expected == mdata)


def test_extended_time_stamp_no_other_meta():
    test_str = '2019-05-25-23-20-24-EST.tif'
    mdata = metastring(test_str)
    expected = {'date': '2019-05-25',
                'time': '23-20-24-EST',
                'rstr': test_str}
    assert(expected == mdata)

    test_str = '2019-05-25-23-20-24-EST_.tif'
    mdata = metastring(test_str)
    expected = {'date': '2019-05-25',
                'time': '23-20-24-EST',
                'rstr': test_str}
    assert(expected == mdata)

    test_str = '23-20-24-EST.tif'
    mdata = metastring(test_str)
    expected = {'time': '23-20-24-EST',
                'rstr': test_str}
    assert(expected == mdata)

    test_str = '23-20-24-EST_.tif'
    mdata = metastring(test_str)
    expected = {'time': '23-20-24-EST',
                'rstr': test_str}
    assert(expected == mdata)


def test_blank_value():
    test_str = '2019-04-26_run-_reactor-7.tif'
    mdata = metastring(test_str)
    expected = {'date': '2019-04-26',
                'run': '',
                'reactor': '7',
                'rstr': test_str}
    assert(expected == mdata)


def test_blank_key():
    test_str = '2019-04-26_-2_reactor-7.tif'
    mdata = metastring(test_str)
    expected = {'date': '2019-04-26',
                '': '2',
                'reactor': '7',
                'rstr': test_str}
    assert(expected == mdata)


def test_blank_kvpair():
    test_str = '2019-04-26_run-2__reactor-7.tif'
    with pytest.raises(Exception):
        assert(metastring(test_str))


def test_multipair():
    test_str = '2019-04-26_run-2-3_reactor-7.tif'
    with pytest.raises(Exception):
        assert(metastring(test_str))


def test_warn_reserved():
    test_str = '2019-04-26_run-2_rstr-7.tif'
    with pytest.warns(UserWarning):
        assert(metastring(test_str))

    test_str = '2019-04-26_run-2_date-7.tif'
    with pytest.warns(UserWarning):
        assert(metastring(test_str))

    test_str = '2019-04-26_run-2_time-7.tif'
    with pytest.warns(UserWarning):
        assert(metastring(test_str))
