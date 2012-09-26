Dear Helber,

Below is a description of how to upgrade to 2011_01_13 version.

Please use ftp client to connect ftp.cameo.com.tw. And username and password is
rd3raywu.
The image is in "/rd3raywu/Upload/011311/2011_01_13_libs.rar". Please extract the
file and check md5 file.

Please login with root account on DUT, and execute below commands.

1) dd if=2011_01_13_nblock5.img of=/dev/nblock5
2) reboot

When DUT is ready, please login again. Then execute below commands.

1) umount /opt/qt
2) umount /conf
3) flash_erase /dev/mtd0 0 8
4) dd if=2011_01_13_jffs2.img of=/dev/mtdblock0
5) dd if=2011_01_13_nblock9.img of=/dev/nblock9
6) sync
Reboot

Thank you!

Regards,
Frank
