# Flexible-GFDM-PHY

This repository is not longer maintained. Please check: https://fusionforge.zih.tu-dresden.de/projects/flexiblegfdmphy/ for the latest version. 


------------------------------------------------------------------------------------------------------------------------------

This repository includes the FPGA implementation of a GFDM based transceiver running on National Instruments USRP using LabVIEW Communications System Design Suite 2.0

A more detailed description is available in the documentation folder and on the website http://owl.ifn.et.tu-dresden.de.

Notes:
- The latest USRP1700 driver must be installed! However, now all projects created and saved by this computer require the latest USRP driver!
- Currently the USRP-RIOs with the 40 MHz frontends are fully supported. The 120 and 160 MHz frontends are known to work, however the gain setting cannot be changed or have strange behaviour.

Ideally the transceiver is tried out using a cable between the most left TX and the most right RX port with a 30dB-attenuator and with a fixed 37 dB receiver gain setting. The transceiver only creates packets if data is created at the host side. After the transceiver runs over the cable, antennas can be used.

Updated Synchronization - recommended parameters:
shift_threshold = -2;
min_threshold = 0,001;
preamble scale = 7;
CFO removal = false;
