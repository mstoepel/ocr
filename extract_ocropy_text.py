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
import numpy as np

def classify_text(lines):
    """ Classify ocr elements based on their location on the page. We pretty much know what is what based on its location"""
    lines = lines[:]
    for line in lines:
        if np.average([line['x1'],line['x2']]) > 860 and np.average([line['x1'],line['x2']]) < 1600:
            line['type'] = 'Owner'
        elif np.average([line['x1'],line['x2']]) > 1900 and np.average([line['x1'],line['x2']]) < 2600:
            line['type'] = 'Location'
        elif np.average([line['x1'], line['x2']]) > 2800 and np.average([line['x1'], line['x2']]) < 3600:
            line['type'] = 'Description'
        elif np.average([line['x1'], line['x2']]) > 4000 and np.average([line['x1'], line['x2']]) < 4300:
            line['type'] = 'Construction Value'
        elif np.average([line['x1'], line['x2']]) > 4400 and np.average([line['x1'], line['x2']]) < 4700:
            line['type'] = 'Permit Fee'
        else:
            line['type'] = 'Garbage'
        if np.average([line['y1'],line['y2']]) > 5500 or np.average([line['y1'],line['y2']]) < 500:
            line['type'] = 'Garbage'

    return lines

def y_overlapping(a, b):
    overlap = min(a['y2'], b['y2']) - max(a['y1'], b['y1'])
    height = min(a['y2'] - a['y1'], b['y2'] - b['y1'])
    return 1.0 * overlap / height > 0.5

def close_enough(a,b):
    """Two or more lines are pretty close to each other, so we should put them on the same line"""
    y_distance = b['y1'] - a['y2']
    x_overlap = min(a['x2'],b['x2']) - max(a['x1'],b['x1'])
    return abs(y_distance) < 100  and x_overlap > 0  #change 90 to a relative variable, not hard coded

def sort_lines(lines):
    lines = lines[:]
    for a, b in zip(lines[:-1], lines[1:]):
        if close_enough(a, b):
            b['continuation'] = True
    return lines

def hocr_to_lines(hocr_path):
    lines = []
    soup = BeautifulSoup(file(hocr_path))
    dims = re.search(r'(-?\d{4}) (-?\d{4})',soup.select('.ocr_page')[0].get('title'))
    width, length = (int(v) for v in dims.groups())
    # for page in soup.select('.ocr_page'):
    #     i = 0
    #     p = re.match(r'image houses\\(0\d+)',page.get('title'))
    #     assert p
    #     pg = p.groups()[i]
    for tag in soup.select('.ocr_line'):
        # if re.match(r'image houses\\(0\d+)',tag.fetchParents()[i].get('title')) == pg: # figure out a way to only work on line if on appropriate page. currently repeating
        p = re.match(r'image houses\\(0\d+)',tag.fetchParents()[0].get('title'))
        assert p
        pg = p.groups()[0]
        # print pg
        m = re.match(r'bbox (-?\d+) (-?\d+) (-?\d+) (-?\d+)', tag.get('title'))
        assert m
        x0, y0, x1, y1 = (int(v) for v in m.groups())
        lines.append({
            'text': tag.text,
            'x1': x0,
            'y1': y0,
            'x2': x1,
            'y2': y1,
            'page': pg
        })
    # i +=1
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
    lines =  sort_lines(lines)
    lines = classify_text(lines)
    output = ''
    # print lines
    for idx, line in enumerate(lines):
        if line.get('remove'):
            lines.pop(idx)
    for idx, line in enumerate(lines):
        if lines[idx].get('continuation'):
            if lines[idx-1].get('continuation'):
                if lines[idx-2].get('continuation'):
                    if lines[idx-3].get('continuation'):
                        pass
                    else:
                        lines[idx-3]['text'] = lines[idx-3]['text'] + " " + lines[idx]['text']
                        lines[idx]['type'] = 'Garbage'
                else:
                    lines[idx-2]['text'] = lines[idx-2]['text'] + " " + lines[idx]['text']
                    lines[idx]['type'] = 'Garbage'
            else:
                lines[idx-1]['text'] = lines[idx-1]['text'] + " " + lines[idx]['text']
                lines[idx]['type'] = 'Garbage'
    # for idx, line in enumerate(lines):
    #     if line.get('continuation'):
    #         lines.pop(idx)
    # for idx, line in enumerate(lines):
    #     if line.get('type') == 'Garbage':
    #         lines.pop(idx)
    # print len(lines)
    [lines.pop(idx) for idx, line in enumerate(lines) if line.get('type') == 'Garbage']

    # check = ['Owner','Owner','Location','Description','Construction Value','Permit Fee']
    #
    # for i in range(len(lines)):
    #     if lines[i]['type'] != check[i%6]:
    #         lines.insert(i,{'text':'Filler','type':check[i%5]})

    # print type(lines)

    owners = [line['text'] for idx, line in enumerate(lines) if line['type'] == 'Owner']
    locations = [line['text'] for idx, line in enumerate(lines) if line['type'] == 'Location']
    descriptions = [line['text'] for idx, line in enumerate(lines) if line['type'] == 'Description']
    con_val = [line['text'] for idx, line in enumerate(lines) if line['type'] == 'Construction Value']
    perm_fee = [line['text'] for idx, line in enumerate(lines) if line['type'] == 'Permit Fee']
    page = [line['page'] for i in range(len(owners))]

    # print len(owners)
    # print len(locations)
    # print len(descriptions)
    # print len(con_val)
    # print len(perm_fee)
    #
    # print type(descriptions)
    descriptions.extend(["hi","hey"])

    # print len(descriptions)

    df = pd.DataFrame({'Owner':owners,'Location':locations,'Description':descriptions,'Construction Value':con_val,'Permit Fee':perm_fee})

    f.write(output.encode('utf8'))
    f.close()
    # print df[97:111]['Description']
    # print df.iloc[103]['Description']
    df.to_csv('output.csv')

    print df
    ## missing page 9 of 10 shed 8" x 12". not even in 0009 folder. must be gpageseg issue? or was it tagged as garbage?
    #  THE PROBLEM IS THAT SHED 8 x 12 IS GETTING CONNECTED TO 1701 MASCOUTAH AV #16. NEED TO KEEP THE LINES SEPARATED.
    # SOMEHOW GETTING CONNECTED WITH THE LOCATION IN THAT ROW. FIX THAT
