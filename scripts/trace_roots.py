sep = '\\'
if os.name == 'posix':
	sep = '/'

if "SEED" in file:
	file_base = file.replace("_SEED_.txt","")
	print "processing: ", file_base
	p = subprocess.call(["imagej","-macro","C:"+sep"+Program Files"+sep"+ImageJ"+sep"+plugins"+sep"+root_tracing"+sep"+TraceMacro.txt", file_base])
	

