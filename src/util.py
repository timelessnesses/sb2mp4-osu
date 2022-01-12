def applyVariables(line, variables):
	if not "$" in line:
		return line
	for entry in variables:
		line = line.replace(entry[0], entry[1])
	return line

def removeQuotes(string):
	return string[1:-1] if string.startswith('"') and string.endswith('"') else string

def s(s):
		if type(s) is float:
			return ""
		if type(s) is int:
			return "" if s == 1 else "s"
		return "" if len(s) == 1 else "s"