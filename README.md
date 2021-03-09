# Grand Challenge: Live Video Streaming

This repository contains the simulator code being used for Live Video Streaming.  The simulator is a frame-level DASH video streaming simulator with a pluggable client module for bitrate control and latency control.

## Files

![Image text](https://github.com/tse-hou/Live-Video-Streaming-Challenge/blob/master/architecture.gif)

The simulator contains the following files:

* `run.py` : An SDK to call the SIM and ABR
* `ABR.py` : your ABR algorithm
* `fixed_env.py` : SIM code simulates live streaming player download, play, card, skip frame, etc
* `load_trace.py` : load trace to memory

The folder `dataset` contains the network traces and video traces.  Please see the README.md file in the dataset directory for decsription of the dataset.

# The Simulator

The simulator simulates a live video player，including downloading and playback of video frames.  It reads as inputs:

1. A video trace, which contains the size of each video frame in a video file.
2. A network trace, which contains the network throughput at each time instance.
3. The bitrate control and latency control algorithm provided by participant.

The simulator output the following:

|   params           | params description                       |  example   |
| ------------------ | ---------------------------------------- | ---------- |
| time(s)            | physical time                            |   0.46(s)  |
| time_interval(s)   | duration in this cycle                   |   0.012(s) |  
| send_data_size(bit)| The data size downloaded in this cycle   |   14871(b) |
| frame_time_len(s)  | The time length of the frame currently   |   0.04(s)  |
| rebuf(s)           | The rebuf time of this cycle             |   0.00(s)  |
| buffer_size(s)     | The buffer size time length              |   1.26(s)  |
| play_time_len(s)   | The time length of playing in this cycle |   0.012(s) |
| end_delay(s)       | Current end-to-to delay                  |   1.31(s)  |
| cdn_newest_id      | Cdn the newest frame id                  |   85       |
| download_id        | Download frame id                        |   41       |
| cdn_has_frame      | cdn cumulative frame info                |   1.31(s)  |
| decision_flag      | Gop boundary flag or I frame flag        |   False    |
| buffer_flag        | Whether the player is buffering          |   False    |
| cdn_rebuf_flag     | Whether the cdn is rebuf                 |   False    |
| end_of_video       | Whether the end of video                 |   False    |

## Requirement

You will need Python 3 to run the simulator.

## Running the Simulator

To run the simulator, you execute

```
python run.py all
```

The given default code should produce something like the following:

```
YYF_2018_08_12,low: Done
game,fixed: Done
game,low: Done
room,low: Done
AsianCup_China_Uzbekistan,low: Done
Fengtimo_2018_11_3,low: Done
Fengtimo_2018_11_3,fixed: Done
room,medium: Done
Fengtimo_2018_11_3,medium: Done
game,medium: Done
AsianCup_China_Uzbekistan,fixed: Done
YYF_2018_08_12,fixed: Done
sports,fixed: Done
room,fixed: Done
AsianCup_China_Uzbekistan,medium: Done
sports,low: Done
YYF_2018_08_12,medium: Done
sports,medium: Done
AsianCup_China_Uzbekistan,high: Done
game,high: Done
YYF_2018_08_12,high: Done
Fengtimo_2018_11_3,high: Done
sports,high: Done
room,high: Done
[[1003.0643755032955, 1.4848107451463873e-06], [1468.1899223244538, 1.4225835587652947e-06], [1515.4896973625787, 1.4499867526933675e-06], [1535.3410570279666, 1.3545695121573868e-06], [996.4359586392395, 1.5619065521992875e-06], [1360.1296820536336, 1.6087132511847381e-06], [1634.203817372895, 1.5164349390184837e-06], [1944.3635834321335, 1.6719062312119671e-06], [962.1517246733974, 1.4780837156406462e-06], [1391.4320800027003, 1.6092656549056967e-06], [1632.4709275956995, 1.5909295776093931e-06], [1862.3119642996699, 1.5455924096654674e-06], [1022.4077588924314, 1.6270570546929787e-06], [1399.8878565939472, 1.6120530396826196e-06], [1647.239833065784, 1.4675038108408778e-06], [1867.1238357565812, 1.645161480200095e-06], [918.3925549314956, 1.451731368019917e-06], [1268.203516951356, 1.443557658036437e-06], [1303.9777877439697, 1.379908865609856e-06], [1324.7899687878103, 1.391296779288731e-06], [963.301917210777, 1.6739684119299014e-06], [1415.9670930158863, 1.4867778805828403e-06], [1619.5561920445957, 1.8365560589165313e-06], [1846.2505164302045, 1.674857947344337e-06]]
[1.41261182e+03 1.54105055e-06]

```

## Configuring the Simulator

* run all video_trace and network_trace
```
python run.py all
```

* run specific video_trace and network_trace
```
python run.py [video_trace] [network_trace]
```

* The simulator can produce detailed log files for debugging.  To turn this on, set the variable `DEBUG` to `True`.  By default, the logs will be written to a sub-directory called `log`.  This log directory can be changed by setting the `LOG_FILE_PATH` variable.  Note that you may want to set `DEBUG` to `False` if you are training an AI model as large volume of data may be written to disk when logging is on.