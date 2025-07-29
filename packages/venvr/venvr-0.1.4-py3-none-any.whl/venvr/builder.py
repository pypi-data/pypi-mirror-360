import os, inspect
from .util import Basic
from .templates import RTMP, PTMP

class Builder(Basic):
	def __init__(self, name, config):
		self.name = name
		self.config = config

	def build(self):
		self.log("build")
		self.dir()
		self.env()
		self.deps()

	def dir(self):
		bp = self.config.path.base
		self.log("dir", bp)
		os.makedirs(bp)

	def env(self):
		vp = self.config.path.venv
		self.log("env", vp)
		self.out("python3 -m venv %s"%(vp,))

	def deps(self):
		deps = self.config.deps
		self.log("deps", *deps)
		for dep in deps:
			self.install(dep)

	def install(self, package):
		self.log("install", package)
		path = self.config.path
		pipper = path.pip
		if type(package) is str:
			return self.out("%s install %s"%(pipper, package))
		# git installation
		gp = package["git"]
		pjoin = os.path.join
		gdir = gp.split("/").pop()
		os.chdir(path.base)
		self.out("git clone https://github.com/%s.git"%(gp,))
		self.out("ln -s %s"%(pjoin(gdir, package["sym"]),))
		os.chdir(pjoin("..", ".."))
		self.out("%s install -r %s"%(pipper, pjoin(path.base, gdir, package["requirements"])))

	def register(self, func, port):
		cfg = self.config
		fsrc = inspect.getsource(func)
		name = fsrc.split(" ", 1).pop(1).split("(", 1).pop(0)
		rp = self.based("%s.py"%(name,))
		cfg.path.run.update(name, rp)
		caller = fsrc.startswith("class") and "%s(log)"%(name,) or name
		self.log("register", name, rp)
		codestring = (cfg.persistent and PTMP or RTMP)%(fsrc, caller)
		if cfg.persistent:
			codestring = codestring.replace("PID", str(os.getpid()))
			codestring = codestring.replace("PORT", str(port))
		with open(rp, "w") as f:
			f.write(codestring)
		return name