# -*- coding: utf-8 -*-
from cshm.content import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from mingtak.ECBase.browser.views import SqlObj
import json
import datetime
import pdfkit
import wkhtmltopdf
import weasyprint


class ReceiptList(BrowserView):
    template = ViewPageTemplateFile("template/receipt_list.pt")
    def __call__(self):
        self.portal = api.portal.get()
        context = self.context

        uid = context.UID()
        sqlInstance = SqlObj()
        # 正取名單
        sqlStr = """SELECT reg_course.*,receipt_money.money FROM reg_course LEFT JOIN receipt_money ON receipt_money.user_id = reg_course.id 
                    WHERE reg_course.uid = '{}' and isAlt = 0 and on_training = 1 ORDER BY reg_course.seatNo""".format(uid)
        self.admit = sqlInstance.execSql(sqlStr)
        sqlStr = """SELECT id,user_id FROM receipt WHERE is_cancel = 0"""
        receipt = sqlInstance.execSql(sqlStr)
        idDict = {}
        for item in receipt:
            idList = item[1].split(',')
            for id in idList:
                if id:
                    idDict[id] = item[0]
        self.idDict = idDict
        return self.template()


class AdminReceiptList(BrowserView):
    template = ViewPageTemplateFile("template/admin_receipt_list.pt")
    def __call__(self):
        request = self.request
        sqlInstance = SqlObj()
        sqlStr = """SELECT * FROM receipt WHERE is_cancel = 0 AND is_check = 0 ORDER BY receipt_date"""
        self.result = sqlInstance.execSql(sqlStr)
        return self.template()


class ReceiptCreateView(BrowserView):
    template = ViewPageTemplateFile("template/receipt_create.pt")
    def __call__(self):
        request = self.request
        userList = request.get("userList", "")
        if userList:
            userList = json.loads(userList)
            if type(userList) == int:
                userList = [userList, 'aa']
            sqlInstance = SqlObj()
            sqlStr = """SELECT name,tax_no,company_name,receipt_money.money FROM reg_course LEFT JOIN receipt_money ON receipt_money.user_id = 
                        reg_course.id WHERE reg_course.id in {}""".format(tuple(userList))
            result = sqlInstance.execSql(sqlStr)
            title = ''
            totalMoney = 0
            for item in result:
                name = item[0]
                self.tax_no = item[1] if item[1] != 'None' and item[1] else ''
                money = item[3]
                company_name = item[2]

                if money:
                    totalMoney += money

                if company_name:
                    title = company_name
                elif title:
                    title+= ',%s' %name
                else:
                    title = name

            self.title = title
            self.totalMoney = totalMoney
            try:
                userList.remove('aa')
            except:
                pass
            self.userList = userList

        return self.template()


class DoReceiptCreate(BrowserView):
    def __call__(self):
        request = self.request
        uid = self.context.UID()
        sqlInstance = SqlObj()
        user_id = json.loads(request.get('user_id'))
        total_money = request.get('total_money')
        type = request.get('type')
        apply_date = request.get('apply_date')
        receipt_date = request.get('receipt_date')
        title = request.get('title')
        tax_no = request.get('tax_no')
        note = request.get('note')
        detail1_money = request.get('detail1_money')
        detail2_money = request.get('detail2_money')
        detail1_name = request.get('detail1_name')
        detail2_name = request.get('detail2_name')
        detail1_note = request.get('detail1_note')
        detail2_note = request.get('detail2_note')
        user_name = api.user.get_current().getUserName()
        training_center = self.context.trainingCenter.to_object.title
        if training_center == '台北職訓中心':
            training_center = '北訓'
        elif training_center == '基隆職訓中心':
            training_center = '基訓'
        elif training_center == '桃園職訓中心':
            training_center = '桃訓'
        elif training_center == '中壢職訓中心':
            training_center = '壢訓'
        elif training_center == '台中職訓中心':
            training_center = '中訓'
        elif training_center == '花蓮職訓中心':
            training_center = '花訓'
        elif training_center == '嘉義職訓中心':
            training_center = '嘉訓'
        elif training_center == '高雄職訓中心':
            training_center = '高訓'
        elif training_center == '南科職訓中心':
            training_center = '南訓'

        sqlStr = """SELECT MAX(serial_number) FROM receipt WHERE training_center = '{}'""".format(training_center)
        serial_number = sqlInstance.execSql(sqlStr)[0][0]
        if serial_number:
            serial_number += 1
        else:
            serial_number = 1

        year = datetime.datetime.now().year - 1911

        ids = ''
        for id in user_id:
            ids += '%s,' %id

        detail = detail1_name + '/' + detail1_money + '/' + detail1_note + ',' +detail2_name + '/' + detail2_money + '/' + detail2_note
        sqlStr = """INSERT INTO `receipt`(`uid`, `user_id`, `money`, `type`, `receipt_date`, `apply_date`, `title`, `tax_no`, `note`,
                    `detail`, `undertaker`, training_center, serial_number, year) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}',
                    '{}','{}',{}, {})""".format(uid, ids, total_money, type, receipt_date, apply_date, title, tax_no, note, detail,
                    user_name, training_center, serial_number, year)

        sqlInstance.execSql(sqlStr)
        request.response.redirect(self.context.absolute_url() + '/@@receipt_list')


