## v0.7.1 (2025-07-06)

### Fix

- cap sqlalchemy version to 1.x

## v0.7.0 (2025-07-06)

### Feat

- add basic support to "resolve" a pending product

### Fix

- allow config injection for sake of tests
- bump version requirement for wuttaweb

## v0.6.0 (2025-02-20)

### Feat

- allow re-order past product for new orders
- add per-department default item discount
- add config option to show/hide Store ID; default value
- add basic model, views for Stores

### Fix

- fix customer rendering in OrderItem grids; add sort/filter
- track vendor name/SKU per OrderItem
- require store for new orders, if so configured
- move Pricing config to separate section, for orders/configure

## v0.5.0 (2025-01-26)

### Feat

- add pkg extras for postgres, mysql; update install doc
- allow basic support for item discounts

### Fix

- add setup hook to auto-create Order Admin role
- bugfix for view order item page template

## v0.4.0 (2025-01-23)

### Feat

- add initial workflow master views, UI features
- add tools to change order item status; add notes
- add initial support for order item events

### Fix

- customize "view order item" page w/ panels
- add loading overlay for expensive calls in orders/create
- hide local customer when not applicable, for order view

## v0.3.0 (2025-01-13)

### Feat

- move lookup logic to handler; improve support for external lookup

### Fix

- expose new order batch handler choice in orders/configure
- add "Other" menu, for e.g. integration system links
- bugfix when new order with no pending customer

## v0.2.0 (2025-01-09)

### Feat

- add basic support for local customer, product lookups

### Fix

- expose config for new order w/ pending product

## v0.1.0 (2025-01-06)

### Feat

- add basic "create order" feature, docs, tests

### Fix

- add static libcache files for vue2 + buefy
