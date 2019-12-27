#!/usr/bin/env python

import logging
import webapp2
from base_handlers import Handler
import shopping_lists
import urllib
from google.appengine.ext import ndb

class MainHandler(Handler):
    def get(self):
        lists = shopping_lists.get_user_lists(self.user.user_id())
        shops = shopping_lists.get_shops(self.user.user_id())
        configs = shopping_lists.get_shopping_configs(self.user.user_id())
        self.render("main.html", lists=lists, shops=shops, configs=configs)

class WelcomeHandler(Handler):
    def get(self):
        self.render("welcome.html")

class ManageHandler(Handler):
    def get(self):
        lists = shopping_lists.get_user_lists(self.user.user_id())
        self.render("manage.html", lists=lists)

class EditListHandler(Handler):
    def get(self):
        list_name = self.request.get('list_name')
        if not list_name:   # no info: New list, render with no info
            self.render("edit_list.html")
            return

        list_items = shopping_lists.get_list_items(self.user.user_id(), list_name)
        self.render("edit_list.html", list_name=list_name,
                list_content=shopping_lists.format_items(list_items))

    def post(self):
        list_name = self.request.get('list_name')
        list_content = self.request.get('shoppinglist')
        go_shopping = bool(self.request.get('save_and_shopping'))   # did we use that button?
        if not list_name:
            self.render("edit_list.html", list_name=list_name, list_content=list_content,
                    name_error="List name was empty! Lists must have a name.")
            return

        shopping_list_items, error_msg = shopping_lists.parse_list(list_content)
        if error_msg:
            self.render("edit_list.html", list_name=list_name, list_content=list_content,
                    content_error=error_msg)
            return

        shopping_lists.update_list_items(self.user.user_id(), list_name, shopping_list_items)

        # redirect to the get() request with this list_name
        # so user sees what was added
        target_params = {'list_name' : list_name.encode("utf-8")}
        if go_shopping:
            self.redirect("/shopping/by_list/" + urllib.quote(list_name.encode("utf-8")))
        else:
            self.redirect("/manage_lists/edit_list?" + urllib.urlencode(target_params))

class EditShoppedHandler(Handler):
    def post(self):
        item_shopped = {}
        for k,v in self.request.POST.items():
            if k.startswith("Key"):
                k = k[3:]
                if v == "0":
                    shopped = False
                elif v == "1":
                    shopped = True
                else:
                    self.error(412)
                    return
                key = ndb.Key(urlsafe=k)
                item_shopped[key] = shopped

        shopping_lists.update_shopped(self.user.user_id(), item_shopped)

class DeleteListHandler(Handler):
    def post(self):
        list_name = self.request.get('list_name')
        if not list_name:
            # Error, this shouldn't happen, we constructed that request,
            # unless someone spoofed the request
            self.error(412)
            return

        # Try to delete - if no items deleted also error?
        shopping_lists.delete_list(self.user.user_id(), list_name)

        # Finally redirect to manage as the list edit doesn't apply any more.
        self.redirect("/manage_lists")


class SettingsHandler(Handler):
    def get(self):
        settings = shopping_lists.get_user_settings(self.user.user_id())
        if not settings:
            settings = shopping_lists.get_default_settings(self.user.user_id())

        self.render("settings.html", settings=settings)

    def post(self):
        settings = shopping_lists.get_user_settings(self.user.user_id())
        if not settings:
            settings = shopping_lists.get_default_settings(self.user.user_id())

        settings.display_by_shop_shops = self.request.get('display_by_shop_shops') == "on"
        settings.display_by_shop_list_name = self.request.get('display_by_shop_list_name') == "on"
        settings.display_by_list_shops = self.request.get('display_by_list_shops') == "on"
        settings.display_by_list_list_name = self.request.get('display_by_list_list_name') == "on"
        settings.display_custom_shops = self.request.get('display_custom_shops') == "on"
        settings.display_custom_list_name = self.request.get('display_custom_list_name') == "on"
        settings.put()

        settings = shopping_lists.get_user_settings(self.user.user_id())
        self.render("settings.html", settings=settings)