class UpdateReceiptMoney(BrowserView):
    def __call__(self):
        try:
            request = self.request
            money = int(request.get('money'))
            user_id = int(request.get('user_id'))
            uid = self.context.UID()
            sqlInstance = SqlObj()
            sqlStr = """SELECT id FROM receipt_money WHERE user_id = {}""".format(user_id)
            check = sqlInstance.execSql(sqlStr)
            if check:
                sqlStr = """UPDATE receipt_money SET money = {} WHERE user_id = {}""".format(money, user_id)
                sqlInstance.execSql(sqlStr)
            else:
                sqlStr = """INSERT INTO receipt_money(user_id, money, uid) VALUES({}, {}, '{}')""".format(user_id, money, uid)
                sqlInstance.execSql(sqlStr)
            return 'success'
        except  Exception as e:
            print e
            return 'error'


class ReceiptApplyForm(BrowserView):
    template = ViewPageTemplateFile('template/receipt_apply_form.pt')
    def __call__(self):
        request = self.request
        user_id = request.get('user_id')
        sqlInstance = SqlObj()
        sqlStr = """SELECT * FROM reg_course WHERE id = '{}'""".format(user_id)
        self.result = sqlInstance.execSql(sqlStr)
        return self.template()


class CancelReceipt(BrowserView):
    def __call__(self):
        request = self.request
        receipt_id = request.get('receipt_id')
        if receipt_id:
            sqlInstance = SqlObj()
            sqlStr = """UPDATE receipt SET is_cancel = 1 WHERE id = {}""".format(int(receipt_id))
            sqlInstance.execSql(sqlStr)
            request.response.redirect('%s/@@receipt_list' %self.context.absolute_url())


class ReceiptDetail(BrowserView):
    template = ViewPageTemplateFile("template/receipt_detail.pt")
    def __call__(self):
        request = self.request
        receipt_id = request.get('receipt_id')
        if receipt_id:
            sqlInstance = SqlObj()
            sqlStr = """SELECT * FROM receipt WHERE id = {}""".format(receipt_id)
            self.result = sqlInstance.execSql(sqlStr)
            self.receipt_id = receipt_id
        return self.template()


class PassReceipt(BrowserView):
    def __call__(self):
        request = self.request
        receipt_id = request.get('receipt_id')
        if receipt_id:
            sqlInstance = SqlObj()
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            user_name = api.user.get_current().getUserName()
            sqlStr = """UPDATE receipt SET is_check = 1,check_date = '{}',inspector = '{}'  WHERE id = {}""".format(now, user_name, receipt_id)
            self.result = sqlInstance.execSql(sqlStr)
            request.response.redirect('%s/@@admin_receipt_list' %self.context.absolute_url())


class DownloadReceiptPdf(BrowserView):
    template = ViewPageTemplateFile("template/receipt_pdf_template.pt")
    def __call__(self):
        request = self.request
        receipt_id = request.get('receipt_id')
        sqlInstance = SqlObj()

        sqlStr = """SELECT * FROM receipt WHERE id = {}""".format(receipt_id)
        self.result = sqlInstance.execSql(sqlStr)
        self.trainingCenter = self.context.trainingCenter.to_object.title

        return self.template()
