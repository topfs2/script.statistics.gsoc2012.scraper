from urlparse import urlsplit, urlunsplit
from urllib import urlencode, quote_plus, unquote_plus
import string

def removeFromStackAndRecurse(url):
	url = urlsplit(url)
	netloc = url.netloc
	if "@" in netloc:
		netloc = netloc[netloc.index("@") + 1:]

	netloc_list = netloc.split(" , ") if url.scheme == "stack" else [ netloc ]
	newnetloc_list = list()

	for n in netloc_list:
		netloc_unquoted = unquote_plus(n)
		if netloc_unquoted != n:
			newnetloc_list.append(quote_plus(removeFromStackAndRecurse(netloc_unquoted)))

	netloc = string.join(newnetloc_list, " , ")

	return urlunsplit((url.scheme, netloc, url.path, url.query, url.fragment))


def main():
	test = "http://foo:bar@foobar:9090/file.mp3"

	#print "Input simple", test
	#print "Removed", removeUserPass(test)

	smb1 = urlunsplit(("smb", "foo:bar@foobar:9090", "file.rar", None, None))
	print "SMB1 Base", smb1

	smb_quoted1 = quote_plus(smb1)
	#print smb_quoted

	rar1 = urlunsplit(("rar", "bar:foo@" + smb_quoted1, "file.avi", None, None))
	print "RAR1 on SMB1", rar1

	smb2 = urlunsplit(("smb", "foo:bar@foobar2:9090", "file2.rar", None, None))
	print "SMB2 Base", smb2

	smb_quoted2 = quote_plus(smb2)
	#print smb_quoted

	rar2 = urlunsplit(("rar", "bar:foo@" + smb_quoted2, "file2.avi", None, None))
	print "RAR2 on SMB2", rar2

	rar1 = quote_plus(rar1)
	rar2 = quote_plus(rar2)

	stack = urlunsplit(("STACK", "fjo:bja@" + rar1 + " , " + rar2, "", None, None))
	print "Stacked", stack
	#print "", removeUserPass(rar)
	r = removeFromStackAndRecurse(stack)
	print "Removed all passwords", r

	t = removeFromStackAndRecurse(stack)
	unquoted = unquote_plus(urlsplit(t).netloc)
	print "The stacked URL", [unquote_plus(s) for s in unquoted.split(" , ")]

if __name__ == "__main__":
	main()
