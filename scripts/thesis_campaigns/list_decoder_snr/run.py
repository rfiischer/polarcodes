"""


Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.main import main

if __name__ == "__main__":
    snr_vec = [1, 1.5, 2, 2.5]
    for snr in snr_vec:
        main("parameters/batch_0.ini", {'POLAR': {'base_design_snr': snr},
                                        'GENERAL': {'log_file': '"log/{}_log.log"'.format('snr_' + str(snr)),
                                                    'results_dir': '"results/{}/"'.format('snr_' + str(snr))},
                                        'RUN': {'num_workers': 16,
                                                'frame_pack_size': 16}})