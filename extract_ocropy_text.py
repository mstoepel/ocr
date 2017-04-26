#!/usr/bin/env python
"""Extract text from ocropus outputs.
This concatenates the individual text fragments, from left to right and then
top to bottom.
It orders the fragments by y-midpoint, then uses x coordinates to order
overlapping fragments.
Input is an hOCR file (from ocropus-hocr).
Output is text, printed to stdout.
"""

import re
import sys


from bs4 import BeautifulSoup


def overlapping(a, b):
    """Two lines are overlapping if >50% of either is in the other."""
    overlap = min(a['y2'], b['y2']) - max(a['y1'], b['y1'])
    height = min(a['y2'] - a['y1'], b['y2'] - b['y1'])
    x_overlap = min(a['x2'],b['x2']) - max(a['x1'],b['x1'])
    return 1.0 * overlap / height > 0.5 and x_overlap > 0

def y_overlapping(a, b):
    overlap = min(a['y2'], b['y2']) - max(a['y1'], b['y1'])
    height = min(a['y2'] - a['y1'], b['y2'] - b['y1'])
    return 1.0 * overlap / height > 0.5

def close_enough(a,b):
    """Two lines are pretty close to each other, so we should put them on the same line"""
    y_distance = b['y1'] - a['y2']
    x_overlap = min(a['x2'],b['x2']) - max(a['x1'],b['x1'])
    return y_distance < 40  and x_overlap > 0  #change 90 to a relative variable, not hard coded

def remove_bottom(a):
    """If text at the very bottom of the page, remove it"""
    y_coords = a['y1']
    return y_coords > 5500

def sort_lines(lines):
    lines = lines[:]

    # First, sort by combination of y and x, so that goes down columns first
    lines.sort(key=lambda line: (8*line['x1'] + line['y1']))

    for a, b in zip(lines[:-1], lines[1:]):
        if close_enough(a, b):
            b['continuation'] = True

    for a in lines:
        if remove_bottom(a):
            a['remove'] = True

    return lines

def hocr_to_lines(hocr_path):
    lines = []
    soup = BeautifulSoup(file(hocr_path))
    for tag in soup.select('.ocr_line'):
        m = re.match(r'bbox (-?\d+) (-?\d+) (-?\d+) (-?\d+)', tag.get('title'))
        assert m
        x0, y0, x1, y1 = (int(v) for v in m.groups())
        lines.append({
            'text': tag.text,
            'x1': x0,
            'y1': y0,
            'x2': x1,
            'y2': y1  # note swap
        })
    # hOCR specifies that y-coordinates are from the bottom.
    # We fix that here. We don't know the height of the image, so we use the
    # largest y-value in its place.
    h = max(line['y1'] for line in lines)
    for line in lines:
        line['y1'] =  line['y1']
        line['y2'] =  line['y2']
    return lines


if __name__ == '__main__':
    _, hocr_path = sys.argv
    f = open('ocr_output.txt','w')
    lines = hocr_to_lines(hocr_path)
    lines = sort_lines(lines)
    print lines

    output = ''
    for idx, line in enumerate(lines):
        if idx > 0:
            if line.get('continuation'):
                output += '  '
            else:
                output += '\n'
        if 'text' in line and not line.get('remove'):
            output += line['text']
        # if line.get('remove'):
        #     del line
    f.write(output.encode('utf8'))
    f.close()
    # print output

