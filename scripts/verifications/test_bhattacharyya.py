"""


Created on 10/03/2020 16:06

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from coding.polarcoding.construction import bhattacharyya

n = 5
des_snr = 0

for i in range(1, n + 1):
    print(bhattacharyya(i, des_snr))
    print('\n')

print(bhattacharyya(10, des_snr))
