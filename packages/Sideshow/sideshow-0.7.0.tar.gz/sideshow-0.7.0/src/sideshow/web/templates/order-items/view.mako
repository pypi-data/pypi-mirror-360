## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="content_title()">
  (${app.enum.ORDER_ITEM_STATUS[item.status_code]})
  ${instance_title}
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style>

    nav .field .field-label .label {
        white-space: nowrap;
        width: 10rem;
    }

  </style>
</%def>

<%def name="page_content()">
  <div style="padding: 2rem; display: flex; justify-content: space-evenly; gap: 2rem;">
    <div style="flex-grow: 1;">

      <nav class="panel" style="width: 100%;">
        <p class="panel-heading">Order Item</p>
        <div class="panel-block">
          <div style="width: 100%;">
            <b-field horizontal label="ID">
              <span>${h.link_to(f"Order ID {order.order_id}", url('orders.view', uuid=order.uuid))} &mdash; Item #${item.sequence}</span>
            </b-field>
            % if expose_store_id:
                <b-field horizontal label="Store">
                  <span>
                    % if order.store:
                        ${h.link_to(order.store.get_display(), url('stores.view', uuid=order.store.uuid))}
                    % elif order.store_id:
                        ${order.store_id}
                    % endif
                  </span>
                </b-field>
            % endif
            <b-field horizontal label="Order Qty">
              <span>${order_qty_uom_text|n}</span>
            </b-field>
            % if item.discount_percent:
                <b-field horizontal label="Discount">
                  <span>${app.render_percent(item.discount_percent)}</span>
                </b-field>
            % endif
            <b-field horizontal label="Total Due">
              <span>${app.render_currency(item.total_price)}</span>
            </b-field>
            <b-field horizontal label="Total Paid">
              <span>${app.render_currency(item.paid_amount)}</span>
            </b-field>
            <b-field horizontal label="Status">
              <div style="display: flex; gap: 1rem; align-items: center;">
                <span
                  % if item_status_variant:
                      class="has-background-${item_status_variant}"
                  % endif
                  % if master.has_perm('change_status'):
                      style="padding: 0.25rem;"
                  % endif
                  >
                  ${app.enum.ORDER_ITEM_STATUS[item.status_code]}
                </span>
                % if master.has_perm('change_status'):
                    <b-button type="is-primary"
                              icon-pack="fas"
                              icon-left="edit"
                              @click="changeStatusInit()">
                      Change Status
                    </b-button>
                    <${b}-modal
                      % if request.use_oruga:
                          v-model:active="changeStatusShowDialog"
                      % else:
                          :active.sync="changeStatusShowDialog"
                      % endif
                      >
                      <div class="card">
                        <div class="card-content">

                          <h4 class="block is-size-4">Change Item Status</h4>

                          <b-field horizontal label="Current Status">
                            <span>{{ changeStatusCodes[changeStatusOldCode] }}</span>
                          </b-field>

                          <br />

                          <b-field horizontal label="New Status"
                                   :type="changeStatusNewCode ? null : 'is-danger'">
                            <b-select v-model="changeStatusNewCode">
                              <option v-for="status in changeStatusCodeOptions"
                                      :key="status.key"
                                      :value="status.key">
                                {{ status.label }}
                              </option>
                            </b-select>
                          </b-field>

                          <b-field label="Note">
                            <b-input v-model="changeStatusNote"
                                     type="textarea" rows="4" />
                          </b-field>

                          <br />

                          <div class="buttons">
                            <b-button type="is-primary"
                                      :disabled="changeStatusSaveDisabled"
                                      icon-pack="fas"
                                      icon-left="save"
                                      @click="changeStatusSave()">
                              {{ changeStatusSubmitting ? "Working, please wait..." : "Update Status" }}
                            </b-button>
                            <b-button @click="changeStatusShowDialog = false">
                              Cancel
                            </b-button>
                          </div>

                        </div>
                      </div>
                    </${b}-modal>

                    ${h.form(master.get_action_url('change_status', item), ref='changeStatusForm')}
                    ${h.csrf_token(request)}
                    ${h.hidden('new_status', **{'v-model': 'changeStatusNewCode'})}
                    ## ${h.hidden('uuids', **{':value': 'changeStatusCheckedRows.map((row) => {return row.uuid}).join()'})}
                    ${h.hidden('note', **{':value': 'changeStatusNote'})}
                    ${h.end_form()}

                % endif
              </div>
            </b-field>
          </div>
        </div>
      </nav>

      <nav class="panel" style="width: 100%;">
        <p class="panel-heading">Pricing</p>
        <div class="panel-block">
          <div style="width: 100%;">
            <b-field horizontal label="Unit Cost">
              <span>${app.render_currency(item.unit_cost, scale=4)}</span>
            </b-field>
            <b-field horizontal label="Unit Price Reg.">
              <span>${app.render_currency(item.unit_price_reg)}</span>
            </b-field>
            <b-field horizontal label="Unit Price Sale">
              <span>${app.render_currency(item.unit_price_sale)}</span>
            </b-field>
            <b-field horizontal label="Sale Ends">
              <span>${app.render_datetime(item.sale_ends)}</span>
            </b-field>
            <b-field horizontal label="Unit Price Quoted">
              <span>${app.render_currency(item.unit_price_quoted)}</span>
            </b-field>
            <b-field horizontal label="Case Size">
              <span>${app.render_quantity(item.case_size)}</span>
            </b-field>
            <b-field horizontal label="Case Price Quoted">
              <span>${app.render_currency(item.case_price_quoted)}</span>
            </b-field>
          </div>
        </div>
      </nav>

    </div>
    <div style="flex-grow: 1;">

      <nav class="panel" style="width: 100%;">
        <p class="panel-heading">Customer</p>
        <div class="panel-block">
          <div style="width: 100%;">
            <b-field horizontal label="Customer ID">
              <span>${order.customer_id}</span>
            </b-field>
            % if not order.customer_id and order.local_customer:
                <b-field horizontal label="Local Customer">
                  <span>${h.link_to(order.local_customer, url('local_customers.view', uuid=order.local_customer.uuid))}</span>
                </b-field>
            % endif
            % if not order.customer_id and order.pending_customer:
                <b-field horizontal label="Pending Customer">
                  <span>${h.link_to(order.pending_customer, url('pending_customers.view', uuid=order.pending_customer.uuid))}</span>
                </b-field>
            % endif
            <b-field horizontal label="Customer Name">
              <span>${order.customer_name}</span>
            </b-field>
            <b-field horizontal label="Phone Number">
              <span>${order.phone_number}</span>
            </b-field>
            <b-field horizontal label="Email Address">
              <span>${order.email_address}</span>
            </b-field>
          </div>
        </div>
      </nav>

      <nav class="panel" style="width: 100%;">
        <p class="panel-heading">Product</p>
        <div class="panel-block">
          <div style="width: 100%;">
            <b-field horizontal label="Product ID">
              <span>${item.product_id or ''}</span>
            </b-field>
            % if not item.product_id and item.local_product:
                <b-field horizontal label="Local Product">
                  <span>${h.link_to(item.local_product, url('local_products.view', uuid=item.local_product.uuid))}</span>
                </b-field>
            % endif
            % if not item.product_id and item.pending_product:
                <b-field horizontal label="Pending Product">
                  <span>${h.link_to(item.pending_product, url('pending_products.view', uuid=item.pending_product.uuid))}</span>
                </b-field>
            % endif
            <b-field horizontal label="Scancode">
              <span>${item.product_scancode or ''}</span>
            </b-field>
            <b-field horizontal label="Brand">
              <span>${item.product_brand or ''}</span>
            </b-field>
            <b-field horizontal label="Description">
              <span>${item.product_description or ''}</span>
            </b-field>
            <b-field horizontal label="Size">
              <span>${item.product_size or ''}</span>
            </b-field>
            <b-field horizontal label="Sold by Weight">
              <span>${app.render_boolean(item.product_weighed)}</span>
            </b-field>
            <b-field horizontal label="Department ID">
              <span>${item.department_id or ''}</span>
            </b-field>
            <b-field horizontal label="Department Name">
              <span>${item.department_name or ''}</span>
            </b-field>
            <b-field horizontal label="Special Order">
              <span>${app.render_boolean(item.special_order)}</span>
            </b-field>
            <b-field horizontal label="Vendor Name">
              <span>${item.vendor_name or ''}</span>
            </b-field>
            <b-field horizontal label="Vendor Item Code">
              <span>${item.vendor_item_code or ''}</span>
            </b-field>
          </div>
        </div>
      </nav>

    </div>
  </div>

  <div style="padding: 0 2rem;">
    <nav class="panel" style="width: 100%;">
      <p class="panel-heading"
         % if master.has_perm('add_note'):
             style="display: flex; gap: 2rem; align-items: center;"
         % endif
         >
        <span>Events</span>
        % if master.has_perm('add_note'):
            <b-button type="is-primary"
                      icon-pack="fas"
                      icon-left="plus"
                      @click="addNoteInit()">
              Add Note
            </b-button>
            <${b}-modal has-modal-card
                        % if request.use_oruga:
                            v-model:active="addNoteShowDialog"
                        % else:
                            :active.sync="addNoteShowDialog"
                        % endif
                        >
              <div class="modal-card">

                <header class="modal-card-head">
                  <p class="modal-card-title">Add Note</p>
                </header>

                <section class="modal-card-body">
                  <b-field>
                    <b-input type="textarea" rows="8"
                             v-model="addNoteText"
                             ref="addNoteText"
                             expanded />
                  </b-field>
