import logging
from google.appengine.ext import ndb

#TODO Finally check that no client function here is without user_id
# and that it is always used in requests to db - we don't want to accidentally
# delete stuff for another user.

# combine both into one list?
#class ShoppingList(ndb.Model):
#    name = ndb.StringProperty()
#    owner = ndb.StringProperty()
#    items = ndb.ListProperty(ndb.Key)     # list of ShoppingItem keys

class ShoppingItem(ndb.Model):
    count = ndb.IntegerProperty()
    item_name = ndb.StringProperty()
    shopped = ndb.BooleanProperty()
    order = ndb.IntegerProperty()       # Custom user order index

    shop = ndb.StringProperty()
    list_name = ndb.StringProperty()
    user_id = ndb.StringProperty()        # Use user.user_id()

class ShoppingConfigPair(ndb.Model):
    shop = ndb.StringProperty()
    list_name = ndb.StringProperty()

class ShoppingConfig(ndb.Model):
    name = ndb.StringProperty()
    user_id = ndb.StringProperty()
    config_pairs = ndb.StructuredProperty(ShoppingConfigPair, repeated=True)

class ShoppingSettings(ndb.Model):
    display_by_shop_shops = ndb.BooleanProperty()
    display_by_shop_list_name = ndb.BooleanProperty()
    display_by_list_shops = ndb.BooleanProperty()
    display_by_list_list_name = ndb.BooleanProperty()
    display_custom_shops = ndb.BooleanProperty()
    display_custom_list_name = ndb.BooleanProperty()
    user_id = ndb.StringProperty()

#def shopping_list_key(group = "default"):
#    return ndb.Key.from_path("shopping_lists", group)

# For now always use all, maybe later make a hiearchy of keys - however that's correctly done.
def shopping_item_key(list_name = "all"):
    return ndb.Key("ShoppingList", list_name)

def shopping_config_key(sc_user = "all"):
    return ndb.Key("ShoppingConfig", sc_user)

def shopping_settings_key(sc_user = "all"):
    return ndb.Key("ShoppingSettings", sc_user)

def get_default_settings(user_id):
    settings = ShoppingSettings(user_id=user_id,
        display_by_shop_shops=False,
        display_by_shop_list_name=True,
        display_by_list_shops=True,
        display_by_list_list_name=False,
        display_custom_shops=True,
        display_custom_list_name=False,
        parent=shopping_settings_key())
    return settings

def get_user_settings(user_id):
    q = ShoppingSettings.query(
            ShoppingSettings.user_id == user_id,
            ancestor=shopping_settings_key())
    set_list = list(q)
    if not set_list:
        return None
    if len(set_list) != 1:
        logging.error("get_user_settings: For user %s - Unexpected settings length: %d" % (user_id, len(set_list)))

    return set_list[0]


def get_user_lists(user_id):
    q = ShoppingItem.query(
            ShoppingItem.user_id == user_id,
            ancestor=shopping_item_key(),
            projection=[ShoppingItem.list_name],
            distinct=True).order(ShoppingItem.list_name)
    return list(q)

def get_shops(user_id):
    q = ShoppingItem.query(
            ShoppingItem.user_id == user_id,
            ancestor=shopping_item_key(),
            projection=[ShoppingItem.shop],
            distinct=True).order(ShoppingItem.shop)
    return list([item.shop for item in q])

def get_list_items(user_id, list_name):
    q = ShoppingItem.query(
            ShoppingItem.user_id == user_id,
            ShoppingItem.list_name == list_name,
            ancestor=shopping_item_key(),
            ).order(ShoppingItem.order)
    return list(q)

def get_shop_items(user_id, shop_name):
    q = ShoppingItem.query(
            ShoppingItem.user_id == user_id,
            ShoppingItem.shop == shop_name,
            ancestor=shopping_item_key(),
            ).order(ShoppingItem.order)
    return list(q)

def item_matches(item1, item2):
    if item1.count != item2.count:
        return False
    if item1.item_name != item2.item_name:
        return False
    if item1.shop != item2.shop:
        return False
    if item1.list_name != item2.list_name:
        return False
    if item1.user_id != item2.user_id:
        return False

    # If shopped or order changes, it's still the same item.
    return True

