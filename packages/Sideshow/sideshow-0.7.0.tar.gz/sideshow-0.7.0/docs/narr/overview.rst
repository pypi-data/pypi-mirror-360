
==========
 Overview
==========

Here we'll give the high-level view of what Sideshow is/does.


Intended Use Case
-----------------

Sideshow is designed with "brick and mortar" retailers in mind.  They
normally sell product "in person" using POS software.

Some retailers allow customers to "place an order" for product which
is not currently in stock.  The retailer will then place an order with
their vendor, and ultimately the customer will pay for and receive the
product.  Depending on the retailer's business rules, customer may
need to pay for the product up-front, or else at time of pickup.
They may also receive a discount when ordering by the case etc.

Sideshow provides a common system to track such "case / special orders"
- which are just called "orders" in Sideshow.  It runs as a web app,
(normally) on the internal network, where staff can access it from any
machine.


Workflow
--------

Staff must first create the :term:`order` in Sideshow.  They identify
the customer / contact info, and add item(s) with desired quantity.

Depending on config, staff may be able to create orders for customer
and/or products which do not yet exist in the system.

From there, dedicated workflow pages may be used for various steps:

* Placement - staff indicates item(s) are on order from vendor
* Receiving - staff indicates item(s) arrived from vendor
* Contact - staff indicates customer has been notified
* Delivery - staff indicates customer has picked up item(s)

Each :term:`order item` has a status indicating where it is in the
workflow.  Staff can manually override the status if needed, when
unexpected situations arise.


Customer + Product Data
-----------------------

By default, Sideshow stores "local" :term:`customers <local customer>`
and :term:`products <local product>` in its :term:`app database`.

Whenever an order is created for new/unknown customer and/or product,
records are added to the local customer/product tables as needed.
From then on those records are available for lookup when creating new
orders.

However in many cases it's better to query the POS DB for
customer/product data.  That way the lookup "just works" from the
staff perspective, and there is no need to store those in Sideshow.

The latter case is referred to as "external" :term:`customers
<external customer>` and :term:`products <external product>`.  Some
POS systems are already supported for this:

* CORE-POS via `Sideshow-COREPOS
  <https://forgejo.wuttaproject.org/wutta/sideshow-corepos>`_
* ECRS Catapult via `Sideshow-Catapult
  <https://forgejo.wuttaproject.org/wutta/sideshow-catapult>`_
  (nb. access restricted)
* LOC SMS via `Sideshow-LOCSMS
  <https://forgejo.wuttaproject.org/wutta/sideshow-locsms>`_
  (nb. access restricted)
