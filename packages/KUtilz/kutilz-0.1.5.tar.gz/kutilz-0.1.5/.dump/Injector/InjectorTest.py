from HooksInjector import HooksInjector


# class InjectorB(BaseInjector):
#     pass

class Dummy:
    @HooksInjector.Inject()
    def yeet(self):
        print('YEETING0')

    def __init__(self):
        self.hooks = HooksInjector(self)
        self.hooks.call_all()

class Dummy2:
    @HooksInjector.Inject()
    def yeet(self):
        print('I dont know how to yeet')
class BigDummy(Dummy, Dummy2):
    @HooksInjector.Inject()
    def yeet(self):
        print('YEETING1')

dummy = BigDummy()
# yeeted = dummy.yeet()
# print(yeeted)
print('finished')