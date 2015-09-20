#
# Trac login backend
# by Bruno Cabral 2013
#
#


from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import connection

import logging

logger = logging.getLogger(__name__)

class CookieMiddleware( object ):

    def get_trac_user(self, token):
        logger.error('Will get the trac user') # will print a message to the console
        cursor = connection.cursor()
        cursor.execute("SELECT name"
                   " FROM auth_cookie"
                   " WHERE cookie='%s'" % token)
        return cursor.fetchone()[0]
        
    def process_request(self, request):
        #if not hasattr(request, 'user'):
        #    raise ImproperlyConfigured() 
        if "trac_auth" not in request.COOKIES:
            return 
        token= request.COOKIES["trac_auth"]
        # REST request to OpenAM server for user attributes.
        #token, attribute, role = identity_manager.get_attributes( token )
        username = self.get_trac_user(token)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Create a new user. Note that we can set password
            # to anything, because it won't be checked; the password
            # from settings.py will.
            user = User(username=username, password='')
            user.is_staff = True
            user.is_superuser = True
            user.save()
        user.backend = 'noop'
        request.user = user
        login(request, user)
        