def update_list_items(user_id, list_name, new_list_items):
    # Set list_name and user_id for the items
    for item in new_list_items:
        item.list_name = list_name
        item.user_id = user_id

    cur_list_items = get_list_items(user_id, list_name)
    # We now have a list of items currently stored
    # The result of this operation should be that this
    # will be equal to new_list_items
    # We don't want to delete everything and readd everything new
    # as that's quite inefficient, but rather update items

    add_items = []
    matching_items = []
    # For each new item determine if it's really new or an update
    for new_item in new_list_items:
        taken_idx = -1
        for ind, cur_item in enumerate(cur_list_items):
            if item_matches(new_item, cur_item):
                matching_items.append((cur_item, new_item))
                taken_idx = ind
                break
        if taken_idx >= 0:  # Found an update
            del cur_list_items[taken_idx]   # Remove to prevent double matches (can only update once)
        else:
            add_items.append(new_item)

    # cur_list_items now contains those items that we haven't match in new for an update.
    # Updateing must also remove any entries for this list that arent' in here any more.
    # This will auto-delete the list. Will need to see later if that's what we want.
    remove_item_keys = [item.key for item in cur_list_items]

    # Perform the update to the changed items
    # Update cur from new as cur is in the db
    # match states that everything matches, but those two properties that we update
    update_items = []
    for cur_it, new_it in matching_items:
        # Nothing changed, no update necessary
        if cur_it.order == new_it.order and cur_it.shopped == new_it.shopped:
            continue
        cur_it.order = new_it.order
        cur_it.shopped = new_it.shopped
        update_items.append(cur_it)

    logging.error("Adding %d" % len(add_items))
    logging.error("Updating %d" % len(update_items))
    logging.error("Deleting %d" % len(remove_item_keys))

    ndb.put_multi(add_items)
    ndb.put_multi(update_items)
    ndb.delete_multi(remove_item_keys)

def delete_list(user_id, list_name):
    q = ShoppingItem.query(
            ShoppingItem.user_id == user_id,
            ShoppingItem.list_name == list_name,
            ancestor=shopping_item_key(),
            )
    item_keys = [item.key for item in q]
    ndb.delete_multi(item_keys)

def update_shopped(user_id, new_item_shopped):
    # new_item_shopped is a dict: Key -> shopped for the new assignments

    # First get the matching items form db
    items = ndb.get_multi(new_item_shopped.keys())

    items_changed = []
    for item in items:
        if item.user_id != user_id:     # Someone might have spoofed the request to change other keys
            continue
        if item.shopped == new_item_shopped[item.key]:
            continue
        item.shopped = new_item_shopped[item.key]
        items_changed.append(item)
    ndb.put_multi(items_changed)


def get_shopping_config_pairs(user_id):
    q = ShoppingItem.query(
            ShoppingItem.user_id == user_id,
            ancestor=shopping_item_key(),
            )
    config_pairs = set()
    for item in q:
        config_pairs.add((item.list_name, item.shop))
    config_pairs = list(config_pairs)
    config_pairs.sort()

    shopping_config_pairs = []
    for cp in config_pairs:
        shopping_config_pairs.append(ShoppingConfigPair(list_name=cp[0], shop=cp[1]))

    return shopping_config_pairs

def get_shopping_config(user_id, config_name):
    q = ShoppingConfig.query(
            ShoppingConfig.user_id == user_id,
            ShoppingConfig.name == config_name,
            ancestor=shopping_config_key(),
            )
    sc_list = list(q)
    if not sc_list:
        return None
    if len(sc_list) != 1:
        logging.error("get_shopping_config: For user %s - Unexpected config length: %d" % (user_id, len(sc_list)))

    return sc_list[0]
 
def get_shopping_configs(user_id):
    q = ShoppingConfig.query(
            ShoppingConfig.user_id == user_id,
            ancestor=shopping_config_key(),
            ).order(ShoppingConfig.name)
    return list(q)

def update_shopping_config(user_id, config_name, selected_config_pairs):
    current_config = get_shopping_config(user_id, config_name)
    if not current_config:  # new
        current_config = ShoppingConfig(name=config_name, user_id=user_id,
                parent=shopping_config_key())
    current_config.config_pairs = selected_config_pairs
    keys = current_config.put()
    logging.error("added key %s" % keys)
    if not keys:
        logging.error("current_config.put() failed.")

