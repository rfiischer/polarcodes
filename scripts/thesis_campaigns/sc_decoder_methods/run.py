"""


Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.main import main

if __name__ == "__main__":
    methods = ['bhattacharyya', 'tahir', 'mdega', 'dega']
    for method in methods:
        main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"{}"'.format(method)},
                                        'GENERAL': {'log_file': '"log/{}_log.log"'.format('m_' + method),
                                                    'results_dir': '"results/{}/"'.format('m_' + method)},
                                        'RUN': {'num_workers': 16,
                                                'frame_pack_size': 16}})
