import imaplib
from fyg.util import Loggy
from email import message_from_bytes
from catmail.config import config

class Reader(Loggy):
	def __init__(self, addr):
		self.addr = addr
		if addr:
			self.isgmail = config.gmailer or addr.endswith("@gmail.com")
			self.domain = self.isgmail and "imap.gmail.com" or addr.split("@").pop()

	def connect(self, mailbox="inbox"):
		self.conn = imaplib.IMAP4_SSL(self.domain)
		self.conn.login(self.addr, config.cache("email password? "))
		self.conn.select(mailbox)

	def disconnect(self):
		self.conn.close()
		self.conn.logout()
		self.conn = None

	def ids(self, criteria="UNSEEN", critarg=None):
		typ, msgids = self.conn.search(None, criteria, critarg)
		return msgids[0].split()[::-1]

	def fetch(self, num, mparts="(RFC822)"):
		typ, data = self.conn.fetch(num, mparts)
		return message_from_bytes(data[0][1])

	def read(self, msg, variety="plain"):
		bod = msg
		if msg.is_multipart():
			for part in msg.walk():
				if part.get_content_type() == "text/%s"%(variety,):
					bod = part
		return bod.get_payload(decode=True).decode()

	def show(self, msg, variety="plain"): # or html
		body = self.read(msg, variety)
		self.log("\n\nfrom:", msg['from'], "\nsubject:",
			msg['subject'], "\n\nbody:", body)
		return body

	def inbox(self, count=1, criteria="UNSEEN", critarg=None, mailbox="inbox"):
		msgs = []
		self.connect(mailbox)
		for num in self.ids(criteria, critarg)[:count]:
			msgs.append(self.fetch(num))
		self.disconnect()
		return msgs

	def view(self, count=1, criteria="UNSEEN", critarg=None, mailbox="inbox"):
		for msg in self.inbox(count, criteria, critarg, mailbox):
			self.show(msg)
