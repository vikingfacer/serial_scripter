import os
import sys
import serial
import time
import threading 
import curses

global serial_dev
serial_dev = None
device_descripter = ""
brate = ""
close_program = False

def is_float(num : str):
	success = False
	try:
		float(num)
		success = True
	except ValueError:
		success = False
	return success

def com_sleep(arg):
	try:
		sleep_time = float(arg)
		time.sleep(sleep_time)
	except ValueError:
		print("sleep argument is bad: ", arg)	

def com_print_list(hist):
	i = 0
	for item in hist:
		i += 1
		print(i, ": ", item)

def com_get_history(hist, action):
	index = 0
	event = str()
	try:
		index = int(action)
	except ValueError:
		print("history index is bad: ", index)
	if index >= len(hist):
		print("history index is bad: ", index)
	else:
		event = hist[index]
		print(event)
	return event

def com_make_future(future, filename):
	with open(filename, 'r') as fin:
		for line in fin:
			future.append(line)
	future.reverse()

def write(serial_device):
	history_max = 10
	history = list()
	input_buffer = str()
	future = list()
	sleep_command = False
	try:
		while True:
			print("output: ", serial_device.out_waiting, "input: ", serial_device.in_waiting)
			if len(future) > 0:
				buffer = future.pop()
			else:
				buffer = input("~ ")

			command = buffer.find('!') != -1 
			command_list = buffer[1:].split()
			sleep_command = False

			if command:
				action = command_list[0]

				if len(command_list) >= 2:
					arg = command_list[1]
					if action.lower() == 'sleep':
						com_sleep(arg)
						input_buffer = "!sleep " + arg
						sleep_command = True
					if action.lower() == 'file':
						com_make_future(future, arg)
				elif len(command_list) < 2:
					if action.lower() == 'list':
						com_print_list(history)

					elif action.lower() == 'exit':
						close_program = True
						break

					elif action.isalnum():
						input_buffer = com_get_history(history, action)

			else:
				input_buffer = buffer


			history.insert(0, input_buffer)
			if not sleep_command:
				serial_device.write(bytes(input_buffer, encoding='utf8'))
				serial_device.flush()
			if len(history) >= history_max:
				history = history[1:(len(history) -1)]

			time.sleep(.1)
	except KeyboardInterrupt:
		close_program = True

def read_thread_body(serial_device):
	last = ""
	cur = ""
	while True:
		if serial_device.in_waiting > 0:		
			cur = serial_device.readline()
			print(str(cur))
		else:
			time.sleep(0.1)

		if close_program:
			break

	print(" we dead")

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
		
		read_thread.join()
		write_thread.join()
		serial_dev.close()

	except KeyboardInterrupt:
		sys.exit()

		

