import subprocess
import os, sys

def clone():
	init_list = open('init_list.txt', 'r').read().split('\n')
	for x in init_list:
		if x == '': continue
		name = x.split('/')
		if name[-1] == '':
			name = name[:-1]
		name = name[-1]
		print 'Cloning %s to %s.............' % (x, name)
		subprocess.call('git clone ' + x + ' data' + os.path.sep + name, shell=True)

def checkout():
	init_list = open('init_list.txt', 'r').read().split('\n')
	for x in init_list:
		if x == '': continue
		name = x.split('/')
		if name[-1] == '':
			name = name[:-1]
		name = name[-1]
		os.chdir('data' + os.path.sep + name)
		print 'Cloning %s to %s.............' % (x, name)
		subprocess.call('git checkout', shell=True)
		os.chdir('..\\..')

if __name__ == '__main__':
	t = sys.argv[1]
	if t == 'clone':
		clone()
	elif t == 'checkout':
		checkout()
	else:
		print 'WRONG ARG'