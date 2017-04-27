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
import pandas as pd
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
    dims = re.search(r'(-?\d{4}) (-?\d{4})',soup.select('.ocr_page')[0].get('title'))
    width, length = (int(v) for v in dims.groups())
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
    return lines, width, length


if __name__ == '__main__':
    _, hocr_path = sys.argv
    f = open('ocr_output.txt','w')
    lines,width,length = hocr_to_lines(hocr_path)
    lines = sort_lines(lines)
    df = pd.DataFrame(index=[i for i in range(14)],columns=['Owner_1','Owner_2','Location','Description','Construction Value','Permit Fee'])
    #print lines
    output = ''
    for idx, line in enumerate(lines):
        # if idx > 0:
            # if line.get('continuation'):
            #     output += '  '
            # else:
            #     output += '\n'
        if line.get('remove'):
            lines.pop(idx)
            idx =- idx
            break
        if lines[idx+1].get('continuation'):
            lines[idx] = lines[idx]['text'] + " " + lines[idx+1]['text']
        if line.get('continuation'):
            lines.pop(idx)
            idx =- idx
            break
        if 'text' in line and not line.get('remove'):
            output += line['text']
            for i in range(84):
                if i in (1,3,5,7,9,11,13,15,17,19,21,23,25,27):
                    df.set_value((i-1)//2,'Owner_1',lines[i-1]['text'])
                elif i in (2,4,6,8,10,12,14,16,18,20,22,24,26,28):
                    df.set_value((i-1)//2,'Owner_2',lines[i-1]['text'])
                elif i in (29,30,31,32,33,34,35,36,37,38,39,40,41,42):
                    df.set_value((i%28)-1,'Location',lines[i]['text'])
                elif i in (43,44,45,46,47,48,49,50,51,52,53,54,55,56):
                    df.set_value((i%42)-1,'Description',lines[i]['text'])
                elif i in (57,58,59,60,61,62,63,64,65,66,67,68,69,70):
                    df.set_value((i%56)-1,'Construction Value',lines[i]['text'])
                elif i in (71,72,73,74,75,76,77,78,79,80,81,82,83,84):
                    df.set_value((i%70)-1,'Permit Fee',lines[i]['text'])
    f.write(output.encode('utf8'))
    f.close()
    print df
    # print lines[0]
    # for idx, line in enumerate(lines):
    #     if line.get('remove'):
    #         lines.pop(idx)
    # print lines
