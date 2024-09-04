# from allauth.socialaccount.models import SocialAccount
# from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# @receiver(post_save, sender=SocialAccount)
# def save_user_profile(sender, instance, **kwargs):
#     if instance.provider == 'kakao':
#         user = instance.user
#         profile_data = instance.extra_data.get('properties', {})
#         user.first_name = profile_data.get('nickname', '')
#         user.save()