#!/usr/bin/env python

import logging
import webapp2
from base_handlers import Handler
import shopping_lists
import urllib

class ShoppingByListHandler(Handler):
    def get(self):
        lists = shopping_lists.get_user_lists(self.user.user_id())
        self.render("shop_by_list.html", lists=lists)

class ShopByListHandler(Handler):
    def get(self, list_name):
        if not list_name:
            self.error(404)
            return

        list_name = list_name.decode("utf-8")
        list_items = shopping_lists.get_list_items(self.user.user_id(), list_name)
        if not list_items:
            self.error(404)
            return

        settings = shopping_lists.get_user_settings(self.user.user_id())
        if not settings:
            settings = shopping_lists.get_default_settings(self.user.user_id())

        display_shop = "inline" if settings.display_by_list_shops else "none"
        display_list = "inline" if settings.display_by_list_list_name else "none"
        self.render("grocery-list.html", list_title=list_name, list_items=list_items,
            add_edit_link=True, add_edit_config_link=False,
            display_shop=display_shop, display_list=display_list)

class ShoppingByShopHandler(Handler):
    def get(self):
        shops = shopping_lists.get_shops(self.user.user_id())
        self.render("shop_by_shop.html", shops=shops)

class ShopByShopHandler(Handler):
    def get(self, shop_name):
        if not shop_name:
            self.error(404)
            return

        shop_name = shop_name.decode("utf-8")
        shop_items = shopping_lists.get_shop_items(self.user.user_id(), shop_name)
        if not shop_items:
            # Can never happen?
            self.error(404)
            return

        settings = shopping_lists.get_user_settings(self.user.user_id())
        if not settings:
            settings = shopping_lists.get_default_settings(self.user.user_id())

        display_shop = "inline" if settings.display_by_shop_shops else "none"
        display_list = "inline" if settings.display_by_shop_list_name else "none"
        self.render("grocery-list.html", list_title=shop_name, list_items=shop_items,
            add_edit_link=False, add_edit_config_link=False,
            display_shop=display_shop, display_list=display_list)

class ShoppingCustomHandler(Handler):
    def get(self):
        configs = shopping_lists.get_shopping_configs(self.user.user_id())
        self.render("shop_custom.html", configs=configs)

class EditConfigHandler(Handler):
    def get(self):
        config_name = self.request.get('config_name')
        all_config_pairs = shopping_lists.get_shopping_config_pairs(self.user.user_id())
        if not config_name:   # no info: New list, render with no info
            self.render("edit_config.html", available_config_pairs=all_config_pairs)
            return

        config = shopping_lists.get_shopping_config(self.user.user_id(), config_name)
        if not config:
            self.error(404)
            return

        selected_config_pairs = config.config_pairs
        available_config_pairs = self.get_config_pairs_difference(
                all_config_pairs, selected_config_pairs)

        self.render("edit_config.html", config_name=config_name,
                available_config_pairs=available_config_pairs,
                selected_config_pairs=selected_config_pairs)

    def post(self):
        config_name = self.request.get('config_name')
        selected_configs_str = self.request.get('selected_configs')
        logging.error(selected_configs_str)

        selected_config_pairs = shopping_lists.parse_shopping_config(selected_configs_str)
        logging.error(selected_config_pairs)

        all_config_pairs = shopping_lists.get_shopping_config_pairs(self.user.user_id())
        available_config_pairs = self.get_config_pairs_difference(
                all_config_pairs, selected_config_pairs)

        if not config_name:
            self.render("edit_config.html", config_name=config_name,
                    available_config_pairs=available_config_pairs,
                    selected_config_pairs=selected_config_pairs,
                    name_error="Config name was empty!")
            return

        shopping_lists.update_shopping_config(self.user.user_id(), config_name, selected_config_pairs)

        # redirect to the get() request with this config_name
        # so user sees what was changed
        target_params = {'config_name' : config_name.encode("utf-8")}
        go_shopping = bool(self.request.get('save_and_shopping'))   # did we use that button? TODO js
        if go_shopping:
            self.redirect("/shopping/custom/view/" + urllib.quote(config_name.encode("utf-8")))
        else:
            self.redirect("/shopping/custom/edit_config?" + urllib.urlencode(target_params))


    def get_config_pairs_difference(self, all_pairs, selected_pairs):
        available_config_pairs = []
        for cp in all_pairs:
            # if it's not selected it's available
            selected = False
            for scp in selected_pairs:
                if scp.list_name == cp.list_name and scp.shop == cp.shop:
                    selected = True
                    break
            if not selected:
                available_config_pairs.append(cp)
        return available_config_pairs

class DeleteConfigHandler(Handler):
    def post(self):
        config_name = self.request.get('config_name')
        if not config_name:
            # Error, this shouldn't happen, we constructed that request,
            # unless someone spoofed the request
            self.error(412)
            return

        shopping_lists.delete_config(self.user.user_id(), config_name)

        # Finally redirect as the config edit doesn't apply any more.
        self.redirect("/shopping/custom")

class ShopCustomHandler(Handler):
    def get(self, config_name):
        if not config_name:
            self.error(404)
            return

        config_name = config_name.decode("utf-8")
        config = shopping_lists.get_shopping_config(self.user.user_id(), config_name)
        if not config:
            self.error(404)
            return

        settings = shopping_lists.get_user_settings(self.user.user_id())
        if not settings:
            settings = shopping_lists.get_default_settings(self.user.user_id())

        display_shop = "inline" if settings.display_custom_shops else "none"
        display_list = "inline" if settings.display_custom_list_name else "none"

        config_items = shopping_lists.get_config_items(self.user.user_id(), config)
        self.render("grocery-list.html", list_title=config_name, list_items=config_items,
            add_edit_link=False, add_edit_config_link=True,
            display_shop=display_shop, display_list=display_list)

