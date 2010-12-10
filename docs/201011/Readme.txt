

System upgrade

Download new firmware from ftp and check files with md5.

1)unrar 2010_11_23_libs.rar to a USB flash disk.
2)power-up DUT board and plug-in the flash disk to front usb slot.
3)telnet to the device
	IP:192.168.0.80
	username: root
	password: cameo123
4)stop Arora:
	ps aux | grep arora
	kill arora.pid
	
5)switch directory to "/mnt/usb-front
	command: cd /mnt/usb-front

start to upgrade ( some of them may take time to finish )
6)	command: umount /opt/mrua_dcchd
7)	command: umount /opt/qt
8)	command: dd if=2010_11_23_nblock5.img of=/dev/nblock5
9)	command: dd if=2010_11_23_nblock8.img of=/dev/nblock8
10)	command: dd if=2010_11_23_nblock9.img of=/dev/nblock9

11) when the process is finished. rebooting the board.

PS. DO NOT RESET or REBOOT the device during system upgrade.


Release Notes:

caMediaPlayer:
1. adding 2 functions to show part of Arora(OSD) over Video layer.
	toSetHolePositionAndSize( int idx, int x, int y, int w, int h );	// to create hole
	toDelHole( int idx );	// to delete hole
	PS. we only support 1 hole now, and may support more in the future.
	
2. allowing users to change context while the player is on STOP mode.

caNetConfigObj:
	our new javascript object. 
	For more information, please read "releasenote_caNetConfigObj.txt" and try it's sample "caFB_test5.html"

