"""


Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.main import main

if __name__ == "__main__":
    workers = [1, 2, 4, 6, 8, 10, 12, 14, 16]
    for num_workers in workers:
        main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"{}"'.format('bhattacharyya')},
                                        'GENERAL': {'log_file': '"log/{}_log.log"'.format('bhattacharyya' +
                                                                                          str(num_workers)),
                                                    'results_dir': '"results/{}/"'.format('bhattacharyya' +
                                                                                          str(num_workers))},
                                        'RUN': {'num_workers': num_workers,
                                                'frame_pack_size': num_workers}})
