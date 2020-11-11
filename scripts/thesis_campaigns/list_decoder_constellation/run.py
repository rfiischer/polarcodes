"""


Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.main import main

if __name__ == "__main__":
    for list_size in [1, 8]:
        main("parameters/batch_0.ini", {'POLAR': {'list_size': list_size,
                                                  'construction_method': '"dega"'},
                                        'GENERAL': {'log_file': '"log/{}_log.log"'.format('ldega_' + str(list_size)),
                                                    'results_dir': '"results/{}/"'.format('ldega_' + str(list_size))},
                                        'RUN': {'num_workers': 16,
                                                'frame_pack_size': 16}})

        main("parameters/batch_0.ini", {'POLAR': {'list_size': list_size,
                                                  'construction_method': '"mdega"'},
                                        'GENERAL': {'log_file': '"log/{}_log.log"'.format('lmdega_' + str(list_size)),
                                                    'results_dir': '"results/{}/"'.format('lmdega_' + str(list_size))},
                                        'RUN': {'num_workers': 16,
                                                'frame_pack_size': 16}})
