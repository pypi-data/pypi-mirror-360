import os
import time

import logging
logging.basicConfig(level=logging.DEBUG)

# from livenodes import Node, Producer, Graph, get_registry
from livenodes_core_nodes.in_data import In_data
# from livenodes_core_nodes.in_playback import In_playback
from livenodes_core_nodes.out_data import Out_data


if __name__ == '__main__':
    os.chdir('./sl')

    # print('=== Construct Pipeline ====')
    # channel_names_raw = ['EMG1', 'Gonio2', 'AccLow2']
    # # channel_names_fts = ['EMG1__calc_mean', 'Gonio2__calc_mean', 'AccLow2__calc_mean']
    # channel_names_fts = ['EMG1__rms', 'Gonio2__calc_mean', 'AccLow2__calc_mean']
    # recorded_channels = [
    #     'EMG1', 'EMG2', 'EMG3', 'EMG4',
    #     'Airborne',
    #     'AccUp1', 'AccUp2', 'AccUp3',
    #     'Gonio1',
    #     'AccLow1', 'AccLow2', 'AccLow3',
    #     'Gonio2',
    #     'GyroUp1', 'GyroUp2', 'GyroUp3',
    #     'GyroLow1', 'GyroLow2', 'GyroLow3']

    meta = {
        "sample_rate": 400,
        "channels": [    "EMG1",
                "ACC_X",
                "ACC_Y",
                "ACC_Z",
                "MAG_X",
                "MAG_Y",
                "MAG_Z"],
        "targets": ["None", "Left Right"]
    }

    # # pipeline = In_playback(compute_on="1", block=False, files="./data/KneeBandageCSL2018/**/*.h5", meta=meta)
    # pipeline = In_playback(block=False, files="./data/bub/*.h5", meta=meta, annotation_holes="None")
    pipeline = In_data(files="./data/bub/*.h5", meta=meta, emit_at_once=1, compute_on=3)

    out = Out_data(folder="data/test/", compute_on=1)
    out.connect_inputs_to(pipeline)

    # channel_names = ['Gonio2', 'GyroLow1', 'GyroLow2', 'GyroLow3']
    # idx = np.isin(recorded_channels, channel_names).nonzero()[0]

    # # draw = Draw_lines(name='Raw Data', compute_on="1")
    # draw = Draw_lines(name='Raw Data', compute_on="1:1")
    # # draw = Draw_lines(name='Raw Data', compute_on="")
    # draw.connect_inputs_to(pipeline)

    # print('=== Load Pipeline ====')
    # pipeline = Node.load('./pipelines/recognize.json')
    # pipeline = Node.load('./pipelines/preprocess.json')
    # pipeline = Node.load('./pipelines/train.json')
    # pipeline = Node.load('./pipelines/preprocess_no_vis.json')
    # pipeline = Node.load('./pipelines/recognize_no_vis.json')

    pipeline.start()
    time.sleep(10)
    # time.sleep(1000000)
    pipeline.stop()
