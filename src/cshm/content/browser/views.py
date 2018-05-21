# -*- coding: utf-8 -*-
from cshm.content import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from Products.CMFPlone.utils import safe_unicode
import logging


class RegCourse(BrowserView):

    template = ViewPageTemplateFile("template/reg_course.pt")

    def __call__(self):
        self.portal = api.portal.get()

        return self.template()


class CourseListing(BrowserView):

    template = ViewPageTemplateFile("template/course_listing.pt")

    def __call__(self):
        self.portal = api.portal.get()
        self.echelonBrain = api.content.find(context=self.portal, Type='Echelon')

        return self.template()
