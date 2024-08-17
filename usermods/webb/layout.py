import math
import numpy as np
import re
import sys
import os.path
from typing import Tuple

ledsPerSegment = 13
hexHeight = 178.3
hexSide = hexHeight * math.tan(math.radians(30))
distanceBetweenLeds = hexSide / ledsPerSegment # approximate, upper limit

vecUpRight = np.array([hexSide / 2, hexHeight / 2])
vecUpLeft = vecUpRight * np.array([-1, 1])
vecDownLeft = -vecUpRight
vecDownRight = -vecUpLeft
vecRight = np.array([hexSide, 0])
vecLeft = -vecRight

directions = {
    'UL': vecUpLeft,
    'UR': vecUpRight,
    'R': vecRight,
    'DR': vecDownRight,
    'DL': vecDownLeft,
    'L': vecLeft
}

def path(s: str) -> np.array:
    """
    Converts a string formatted like 'UR UL R DL' into a vector representing the location in a hex grid.
    """
    components = np.array([directions[segment] for segment in s.split()])
    return np.sum(components, axis=0)

segmentRegex = re.compile(r'([A-Z]+)([0-9]+)?')

def distribute(base: np.array, desc: str, defaultCount: int) -> Tuple[np.array, np.array]:
    """
    Creates an array of 'count' points uniformly distributed along a vector specified by 'description' starting at 'base'.
    """
    match = segmentRegex.match(desc)
    if match is None:
        print(f'Invalid segment description {desc}!')
        sys.exit(1)
    dir = match.group(1)
    count = int(match.group(2)) if match.group(2) is not None else defaultCount

    extent = directions[dir]
    stride = extent / count
    return (np.array([base + stride * (i + 0.5) for i in range(count)]), extent)

segmentBounds = []
currentLed = 0

def sequence(basePath: str, directionPath: str, count: int = ledsPerSegment) -> np.array:
    global currentLed
    start = path(basePath)
    result = np.ndarray(shape=(0,2))
    for segment in directionPath.split():
        skip = segment.startswith('!')
        if skip:
            segment = segment[1:]
            start += directions[segment]
        else:
            (segment, offset) = distribute(start, segment, count)
            result = np.concatenate((result, segment), axis=0)
            start += offset
            actualCount = segment.shape[0]
            segmentBounds.append((currentLed, currentLed + actualCount - 1))
            currentLed += actualCount
    return result

innerStrip = np.concatenate([
        sequence('UL', 'R DR DL L UL UR'),
        sequence('UL', 'UL UR R DR !DL UR R DR DL !L R DR DL L !UL DR DL L UL !UR DL L UL UR !R L UL UR R'),
        sequence('UL UL UR', 'UL'),
        sequence('UR UR UL', 'UR'),
        sequence('UR UR R', 'UR'),
        sequence('R R UR', 'R'),
        sequence('R R DR', 'R'),
        sequence('DR DR R', 'DR'),
        sequence('DR DR DL', 'DR'),
        sequence('DL DL DR', 'DL'),
        sequence('DL DL L', 'DL'),
        sequence('L L DL', 'L'),
        sequence('L L UL', 'L'),
        sequence('UL UL L', 'UL')
    ], axis=0
)

outerStrip = sequence('UL UL UR UL', 'UR R14 DR R DR14 R DR14 DL DR DL14 DR DL14 L DL L14 '
                      'DL L14 UL L UL14 L UL14 UR UL UR14 UL UR14 R UR R14')

combinedStrip = np.concatenate([innerStrip, outerStrip], axis = 0)

def findAdjacentIndices(baseIndex):
    basePos = combinedStrip[baseIndex]
    adjIndices = []
    for index in range(len(combinedStrip)):
        if index == baseIndex:
            continue
        currentPos = combinedStrip[index]
        distance = np.linalg.norm(currentPos - basePos)
        if distance < distanceBetweenLeds * 1.5:
            adjIndices.append(index)
    return adjIndices

