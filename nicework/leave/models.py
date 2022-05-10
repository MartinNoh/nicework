from django.db import models
from common.models import MyUser
from django.core.validators import RegexValidator
import datetime
# Create your models here.


class Annleave(models.Model): # 발생한 연차
    employee = models.ForeignKey(MyUser, on_delete=models.CASCADE) # 로그인한 계정
    reason = models.TextField(max_length=500)
    days = models.FloatField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} : {1}일, 사유 :{2}".format(self.employee.realname, self.days, self.reason)


class Rwdleave(models.Model): # 발생한 포상휴가
    employee = models.ForeignKey(MyUser, on_delete=models.CASCADE) # 로그인한 계정
    reason = models.TextField(max_length=500)
    days = models.FloatField(default=1)
    granter = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} : {1}일, 사유 :{2}".format(self.employee.realname, self.days, self.reason)


class LeavePaid(models.Model): # 비용지급으로 대체된 휴가
    employee = models.ForeignKey(MyUser, on_delete=models.CASCADE) # 로그인한 계정
    reason = models.TextField(max_length=500)
    days = models.FloatField(default=1)
    cost = models.IntegerField(default=0)
    granter = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} : {1}일, 사유 :{2}".format(self.employee.realname, self.days, self.reason)


class UserLeave(models.Model): # 사용자 남은 휴가
    employee = models.ForeignKey(MyUser, on_delete=models.CASCADE) # 로그인한 계정
    acm_overtime = models.FloatField(default=0) # 총 연장근로시간
    acm_annleave = models.FloatField(default=0) # 총 연차
    acm_rwdleave = models.FloatField(default=0) # 총 포상
    used = models.FloatField(default=0) # 사용한 휴가일수
    paid = models.FloatField(default=0) # 비용지급된 휴가일수
    remained = models.FloatField(default=0) # 잔여 휴가일수
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} : 잔여 {1}일".format(self.employee.realname, self.leftleave)


class Leave(models.Model): # 신청된 휴가
    employee = models.ForeignKey(MyUser, on_delete=models.CASCADE) # 로그인한 계정
    reason = models.TextField(max_length=1000) # 휴가 사유
    startdate = models. DateField() # 휴가 시작일시
    enddate = models. DateField() # 휴가 종료일자
    starttime = models.TimeField() # 휴가 시작시간
    endtime = models.TimeField() # 휴가 종료시간
    leaveterm = models.FloatField(default=0) # 휴가 기간
    LEAVECAT_CHOICES = (('AL', '연차'), ('MO', '오전 반차'), ('AO', '오후 반차')
        , ('CV', '경조 휴가'), ('OL', '공가'), ('EL', '조퇴'), ('AB', '결근'), ('SL', '병가'))
    leavecat = models.CharField(max_length=2, choices=LEAVECAT_CHOICES, default='AL') # 휴가 시간구분
    phoneNumberRegex = RegexValidator(regex = r"^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$")
    emgnum = models.CharField(validators = [phoneNumberRegex], max_length=15,) # 비상 연락처
    is_approved = models.BooleanField(default=False) # 매니저 승인여부
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} : {1} ~ {2} ({3}일, {4}) [{5}]".format(self.employee.realname, self.startdate, self.enddate, self.leaveterm, self.leavecat, self.is_approved)