##                   <b-field>
##                     <b-checkbox v-model="addNoteApplyAll">
##                       Apply to all products on this order
##                     </b-checkbox>
##                   </b-field>
                </section>

                <footer class="modal-card-foot">
                  <b-button type="is-primary"
                            @click="addNoteSave()"
                            :disabled="addNoteSaveDisabled"
                            icon-pack="fas"
                            icon-left="save">
                    {{ addNoteSubmitting ? "Working, please wait..." : "Add Note" }}
                  </b-button>
                  <b-button @click="addNoteShowDialog = false">
                    Cancel
                  </b-button>
                </footer>
              </div>
            </${b}-modal>

            ${h.form(master.get_action_url('add_note', item), ref='addNoteForm')}
            ${h.csrf_token(request)}
            ${h.hidden('note', **{':value': 'addNoteText'})}
            ## ${h.hidden('uuids', **{':value': 'changeStatusCheckedRows.map((row) => {return row.uuid}).join()'})}
            ${h.end_form()}

        % endif

      </p>
      <div class="panel-block">
        <div style="width: 100%;">
          ${events_grid.render_table_element()}
        </div>
      </div>
    </nav>
  </div>

</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  ${events_grid.render_vue_template()}
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    % if master.has_perm('add_note'):

        ThisPageData.addNoteShowDialog = false
        ThisPageData.addNoteText = null
        ## ThisPageData.addNoteApplyAll = false
        ThisPageData.addNoteSubmitting = false

        ThisPage.computed.addNoteSaveDisabled = function() {
            if (!this.addNoteText) {
                return true
            }
            if (this.addNoteSubmitting) {
                return true
            }
            return false
        }

        ThisPage.methods.addNoteInit = function() {
            this.addNoteText = null
            ## this.addNoteApplyAll = false
            this.addNoteShowDialog = true
            this.$nextTick(() => {
                this.$refs.addNoteText.focus()
            })
        }

        ThisPage.methods.addNoteSave = function() {
            this.addNoteSubmitting = true
            this.$refs.addNoteForm.submit()
        }

    % endif

    % if master.has_perm('change_status'):

        ThisPageData.changeStatusCodes = ${json.dumps(app.enum.ORDER_ITEM_STATUS)|n}
        ThisPageData.changeStatusCodeOptions = ${json.dumps([dict(key=k, label=v) for k, v in app.enum.ORDER_ITEM_STATUS.items()])|n}

        ThisPageData.changeStatusShowDialog = false
        ThisPageData.changeStatusOldCode = ${instance.status_code}
        ThisPageData.changeStatusNewCode = null
        ThisPageData.changeStatusNote = null
        ThisPageData.changeStatusSubmitting = false

        ThisPage.computed.changeStatusSaveDisabled = function() {
            if (!this.changeStatusNewCode) {
                return true
            }
            if (this.changeStatusSubmitting) {
                return true
            }
            return false
        }

        ThisPage.methods.changeStatusInit = function() {
            this.changeStatusNewCode = null
            // clear out any checked rows
            // this.changeStatusCheckedRows.length = 0
            this.changeStatusNote = null
            this.changeStatusShowDialog = true
        }

        ThisPage.methods.changeStatusSave = function() {
            if (this.changeStatusNewCode == this.changeStatusOldCode) {
                alert("You chose the same status it already had...")
                return
            }

            this.changeStatusSubmitting = true
            this.$refs.changeStatusForm.submit()
        }

    % endif

    ## TODO: ugh the hackiness
    ThisPageData.gridContext = {
        % for key, data in form.grid_vue_context.items():
            '${key}': ${json.dumps(data)|n},
        % endfor
    }

  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  ${events_grid.render_vue_finalize()}
</%def>
