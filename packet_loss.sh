#!/bin/sh

for s in 1 2 3 4 6
do
  sudo -S python packet_loss_simulation.py --switch_loss $s
done
