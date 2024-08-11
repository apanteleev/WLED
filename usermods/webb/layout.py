import math
import numpy as np
import re
import sys
import os.path
from typing import Tuple

ledsPerSegment = 13
hexHeight = 178.3
hexSide = hexHeight * math.tan(math.radians(30))

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

def sequence(basePath: str, directionPath: str, count: int = ledsPerSegment) -> np.array:
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
print(innerStrip.shape)
print(outerStrip.shape)

amax = np.amax(outerStrip)


innerStrip = np.array(innerStrip / amax * 16384, dtype=np.int32)
outerStrip = np.array(outerStrip / amax * 16384, dtype=np.int32)

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.degrees(np.arctan2(y, x)) 
    phi = np.select([np.less(phi, 0), np.greater(phi, 0)], [phi + 360.0, phi], 0)
    phi = phi * (16384.0 / 360.0)
    return(rho, phi)

innerStripPolar = np.array(cart2pol(innerStrip[:, 0], innerStrip[:, 1]), dtype=np.int32).transpose()
outerStripPolar = np.array(cart2pol(outerStrip[:, 0], outerStrip[:, 1]), dtype=np.int32).transpose()

def writePoints(file, data, name, length):
    file.write(f'static const int {name}[{data.shape[0]}][2] = {{\n')
    for row in range(data.shape[0]):
        file.write(f'  {{ {data[row][0]}, {data[row][1]} }},\n')
    file.write('};\n\n')

filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../wled00/webb_leds.h')
with open(filename, 'w') as file:
    file.write('// GENERATED BY usermods/webb/layout.py - DO NOT MODIFY\n\n')
    file.write(f'#define WEBB_LEDS_INNER {innerStrip.shape[0]}\n')
    file.write(f'#define WEBB_LEDS_OUTER {outerStrip.shape[0]}\n')
    minRadius = np.amin(innerStripPolar[:, 0])
    maxRadius = np.amax(outerStripPolar[:, 0])
    file.write(f'#define WEBB_RADIUS_MIN {minRadius}\n')
    file.write(f'#define WEBB_RADIUS_MAX {maxRadius}\n')
    file.write('\n')
    writePoints(file, innerStrip, 'g_InnerStripCartesian', 'WEBB_LEDS_INNER')
    writePoints(file, outerStrip, 'g_OuterStripCartesian', 'WEBB_LEDS_OUTER')
    file.write('\n')
    file.write('// Polar coordinated. Angle is from 0 to 16k.\n')
    writePoints(file, innerStripPolar, 'g_InnerStripPolar', 'WEBB_LEDS_INNER')
    writePoints(file, outerStripPolar, 'g_OuterStripPolar', 'WEBB_LEDS_OUTER')



if False:
    from matplotlib import pyplot
    pyplot.scatter(innerStrip[:, 0], innerStrip[:, 1])
    pyplot.scatter(outerStrip[:, 0], outerStrip[:, 1])
    pyplot.show()