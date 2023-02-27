from subprocess import run, CompletedProcess, PIPE, CalledProcessError
def cmd(*args, timeout=60,shell=True, check=True,**kwargs) -> CompletedProcess | None:
    try:
        cp = run(*args, timeout=timeout, shell=shell, check=True, stdout=PIPE, stderr=PIPE, **kwargs)
    except CalledProcessError as ce:
        print(ce.stderr.decode(encoding='utf-8'))
    else:
        return cp 

class Package:
    dependencies: list["str|Package"] = []

    def __init__(self, version: str = "latest"):
        self.version = version

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def doc(self):
        return self.__class__.__doc__

    def dependency_check(self):
        if not self.dependencies:
            return
        for deps in self.dependencies:
            if not isinstance(deps, Package):
                raise Exception
            deps.build()


    def build(self):
        self.dependency_check()
        self.install()

    def install(self):
        raise NotImplementedError
        

