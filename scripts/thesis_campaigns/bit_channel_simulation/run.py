"""


Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.main import main

if __name__ == "__main__":
    for base_design_snr in [130, 129, 13]:
        main("parameters/batch_0.ini", {'POLAR': {'base_design_snr': base_design_snr},
                                        'GENERAL': {'log_file': '"log/{}_log.log"'.format('b_' + str(base_design_snr)),
                                                    'results_dir': '"results/{}/"'.format('b_' + str(base_design_snr))},
                                        'RUN': {'num_workers': 16,
                                                'frame_pack_size': 16}})