adjacency = []
for beginIndex, endIndex in segmentBounds:
    beginAdjacent = findAdjacentIndices(beginIndex)
    endAdjacent = findAdjacentIndices(endIndex)
    beginAdjacent = [ i for i in beginAdjacent if i < beginIndex or i > endIndex ]
    endAdjacent = [ i for i in endAdjacent if i < beginIndex or i > endIndex ]
    assert 1 <= len(beginAdjacent) <= 2
    assert 1 <= len(endAdjacent) <= 2
    adjacency.append([
        beginIndex, endIndex,
        beginAdjacent[0], beginAdjacent[1] if len(beginAdjacent) > 1 else -1,
        endAdjacent[0], endAdjacent[1] if len(endAdjacent) > 1 else -1
    ])
    # print(f'{beginAdjacent} <- [{beginIndex} .. {endIndex}] -> {endAdjacent}')
    
def amendWithDirection(adj):
    if adj < 0:
        return adj
    for beginIndex, endIndex in segmentBounds:
        if adj == beginIndex:
            return adj
        elif adj == endIndex:
            return adj | 1024
    print(f'led {adj} is neither beginning nor end of any segment')
    assert(False)

for vec in adjacency:
    for i in range(2, 6):
        vec[i] = amendWithDirection(vec[i])

adjacency = np.array(adjacency, dtype=int)

amax = np.amax(combinedStrip)

combinedStrip = np.array(combinedStrip / amax * 16384, dtype=np.int32)

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.degrees(np.arctan2(y, x)) 
    phi = np.select([np.less(phi, 0), np.greater(phi, 0)], [phi + 360.0, phi], 0)
    phi = phi * (16384.0 / 360.0)
    return(rho, phi)

combinedStripPolar = np.array(cart2pol(combinedStrip[:, 0], combinedStrip[:, 1]), dtype=np.int32).transpose()

def write2DArray(file, data, name, length):
    file.write(f'static const int16_t {name}[{length}][{data.shape[1]}] = {{\n')
    for row in range(data.shape[0]):
        col = ', '.join([str(x) for x in data[row]])
        file.write(f'  {{ {col} }},\n')
    file.write('};\n\n')

filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../wled00/webb_leds.h')
with open(filename, 'w') as file:
    file.write('// GENERATED BY usermods/webb/layout.py - DO NOT MODIFY\n\n')
    file.write(f'#define WEBB_LEDS_INNER {innerStrip.shape[0]}\n')
    file.write(f'#define WEBB_LEDS_OUTER {outerStrip.shape[0]}\n')
    file.write(f'#define WEBB_LEDS_COMBINED {combinedStrip.shape[0]}\n')
    file.write(f'#define WEBB_SEGMENTS {adjacency.shape[0]}\n')
    file.write(f'#define WEBB_ADJACENT_DOWN 1024\n')

    minRadius = np.amin(combinedStripPolar[:, 0])
    maxRadius = np.amax(combinedStripPolar[:, 0])
    file.write(f'#define WEBB_RADIUS_MIN {minRadius}\n')
    file.write(f'#define WEBB_RADIUS_MAX {maxRadius}\n')
    file.write('\n')

    write2DArray(file, combinedStrip, 'g_WebbPositionsCartesian', 'WEBB_LEDS_COMBINED')

    file.write('// Polar coordinates. Angle is from 0 to 16k.\n')
    write2DArray(file, combinedStripPolar, 'g_WebbPositionsPolar', 'WEBB_LEDS_COMBINED')

    file.write('// Linear segments and adjacency.\n')
    file.write('// [First, Last, FirstAdj0, FirstAdj1, LastAdj0, LastAdj1]\n')
    file.write('// When adjacent segment indices go down, its index is ORed with WEBB_ADJACENT_DOWN.\n')
    write2DArray(file, adjacency, 'g_WebbSegments', 'WEBB_SEGMENTS')



if False:
    from matplotlib import pyplot
    pyplot.scatter(combinedStrip[:, 0], combinedStrip[:, 1])
    pyplot.show()