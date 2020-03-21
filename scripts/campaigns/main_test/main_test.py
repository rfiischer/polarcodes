"""


Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.main import main

methods = ['bhattacharyya', 'tahir', 'mdega', 'dega']

for method in methods:
    main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"{}"'.format(method)},
                                    'GENERAL': {'log_file': '"log/{}_log.log"'.format(method),
                                                'results_dir': '"results/{}/"'.format(method)}})
