from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element

from KUtils.Typing import *

def textas(el: Element, type: Type[T]) -> T:
    return type(el.text)

def attras(el: Element, attr: str, type: Type[T], default=None) -> T:
    return type(el.get(attr, default=default))

def indented(elem: Element, level=0) -> None:
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indented(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
# def all_attrs(el: Element) -> T:
#