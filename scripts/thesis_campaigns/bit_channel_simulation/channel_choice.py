"""


Created on 17/09/2020 16:40

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import numpy as np
import matplotlib.pyplot as plt

from tcc.coding.polarcoding.construction import tahir


marker_style_0 = dict(color='tab:blue', linestyle='', marker='o',
                      markersize=10, markerfacecoloralt='tab:red')

marker_style_1 = dict(color='tab:red', linestyle='', marker='*',
                      markersize=10, markerfacecoloralt='tab:red')

n = 8
start_snr = 2
end_snr = 5

counter = 0
for i in range(2 ** n):
    start_ref = tahir(n, start_snr)[1][i]
    end_ref = tahir(n, end_snr)[1][i]
    nums = np.where(
                    (
                     (tahir(n, start_snr)[1] > start_ref) &
                     (tahir(n, end_snr)[1] < end_ref)
                    )
                   )

    if nums[0].size != 0:
        counter += 1
        print(i, nums, min(np.max(tahir(n, start_snr)[1][nums[0]] - start_ref),
                           np.max(- tahir(n, end_snr)[1][nums[0]] + end_ref)))


plt.semilogy(tahir(n, start_snr)[1][[128, 10, 12, 17, 18, 20, 33]], fillstyle='none', **marker_style_0)
plt.semilogy(tahir(n, end_snr)[1][[128, 10, 12, 17, 18, 20, 33]], fillstyle='none', **marker_style_1)

plt.show()
