import os
import sys
import serial
import time
import threading 

global serial_dev
serial_dev = None
device_descripter = ""
brate = ""
read_thread_should_die = False

def write(serial_device):
	# serial_device.flush()
	while True:
		print("output: ", serial_device.out_waiting, "input: ", serial_device.in_waiting)
		buffer = input("hello enter me: ")
		serial_device.write(bytes(buffer, encoding='utf8'))
		time.sleep(1)

def read_thread_body(serial_device):
	last = ""
	cur = ""
	while True:
		if serial_device.in_waiting > 0:		
			cur = serial_device.readline()
			print("\n")
			print("got something", str(cur))
			print("\n")
		else:

			time.sleep(0.1)

		if read_thread_should_die:
			break


if __name__ == '__main__':
	try:

		print("args:")
		for x in sys.argv:
			print(x)
			pass
		
		print(len(sys.argv))
		if len(sys.argv) == 3:
			device_descripter =sys.argv[1]
			brate = sys.argv[2]
		else:
			print("expected format: device_descripter brate")


		serial_dev = serial.Serial(device_descripter, brate, timeout=0)
		read_thread = threading.Thread(target=read_thread_body, name = "read_thread", args=(serial_dev,))
		read_thread.setDaemon(True)
		write_thread = threading.Thread(target=write, name = "write_thread", args=(serial_dev,))
		write_thread.setDaemon(True)
		read_thread.start()
		write_thread.start()

	except KeyboardInterrupt:
		read_thread_should_die = True
		sys.exit()

	if read_thread.isAlive():
		read_thread.join()
