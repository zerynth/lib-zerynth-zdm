ZDM Lib
========

ZDM Lib repository contains Zerynth Libraries to use ZDM (Zerynth Device Manager).

zlib_zdm.py contains classes and method definition to connect to the ZDM, send and receive messages.
zlib_zdm_fota.py contains methods to allow user to schedule FOTA(firmware over the air).

Clone this git repository and copy these two files into your project directory.

In the examples directory there are three different main files ready to be uplinked on your device.


With ingestion.py your device will send random data to the ZDM that can be used to test zdm immediately.
Jobs.py enables your device to receive and respond to two different jobs (job1 and job2).
Fota.py enables your device only to receive fota commands after you have uploaded your firmwares to ZDM.

To see how to use these files with more details, see the How To Use guide.