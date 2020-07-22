"""


Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.main import main

if __name__ == "__main__":
    list_sizes = [1, 2, 4, 8, 16, 32]
    for list_size in list_sizes:
        main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"{}"'.format('bhattacharyya'),
                                                  'list_size': list_size},
                                        'GENERAL': {'log_file': '"log/{}_log.log"'.format('bhattacharyya' +
                                                                                          str(list_size)),
                                                    'results_dir': '"results/{}/"'.format('bhattacharyya' +
                                                                                          str(list_size))},
                                        'RUN': {'num_workers': 1,
                                                'frame_pack_size': 1}})
