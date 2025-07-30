from KUtils.MetaProgramming.CodeGen.Writer import CodeWriter
from BoilerplateWriter import BoilerplateWriter
path = '/home/kai/@Work/alg/cv2d_monorepo/KUtils/KUtils/MetaProgramming/CodeGen/Playground.py'

if __name__ == '__main__':
    from Boilerplates.AttrMixin import SomeSetupMixin

    to_write = ['context', 'controller']

    patch = BoilerplateWriter.SearchAndReplace(SomeSetupMixin, 'some', targets=to_write)

    writer = CodeWriter(path)
    writer.dummy_inject(patch)