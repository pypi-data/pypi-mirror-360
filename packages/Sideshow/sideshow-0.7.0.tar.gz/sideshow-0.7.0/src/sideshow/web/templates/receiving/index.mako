## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="render_grid_tag()">
  % if master.has_perm('process_receiving') and master.has_perm('process_reorder'):
      ${grid.render_vue_tag(**{'@process-receiving': "processReceivingInit", '@process-reorder': "processReorderInit"})}
  % elif master.has_perm('process_receiving'):
      ${grid.render_vue_tag(**{'@process-receiving': "processReceivingInit"})}
  % elif master.has_perm('process_reorder'):
      ${grid.render_vue_tag(**{'@process-reorder': "processReorderInit"})}
  % else:
      ${grid.render_vue_tag()}
  % endif
</%def>

<%def name="page_content()">
  ${parent.page_content()}

  % if master.has_perm('process_receiving'):

      <${b}-modal has-modal-card
                  % if request.use_oruga:
                      v-model:active="processReceivingShowDialog"
                  % else:
                      :active.sync="processReceivingShowDialog"
                  % endif
                  >
        <div class="modal-card">
          ${h.form(url(f'{route_prefix}.process_receiving'), ref='processReceivingForm')}
          ${h.csrf_token(request)}
          ${h.hidden('item_uuids', **{':value': 'processReceivingUuids.join()'})}

          <header class="modal-card-head">
            <p class="modal-card-title">Process Receiving</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              This will mark {{ processReceivingUuids.length }}
              item{{ processReceivingUuids.length > 1 ? 's' : '' }}
              as being "received" from vendor.
            </p>
            <b-field horizontal label="Vendor"
                     :type="processReceivingVendor ? null : 'is-danger'">
              <b-input name="vendor_name"
                       v-model="processReceivingVendor"
                       ref="processReceivingVendor" />
            </b-field>
            <b-field horizontal label="Invoice Number">
              <b-input name="invoice_number"
                       v-model="processReceivingInvoiceNumber" />
            </b-field>
            <b-field horizontal label="PO Number">
              <b-input name="po_number"
                       v-model="processReceivingPoNumber" />
            </b-field>
            <b-field horizontal label="Note">
              <b-input name="note"
                       v-model="processReceivingNote"
                       type="textarea" />
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <b-button type="is-primary"
                      @click="processReceivingSubmit()"
                      :disabled="!processReceivingVendor || processReceivingSubmitting"
                      icon-pack="fas"
                      icon-left="save">
              {{ processReceivingSubmitting ? "Working, please wait..." : "Save" }}
            </b-button>
            <b-button @click="processReceivingShowDialog = false">
              Cancel
            </b-button>
          </footer>

          ${h.end_form()}
        </div>
      </${b}-modal>

  % endif

  % if master.has_perm('process_reorder'):

      <${b}-modal has-modal-card
                  % if request.use_oruga:
                      v-model:active="processReorderShowDialog"
                  % else:
                      :active.sync="processReorderShowDialog"
                  % endif
                  >
        <div class="modal-card">
          ${h.form(url(f'{route_prefix}.process_reorder'), ref='processReorderForm')}
          ${h.csrf_token(request)}
          ${h.hidden('item_uuids', **{':value': 'processReorderUuids.join()'})}

          <header class="modal-card-head">
            <p class="modal-card-title">Process Re-Order</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              This will mark {{ processReorderUuids.length }}
              item{{ processReorderUuids.length > 1 ? 's' : '' }}
              as being "ready" for placement (again).
            </p>
            <b-field horizontal label="Note">
              <b-input name="note"
                       v-model="processReorderNote"
                       ref="processReorderNote"
                       type="textarea" />
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <b-button type="is-primary"
                      @click="processReorderSubmit()"
                      :disabled="processReorderSubmitting"
                      icon-pack="fas"
                      icon-left="save">
              {{ processReorderSubmitting ? "Working, please wait..." : "Save" }}
            </b-button>
            <b-button @click="processReorderShowDialog = false">
              Cancel
            </b-button>
          </footer>

          ${h.end_form()}
        </div>
      </${b}-modal>

  % endif
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    % if master.has_perm('process_receiving'):

        ThisPageData.processReceivingShowDialog = false
        ThisPageData.processReceivingUuids = []
        ThisPageData.processReceivingVendor = null
        ThisPageData.processReceivingInvoiceNumber = null
        ThisPageData.processReceivingPoNumber = null
        ThisPageData.processReceivingNote = null
        ThisPageData.processReceivingSubmitting = false

        ThisPage.methods.processReceivingInit = function(items) {
            this.processReceivingUuids = items.map((item) => item.uuid)
            this.processReceivingVendor = null
            this.processReceivingInvoiceNumber = null
            this.processReceivingPoNumber = null
            this.processReceivingNote = null
            this.processReceivingShowDialog = true
            this.$nextTick(() => {
                this.$refs.processReceivingVendor.focus()
            })
        }

        ThisPage.methods.processReceivingSubmit = function() {
            this.processReceivingSubmitting = true
            this.$refs.processReceivingForm.submit()
        }

    % endif

    % if master.has_perm('process_reorder'):

        ThisPageData.processReorderShowDialog = false
        ThisPageData.processReorderUuids = []
        ThisPageData.processReorderNote = null
        ThisPageData.processReorderSubmitting = false

        ThisPage.methods.processReorderInit = function(items) {
            this.processReorderUuids = items.map((item) => item.uuid)
            this.processReorderNote = null
            this.processReorderShowDialog = true
            this.$nextTick(() => {
                this.$refs.processReorderNote.focus()
            })
        }

        ThisPage.methods.processReorderSubmit = function() {
            this.processReorderSubmitting = true
            this.$refs.processReorderForm.submit()
        }

    % endif

  </script>
</%def>