def delete_config(user_id, config_name):
    q = ShoppingConfig.query(
            ShoppingConfig.user_id == user_id,
            ShoppingConfig.name == config_name,
            ancestor=shopping_config_key(),
            )
    conf_keys = [conf.key for conf in q]
    ndb.delete_multi(conf_keys)

def get_config_items(user_id, config):
    config_items = []
    for cp in config.config_pairs:
        q = ShoppingItem.query(
            ShoppingItem.user_id == user_id,
            ShoppingItem.list_name == cp.list_name,
            ShoppingItem.shop == cp.shop,
            ancestor=shopping_item_key(),
            ).order(ShoppingItem.order)
        for item in q:
            config_items.append(item)
    return config_items

def parse_shopping_config(configs_str):
    # Format: 1 entry per line, list_name$$$shop_name (optional)
    #XX$$$Aldi
    #XX$$$
    #X$$$
    config_str_l = configs_str.split('\n')
    config_pairs_str = [e.strip().split("$$$") for e in config_str_l if e.strip()]
    config_pairs = []
    for p in config_pairs_str:
        if not p or not p[0]:
            continue
        cp = ShoppingConfigPair(list_name=p[0])
        if len(p) > 1:
            cp.shop = p[1]
        config_pairs.append(cp)
    return config_pairs

#class ShoppingConfigPair(ndb.Model):
#    list_name = ndb.StringProperty()
#    shop = ndb.StringProperty()
#
#class ShoppingConfig(ndb.Model):
#    name = ndb.StringProperty()
#    user_id = ndb.StringProperty()
#    config_pairs = ndb.StructuredProperty(ShoppingConfigPair, repeated=True)


#class ShoppingItem(ndb.Model):
#    count = ndb.IntegerProperty()
#    item_name = ndb.StringProperty()
#    shop = ndb.StringProperty()
#    list_name = ndb.StringProperty()
#    user_id = ndb.StringProperty()        # Use user.user_id()
#
#    shopped = ndb.BooleanProperty()
#    order = ndb.IntegerProperty()       # Custom user order index


def format_item(list_item):
    item_str = ""
    if list_item.shopped:
        item_str += "X "
    if list_item.count > 1:
        item_str += "%d %s" % (list_item.count, list_item.item_name)
    else:
        item_str += list_item.item_name
    return item_str

# Format ShoppingItem list so it can be put into a text box
# Inverse of parsing
def format_items(list_items):
    list_items.sort(key=lambda item: item.order)
    out_list = []
    current_shop = None
    # handle "Shop:" appearing for each shop
    for item in list_items:
        if item.shop != current_shop:   # Add shop to out_list if it's changed
            if item.shop:
                out_list.append("")     # Empty line before new shop
                out_list.append("%s:" % item.shop)
            elif current_shop is not None:   # shop change to an item without a shop
                out_list.append("INVALID_SHOP:")    # only add this if current shop wasn't set
            current_shop = item.shop
        out_list.append(format_item(item))
    return "\n".join(out_list)

def parse_list(list_content):
    """ Parse a textual list into a list of ShoppingItems.
        Return the list, error_msg - where error_msg is empty if the parse was successfull
    """
    items = []
    error_msg = ""

    cur_shop = ""
    order_idx = 0
    for line in list_content.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.endswith(":"):
            cur_shop = line[:-1]
            if cur_shop == "INVALID_SHOP":
                cur_shop = ""
            continue
        # actual item, first might come a count:
        # 3 beers, 1x banana, tires
        # A starting X or x signals the item is shopped already, e.g.
        # X 3 beers, x 1x banana, X tires
        parts = line.split(" ")
        nextPart = 0

        shopped = False
        shopped_token = parts[nextPart]
        if shopped_token.lower() == "x":
            shopped = True
            nextPart += 1

        count_token = parts[nextPart]
        if count_token.endswith("x"):           # remove a trailing 'x' if there
            count_token = count_token[:-1]
        try:
            count = int(count_token)
            # if no except this was a valid count, otherwise it was actual item name content
            nextPart += 1
        except ValueError:
            count = 1

        item_name = " ".join(parts[nextPart:])

        item = ShoppingItem(count=count, item_name=item_name, shopped=shopped,
                shop=cur_shop, order=order_idx,
                parent = shopping_item_key())
        order_idx += 1
        items.append(item)
    return items, error_msg     # seems we don't have parse errors, yet

