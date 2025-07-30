import smtplib, yagmail, rel
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fyg.util import Named
from catmail.util import TMP, strip_html
from catmail.config import config

class Mailer(Named):
	def __init__(self, addr, mailername=None):
		self.addr = addr
		self.name = mailername
		self._yag = None
		self._smtp = None
		self.queue = []
		self.cbs = {}
		self.churning = False
		if not addr:
			config.verbose and self.log('no email address configured')
		elif config.gmailer or "gmail.com" in addr:
			if self.name:
				mailer = {}
				mailer[addr] = self.name
			elif "gmail.com" in addr:
				mailer = addr.split("@")[0]
			else:
				mailer = addr
			try:
				self._yag = yagmail.SMTP(mailer, config.cache("email password? "))
			except:
				self._yag = yagmail.SMTP(mailer, config.cache("email password? ", overwrite=True))
		else:
			self._smtp = smtplib.SMTP('localhost')

	def _refresh(self):
		self.log('refreshing smtp connection')
		if self._yag:
			self._yag.login(config.cache("email password? "))
			self._yag.send_unsent()
		elif self._smtp:
			self._smtp = smtplib.SMTP('localhost')

	def _noop(self):
		if (self._yag and self._yag.is_closed) or (self._smtp and self._smtp.noop()[0] != 250):
			self._refresh()

	def _prep(self, *args):
		if str == bytes: # is python 2.7
			return [(a and type(a) == unicode and a.encode("utf-8") or a) for a in args]
		return args

	def _body(self, sender, to, subject, body):
		if config.html:
			mpmsg = MIMEMultipart('alternative')
			mpmsg['Subject'] = subject
			mpmsg['From'] = sender
			mpmsg['To'] = to
			mpmsg.attach(MIMEText(strip_html(body), 'plain'))
			mpmsg.attach(MIMEText(body.replace("\n", "<br>"), 'html'))
			return mpmsg.as_string()
		else:
			return TMP%(sender, to, subject, body)

	def _emit(self, to, subject, body, bcc):
		self.log('emailing "', subject, '" to', to)
		if self._yag: # bcc yagmail only!
			try: # failures probs handled by _refresh()...
				self._yag.send(to, subject, body, bcc=bcc)
			except (smtplib.SMTPServerDisconnected, smtplib.SMTPDataError) as e:
				self.log("smtp error (will try again):", str(e))
			if self._yag.unsent:
				self._refresh()
		elif self._smtp:
			sender = self.name and "%s <%s>"%(self.name, self.addr) or self.addr
			try:
				self._smtp.sendmail(self.addr, to, self._body(sender, to, subject, body))
			except smtplib.SMTPRecipientsRefused:
				self.log("Recipient Refused:", to)
				if "refused" in self.cbs:
					self.cbs["refused"](to)

	def _sender(self):
		while len(self.queue):
			to, subject, body, bcc = self.queue.pop(0)
			self._noop()
			self._emit(to, subject, body, bcc)
		self.log(config.sync and "finished sending" or "closing mail thread")
		self.churning = False

	def _send(self, to, subject, body, bcc):
		if to.endswith("@gmail.com"):
			while to.endswith(".@gmail.com"): # ridiculous
				self.log('dropped trailing "." from ridiculous email:', to)
				to = to.replace(".@gmail.com", "@gmail.com")
			while ".." in to:
				to = to.replace("..", ".")
		self.log('enqueueing email "', subject, '" to', to)
		self.queue.append([to, subject, body, bcc])
		if not self.churning:
			self.churning = True
			if config.sync:
				self.log("running _sender")
				self._sender()
			else:
				self.log('spawning mail thread')
				rel.thread(self._sender)

	def on(self, event_name, cb):
		self.cbs[event_name] = cb

	def mail(self, to=None, sender=None, subject=None, body=None, html=None, bcc=None):
		if not self._yag and not self._smtp:
			self.log('email attempted to', to)
			self.log("## content start ##")
			self.log(body)
			self.log("## content end ##")
			return self.log("failed to send email -- no MAILER specified!")
		to, subject, body, html = self._prep(to, subject, body, html)
		self._send(to, subject, html or body, bcc) # ignore sender -- same every time

	def admins(self, subject, body, eset="contacts"):
		acfg = config.admin
		admins = acfg.get(eset)
		if not admins and eset != "contacts":
			self.log("no", eset, "configured - defaulting to contacts")
			eset = "contacts"
			admins = acfg.get(eset)
		admins or self.log("(no admins specified)")
		self.log("emailing admins (", eset, "):", subject)
		if len(body) > 100:
			self.log(body[:100], " ...")
		else:
			self.log(body)
		for admin in admins:
			self.mail(to=admin, subject=subject, body=body)

	def reportees(self, subject, body):
		self.admins(subject, body, "reportees")
