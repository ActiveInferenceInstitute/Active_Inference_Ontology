# DOWNLOAD

Currently the virtual machine file can be downloaded by request to ActiveInference@gmail.com

If you want to set up purely from scratch, obtain a Ubuntu 22.04 Server distribution, and run the commands in the text file:
SigmaVM_Full_History.txt



# SETUP

In VirtualBox, or equivalent virtualization software.

Set up a new 64 bit Ubuntu VM.

Attach the provided .vdi image (Ubuntu 22.04 1 LTS) as the only hard drive.

Change the settings in VirtualBox, so that the primary network connection is "Bridged"

Set 20+ GB of RAM.



# RUN:

Run the VM and when it's done with initial display, log in with:

User:    theuser
PW:      theuser

First run the command

>> source .bashrc

Wait for 5 minutes.

Run this exact command following the >> (including the $)

>> $CATALINA_HOME/bin/startup.sh

It will be finished in a second and then check IP address with

>> ip a

Note the IP address and go to the browser in the host machine and use this URL

http://IP_ADDRESS_HERE:8080/sigma/login.html

http://10.0.0.95:8080/sigma/login.html

Also you may benefit by waiting 5 minutes after running the CATALINA script, for all Sigma services to initialize.




