import time, rel
from fyg.util import Loggy
from catmail.config import config

class Scanner(Loggy):
	def __init__(self, reader):
		if type(reader) == str: # reader is addr
			from catmail.reader import Reader
			reader = Reader(reader)
		self.scanners = {}
		self.reader = reader
		if not config.sync:
			self.ticker = rel.timeout(None, self.tick)

	def criteria(self, sender=None, subject=None, unseen=True):
		crits = []
		if sender:
			crits.append('FROM "%s"'%(sender,))
		if subject:
			crits.append('SUBJECT "%s"'%(subject,))
		if unseen:
			crits.append("UNSEEN")
		return "(%s)"%(" ".join(crits),)

	def scan(self, sender=None, subject=None, unseen=True, count=1, mailbox="inbox"):
		return self.check(self.criteria(sender, subject, unseen), count, mailbox)

	def check(self, crit="UNSEEN", count=1, mailbox="inbox"):
		self.log("scanning", mailbox, "for", crit)
		return self.reader.inbox(count, crit, mailbox=mailbox)

	def tick(self):
		founds = []
		for crit, scanner in self.scanners.items():
			msgs = self.check(crit, scanner["count"], scanner["mailbox"])
			if msgs:
				for msg in msgs:
					scanner["cb"](msg)
				founds.append(crit)
		for found in founds:
			del self.scanners[found]
		if self.scanners:
			if config.sync:
				time.sleep(config.scantick)
				self.tick()
			else:
				return True
		else:
			self.log("stopping scanner")

	def on(self, scanopts, cb=None, count=1, mailbox="inbox"):
		crit = self.criteria(**scanopts)
		shouldstart = not self.scanners
		self.log("watching for", crit)
		self.scanners[crit] = {
			"count": count,
			"mailbox": mailbox,
			"cb": cb or self.reader.show
		}
		if shouldstart:
			self.log("starting scanner")
			if config.sync:
				self.tick()
			else:
				self.ticker.add(config.scantick)