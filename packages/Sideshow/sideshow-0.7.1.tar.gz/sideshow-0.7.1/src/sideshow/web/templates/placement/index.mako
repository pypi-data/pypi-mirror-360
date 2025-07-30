## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="render_grid_tag()">
  % if master.has_perm('process_placement'):
      ${grid.render_vue_tag(**{'@process-placement': "processPlacementInit"})}
  % else:
      ${grid.render_vue_tag()}
  % endif
</%def>

<%def name="page_content()">
  ${parent.page_content()}
  % if master.has_perm('process_placement'):

      <${b}-modal has-modal-card
                  % if request.use_oruga:
                      v-model:active="processPlacementShowDialog"
                  % else:
                      :active.sync="processPlacementShowDialog"
                  % endif
                  >
        <div class="modal-card">
          ${h.form(url(f'{route_prefix}.process_placement'), ref='processPlacementForm')}
          ${h.csrf_token(request)}
          ${h.hidden('item_uuids', **{':value': 'processPlacementUuids.join()'})}

          <header class="modal-card-head">
            <p class="modal-card-title">Process Placement</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              This will mark {{ processPlacementUuids.length }}
              item{{ processPlacementUuids.length > 1 ? 's' : '' }} as
              being "placed" on order from vendor.
            </p>
            <b-field horizontal label="Vendor"
                     :type="processPlacementVendor ? null : 'is-danger'">
              <b-input name="vendor_name"
                       v-model="processPlacementVendor"
                       ref="processPlacementVendor" />
            </b-field>
            <b-field horizontal label="PO Number">
              <b-input name="po_number"
                       v-model="processPlacementNumber" />
            </b-field>
            <b-field horizontal label="Note">
              <b-input name="note"
                       v-model="processPlacementNote"
                       type="textarea" />
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <b-button type="is-primary"
                      @click="processPlacementSubmit()"
                      :disabled="!processPlacementVendor || processPlacementSubmitting"
                      icon-pack="fas"
                      icon-left="save">
              {{ processPlacementSubmitting ? "Working, please wait..." : "Save" }}
            </b-button>
            <b-button @click="processPlacementShowDialog = false">
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
  % if master.has_perm('process_placement'):
      <script>

        ThisPageData.processPlacementShowDialog = false
        ThisPageData.processPlacementUuids = []
        ThisPageData.processPlacementVendor = null
        ThisPageData.processPlacementNumber = null
        ThisPageData.processPlacementNote = null
        ThisPageData.processPlacementSubmitting = false

        ThisPage.methods.processPlacementInit = function(items) {
            this.processPlacementUuids = items.map((item) => item.uuid)
            this.processPlacementVendor = null
            this.processPlacementNumber = null
            this.processPlacementNote = null
            this.processPlacementShowDialog = true
            this.$nextTick(() => {
                this.$refs.processPlacementVendor.focus()
            })
        }

        ThisPage.methods.processPlacementSubmit = function() {
            this.processPlacementSubmitting = true
            this.$refs.processPlacementForm.submit()
        }

      </script>
  % endif
</%def>
