## Port

* Database backup
* How to port to new without trashing old files/database
* DO NOT START THE APP - before this is handled

## Functionality

* Save Recipes
    * Has N Ingredients Lists
    * Ingredients List
        * Scalable (for X people, hints "usually much"/"light snack")
        * Smart ->  Here: Ingredient + Amount (Number, Weight, Volume, 'Prise')
        * Instant add/create easy
    * Ingredients
        * Owner/Edit Right?/View Right
        * Know equal/similar ingredients
        * List categories or particular shops where to buy (maybe with preferences)
        * Replacements/'Generika'   "Sued Zucker"->"Zucker"
        * Supersets (Get any Zucker (Puderzucker oder brauner Zucker -> Egal)) -> Hierarchie
        * List recipes that contain
    * Owner/Rights Management
    * Clone/Variants -> "This is a variante of Recipe <Click>"
* Shops
    * Categories (Supermarkt/Asia-Laden/Baumarkt)
    * Kaufland -> Supermarkt
* Save Shopping Lists
    * Owner/View
    * Extract from Recipes + Scale
* Own Inventory
    * List ingredients that we currently have
    * Update this after cooking/shopping
    * Permanent Inventory Items (Wasser)
* Go Shopping
    * Activate Lists and Scale them
    * Extract Options from 'active lists' + Category
    * Select Shop and Compile List for this shop

## Use Cases

### Plan Dinner Party
1 Choose K recipes to make
1 Invite M people per K
1 Compile or define list selections of shops to go to
1 Select Shops to go to
1 Go Shopping at shop X -> has list of all to get in X

### Recipe vs. Stuff at home
1 Choose K * M recipes
1 Go Shopping
1 Only buy things that we dont have
1 Also consider partial: Have still 1/2 Joghurt

### Replacements vs. Specific
* Recipe 1 needs only butter
* Recipe 2 needs butter or "streichbelag"
    * Can replace with butter or margarine
* Generika Margarine would be bad for Recipe 1
* How to handle, especially when no nice name like "streichbelag"
    * Ingredient Lists can have multiple ingredients per entry (maybe with diffrent scales)

