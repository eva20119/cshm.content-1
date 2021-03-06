# -*- coding: utf-8 -*-
from plone.indexer.decorator import indexer
from zope.interface import Interface
from Products.CMFPlone.utils import safe_unicode
from cshm.content.content.echelon import IEchelon
from cshm.content.content.teacher import ITeacher
from mingtak.ECBase.browser.views import SqlObj
from cshm.content.content.subject import ISubject
from cshm.content.content.officialdoc import IOfficialDoc


@indexer(ITeacher)
def idCardNo_indexer(obj):
    return obj.idCardNo


@indexer(ITeacher)
def activation_indexer(obj):
    return obj.activation


@indexer(IOfficialDoc)
def docsWorkflow_indexer(obj):
    users = obj.workflowStatus.split(',')
    return users


@indexer(IOfficialDoc)
def docHeader_indexer(obj):
    return obj.docHeader


@indexer(IOfficialDoc)
def docSN_indexer(obj):
    return obj.docSN


@indexer(ITeacher)
def teachSubjects_indexer(obj):
    ts = obj.teachSubjects
    tsList = []
    for item in ts:
        tsList.append(item.to_object.title)
    return tsList


@indexer(IEchelon)
def regDeadline_indexer(obj):
    return obj.regDeadline


@indexer(IEchelon)
def classStatus_indexer(obj):
    return obj.classStatus


@indexer(IEchelon)
def quota_indexer(obj):
    return obj.qutoa


@indexer(IEchelon)
def altCount_indexer(obj):
    return obj.altCount


@indexer(IEchelon)
def studentCount_indexer(obj):
    sqlInstance = SqlObj()
    uid = obj.UID()
    sqlStr = """SELECT COUNT(id) FROM reg_course WHERE uid = '{}'""".format(uid)
    result = sqlInstance.execSql(sqlStr)
    return result[0]['COUNT(id)']


@indexer(ISubject)
def startDateTime_indexer(obj):
    return obj.startDateTime

@indexer(IEchelon)
def trainingCenterId_indexer(obj):
    return obj.trainingCenter.to_object.id


@indexer(IEchelon)
def courseStart_indexer(obj):
    return obj.courseStart

@indexer(IEchelon)
def courseEnd_indexer(obj):
    return obj.courseEnd
