# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import uuid

from dateutil.relativedelta import relativedelta
import firebase_admin
from firebase_admin import messaging,firestore,credentials,auth


from pyfcm import FCMNotification

import json


# cred = credentials.Certificate("/home/anchal/Desktop/testing-odoo1-firebase-adminsdk-12kri-f42571eee6.json")
# firebase_admin.initialize_app(cred)


class PwaNotificationTemplate(models.Model):
    _name = "pwa.notification.template"
    _description = "PWA Notifictaion Template"
    
    name = fields.Char('Title')
    
    user_id = fields.Many2one('res.users','User')
    
    
    
    #################### Correct Code Start ##################################
    
    
    # def send_push(self,title,msg,registration_token,dataObject=None):
    #
    #
    #     message=messaging.MulticastMessage(notification=messaging.Notification(title=title,body=msg),data=dataObject,tokens=registration_token)
    #     response= messaging.send_multicast(message)
    #
    #     print (response)
    #
    #
    #
    #
    #
    # def pwa_send_notification_button(self):
    #     # a=messaging.getToken({vapidKey: "AAAAygzGjL0:APA91bFPB0xVuzrhyL4saAHL5I_mhkYCFXWcnB7SofYZrzz6ROTPXJ8dUxBOXMLn4CjTy-LrfsesKR_SHoFIdxtXp8cyRMuP4B0pqi8iNpufLMGw6DqKHN0CUf2GS-BNca6w3coIOryp "});
    #
    #     tokens= [self.user_id.device_token]
    #     self.send_push('Hi','Testing Message',tokens)
    

    
    
    
    
    
    
    
    #################### Correct Code End ##################################

    
    
    
    # def pwa_send_notification_button(self):
    #     topic = 'E-Com'
    #     message = messaging.Message(
    #         notification=messaging.Notification(
    #             title='The weather new  changed', body='27 °C'),
    #         topic=topic,
    #     )
    #     response = messaging.send(message)
    #
    #     print(response)
    
    
    
    
    
    # def pwa_send_notification_button(self):
    #     push_service = FCMNotification(api_key="AAAAygzGjL0:APA91bFPB0xVuzrhyL4saAHL5I_mhkYCFXWcnB7SofYZrzz6ROTPXJ8dUxBOXMLn4CjTy-LrfsesKR_SHoFIdxtXp8cyRMuP4B0pqi8iNpufLMGw6DqKHN0CUf2GS-BNca6w3coIOryp")
    #     email='ta711909@gmail.com'
    #     user=auth.get_user_by_email(email)
    #     print ("9999999999",user.uid)
    #
    #
    #     registration_id = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6IjE6ODY3Nzk3NzMyNTQxOmFuZHJvaWQ6NTAwMjkzNWYzZGRmNzNhM2NmN2JkNCIsImV4cCI6MTYzOTgwOTM2MywiZmlkIjoiYzhhX3V6NlpSdkN3Vlk3VzJHYktpTSIsInByb2plY3ROdW1iZXIiOjg2Nzc5NzczMjU0MX0.AB2LPV8wRQIgQK_WIUrNA7uySiaqeFY933w_7aoQjsFTsj8wGQYScAMCIQDMoTfCNAPUeAEWZfZAp4Wks1kZ9KYPKfVXOunFhu-z8A"
    #     message_title = "Title"
    #     message_body = "Hello"
    #     result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
    #
    #     print (result)
         


    
    

        
    
    
    
    
    
    
