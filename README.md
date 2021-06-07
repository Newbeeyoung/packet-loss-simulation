#Packet Loss Simulation in Video Streaming

Modification of github repo [https://github.com/sumanth232/vlc-streaming-mininet](https://github.com/sumanth232/vlc-streaming-mininet). Video stream is transmitted in a 2-switch network, each swith is connect to one host.
## Preprocess Video Data

Run the python script `utils.convert_video_to_h264.py`, convert video to h.264

## Prepare Environment
Firstly, install [pox](https://noxrepo.github.io/pox-doc/html/#getting-the-code-installing-pox) and [Mininet](http://mininet.org/download/). Requires Python 2+. Then place the controller `linear_2snh_ssim_Controller_QoS.py` into the location:
```
$ cp contoller/linear_2snh_ssim_Controller_QoS.py ~/pox/pox/misc
```

Secondly, start running the controller `linear_2snh_ssim_Controller_QoS.py`:
```
$ pox/pox.py log.level --DEBUG misc.linear_2snh_ssim_Controller_QoS
```
## Run Packet Loss Simulation
Running the shell script as root for packet loss with 5 level of severity (1%, 2%, 3%, 4% and 6% packet loss):
```
$ sh packet_loss.sh
```


