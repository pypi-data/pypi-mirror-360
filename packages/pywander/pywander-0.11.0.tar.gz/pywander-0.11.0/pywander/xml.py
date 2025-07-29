#!/usr/bin/env python
# -*-coding:utf-8-*-


from lxml import etree


def load_xml(text):
    doc = etree.XML(text)
    return doc


def unload_xml(doc):
    content = etree.tostring(doc, pretty_print=True, encoding='utf8').decode()
    return content


def doc_xpath(doc, xpath_syntax):
    """
    返回可能是单个或多个element对象，甚至可能是简单的文本，具体要看xpath的语法。
    """
    e = doc.xpath(xpath_syntax)
    return e


def replace_e_text(e, new_text):
    e.text = new_text