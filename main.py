#!/usr/bin/env python

import os
import logging
import webapp2
from base_handlers import Handler
import page_handlers
import shopping_handlers

DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Development')

app = webapp2.WSGIApplication([
#    ('/.json',                  page_handlers.MainJsonHandler),
    ('/',                       page_handlers.MainHandler),
    ('/shopping/by_list',       shopping_handlers.ShoppingByListHandler),
    ('/shopping/by_list/(.*)',  shopping_handlers.ShopByListHandler),
    ('/shopping/by_shop',       shopping_handlers.ShoppingByShopHandler),
    ('/shopping/by_shop/(.*)',  shopping_handlers.ShopByShopHandler),
    ('/shopping/custom',        shopping_handlers.ShoppingCustomHandler),
    ('/shopping/custom/edit_config',    shopping_handlers.EditConfigHandler),
    ('/shopping/custom/delete_config',  shopping_handlers.DeleteConfigHandler),
    ('/shopping/custom/view/(.*)',      shopping_handlers.ShopCustomHandler),
    ('/manage_lists',           page_handlers.ManageHandler),
    ('/manage_lists/edit_list',  page_handlers.EditListHandler),
    ('/manage_lists/edit_shopped',  page_handlers.EditShoppedHandler),
    ('/manage_lists/delete_list',  page_handlers.DeleteListHandler),
    ('/settings',               page_handlers.SettingsHandler),
    ('/welcome',                page_handlers.WelcomeHandler),
    ], debug=DEBUG)

