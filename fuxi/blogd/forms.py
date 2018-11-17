from django import forms
from django.core.mail import send_mail
# django 使用两个类 来创建表单
# forms.From用来生成标准的表单
# forms.ModelForm 用于从模型中生成表单
from blogd.models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name','email','body')
        # exclude 属性指定需要排除的字段
        # exclude = ('created')

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,widget=forms.Textarea)

