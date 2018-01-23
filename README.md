# Flexible-GFDM-PHY
This repository includes the FPGA implementation of a GFDM based transceiver running on National Instruments USRP.

A more detailed description is available in the documentation folder and on the website http://owl.ifn.et.tu-dresden.de.

Notes:
- The USRP1700 driver should be installed.
- Currently the USRP-RIOs with the 40 MHz frontends are fully supported. The 120 MHz frontends are known to work, however the gain setting cannot be changed.

Known Bugs:
- The path to the preamble file has to be fixed in ImportTxtFileToComplex_Preamble.gvi to Host\preamble.txt
- Tha AGC is prone to oscillate. The workaround is to fix the reciever gain to a fixed value.
