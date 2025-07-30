
Glossary
========

.. glossary::
   :sorted:

   external customer
     A customer account from an external system.  Sideshow can be
     configured to lookup customer data from external system(s) when
     creating an :term:`order`.

     See also :term:`local customer` and :term:`pending customer`.

   external product
     A product record from an external system.  Sideshow can be
     configured to lookup customer data from external system(s) when
     creating an :term:`order`.

     See also :term:`local product` and :term:`pending product`.

   local customer
     A customer account in the :term:`app database`.  By default,
     Sideshow will use its native "Local Customers" table for lookup
     when creating an :term:`order`.

     The data model for this is
     :class:`~sideshow.db.model.customers.LocalCustomer`.

     See also :term:`external customer` and :term:`pending customer`.

   local product
     A product record in the :term:`app database`.  By default,
     Sideshow will use its native "Local Products" table for lookup
     when creating an :term:`order`.

     The data model for this is
     :class:`~sideshow.db.model.products.LocalProduct`.

     See also :term:`external product` and :term:`pending product`.

   new order batch
     When user is creating a new order, under the hood a :term:`batch`
     is employed to keep track of user input.  When user ultimately
     "submits" the order, the batch is executed which creates a true
     :term:`order`.

     The batch handler is responsible for business logic for the order
     creation step; the :term:`order handler` is responsible for
     everything thereafter.

     :class:`~sideshow.batch.neworder.NewOrderBatchHandler` is the
     default handler for this.

   order
     This is the central focus of the app; it refers to a customer
     case/special order which is tracked over time, from placement to
     fulfillment.  Each order may have one or more :term:`order items
     <order item>`.

   order handler
     The :term:`handler` responsible for business logic surrounding
     :term:`order` workflows *after* initial creation.  (Whereas the
     :term:`new order batch` handler is responsible for creation.)

     :class:`~sideshow.orders.OrderHandler` is the default handler for
     this.

   order item
     This is effectively a "line item" within an :term:`order`.  It
     represents a particular product, with quantity and pricing
     specific to the order.

     Each order item is tracked independently of its parent order and
     sibling items.

   pending customer
     A "temporary" customer record used when creating an :term:`order`
     for new/unknown customer.

     The data model for this is
     :class:`~sideshow.db.model.customers.PendingCustomer`.

     See also :term:`local customer` and :term:`external customer`.

   pending product
     A "temporary" product record used when creating an :term:`order`
     for new/unknown product.

     The data model for this is
     :class:`~sideshow.db.model.products.PendingProduct`.

     See also :term:`local product` and :term:`external product`.
