"""


Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from core.main import main
import multiprocessing as mp

methods = ['bhattacharyya', 'tahir']

# Limit the maximum number of parallel processes
max_num_of_proc = 5

if __name__ == '__main__':
    pool = mp.Pool(processes=max_num_of_proc)
    for method in methods:
        pool.apply_async(main,
                         args=("parameters/batch_0.ini",
                               {'POLAR': {'construction_method': '"{}"'.format(method)},
                                'GENERAL': {'log_file': '"log/{}_log.log"'.format(method),
                                            'results_dir': '"results/{}/"'.format(method)}}))

    pool.close()
    pool.join()
