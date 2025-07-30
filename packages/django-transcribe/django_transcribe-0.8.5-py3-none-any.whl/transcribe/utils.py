import logging
from os import path

from transcribe import settings

# from transcribe import models

log = logging.getLogger(__name__)


def sort_diffs(diffs):
    """
    Sort the diffs list so that text with differences (options) is separate
    from text where there are no differences
    (and therefore no need to have options).
    Also, make sure there are always 2 options if diffs exist
    and make sure the first option is never empty.
    And do some other filtering to simplify things.
    """
    new_diffs = []
    for i, diff in enumerate(diffs):
        d = diffs[i]
        # text with no differences:
        # we can append some text to the list
        if d[0] == 0:
            new_diffs.append(d[1])
        # text with differences:
        # we append a list (2 text items) to the list
        else:
            if len(new_diffs) > 0 and type(new_diffs[-1]) is list:
                # append to existing options
                if d[1] != '':
                    new_diffs[-1].append(d[1])
            else:
                # create new options
                if d[1] != '':  # ensures that the first option has content
                    new_options = []
                    new_options.append(d[1])
                    new_diffs.append(new_options)
    # make sure there are always 2 options for diffs
    for i, diff in enumerate(new_diffs):
        if type(new_diffs[i]) is list:
            if len(new_diffs[i]) == 1:
                new_diffs[i].append('')  # append an empty diff
    # remove any diff where one option is a space and the other is empty
    # for i, diff in enumerate(new_diffs):
    #     if type(new_diffs[i]) is list:
    #         if new_diffs[i][0] == " " and new_diffs[i][1] == "":
    #             new_diffs[i] = ""
    # remove any diff where the options are the same except for an extra space
    for i, diff in enumerate(new_diffs):
        if type(new_diffs[i]) is list:
            if new_diffs[i][0].strip() == new_diffs[i][1].strip():
                new_diffs[i] = new_diffs[i][0]

    return new_diffs


def html_diffs(diffs):
    """
    Generate html text from a list of diffs
    marking up the differences as options.
    """
    html = ''
    diffs = sort_diffs(diffs)
    for d in diffs:
        if type(d) is list:
            # the sort_diffs function ensures that
            # there will always be 2 options
            # and the first option will never be empty
            # FIRST DIFF OPTION
            html += '<span class="opts">'
            html += '<span class="opt'
            if set(d[0]) <= set('\r\n'):  # contains only empty and/or newlines
                html += ' optEmpty'
            # prioritize d[0] as firstOption unless it contains only newlines
            # and d[1] contains more than newlines
            if set(d[0]) <= set('\r\n') and set(d[1]) > set('\r\n'):
                html += ' optHidden'
            else:
                html += ' firstOption'
            html += f'">{d[0]}</span>'
            # SECOND DIFF OPTION
            html += '<span class="opt'
            # prioritize d[1] too
            if set(d[0]) <= set('\r\n') and set(d[1]) > set('\r\n'):
                html += ' firstOption'
            else:
                html += ' optHidden'
            if set(d[1]) <= set('\r\n'):  # contains only empty and/or newlines
                html += ' optEmpty'
            html += f'">{d[1]}</span>'
            html += '</span>'
        else:
            # regular text (no diff)
            html += d
    return html


def remove_markup(text):
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def root_path(*paths):
    return path.join(path.abspath(settings.BASE_DIR), *paths)
