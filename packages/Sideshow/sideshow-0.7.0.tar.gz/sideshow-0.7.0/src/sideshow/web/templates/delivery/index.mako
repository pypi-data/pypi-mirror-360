## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="render_grid_tag()">
  % if master.has_perm('process_delivery') and master.has_perm('process_restock'):
      ${grid.render_vue_tag(**{'@process-delivery': "processDeliveryInit", '@process-restock': "processRestockInit"})}
  % elif master.has_perm('process_delivery'):
      ${grid.render_vue_tag(**{'@process-delivery': "processDeliveryInit"})}
  % elif master.has_perm('process_restock'):
      ${grid.render_vue_tag(**{'@process-restock': "processRestockInit"})}
  % else:
      ${grid.render_vue_tag()}
  % endif
</%def>

<%def name="page_content()">
  ${parent.page_content()}

  % if master.has_perm('process_delivery'):

      <${b}-modal has-modal-card
                  % if request.use_oruga:
                      v-model:active="processDeliveryShowDialog"
                  % else:
                      :active.sync="processDeliveryShowDialog"
                  % endif
                  >
        <div class="modal-card">
          ${h.form(url(f'{route_prefix}.process_delivery'), ref='processDeliveryForm')}
          ${h.csrf_token(request)}
          ${h.hidden('item_uuids', **{':value': 'processDeliveryUuids.join()'})}

          <header class="modal-card-head">
            <p class="modal-card-title">Process Delivery</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              This will mark {{ processDeliveryUuids.length }}
              item{{ processDeliveryUuids.length > 1 ? 's' : '' }}
              as being "delivered".
            </p>
            <b-field horizontal label="Note">
              <b-input name="note"
                       v-model="processDeliveryNote"
                       ref="processDeliveryNote"
                       type="textarea" />
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <b-button type="is-primary"
                      @click="processDeliverySubmit()"
                      :disabled="processDeliverySubmitting"
                      icon-pack="fas"
                      icon-left="save">
              {{ processDeliverySubmitting ? "Working, please wait..." : "Save" }}
            </b-button>
            <b-button @click="processDeliveryShowDialog = false">
              Cancel
            </b-button>
          </footer>

          ${h.end_form()}
        </div>
      </${b}-modal>

  % endif

  % if master.has_perm('process_restock'):

      <${b}-modal has-modal-card
                  % if request.use_oruga:
                      v-model:active="processRestockShowDialog"
                  % else:
                      :active.sync="processRestockShowDialog"
                  % endif
                  >
        <div class="modal-card">
          ${h.form(url(f'{route_prefix}.process_restock'), ref='processRestockForm')}
          ${h.csrf_token(request)}
          ${h.hidden('item_uuids', **{':value': 'processRestockUuids.join()'})}

          <header class="modal-card-head">
            <p class="modal-card-title">Process Restock</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              This will mark {{ processRestockUuids.length }}
              item{{ processRestockUuids.length > 1 ? 's' : '' }}
              as being "restocked".
            </p>
            <b-field horizontal label="Note">
              <b-input name="note"
                       v-model="processRestockNote"
                       ref="processRestockNote"
                       type="textarea" />
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <b-button type="is-primary"
                      @click="processRestockSubmit()"
                      :disabled="processRestockSubmitting"
                      icon-pack="fas"
                      icon-left="save">
              {{ processRestockSubmitting ? "Working, please wait..." : "Save" }}
            </b-button>
            <b-button @click="processRestockShowDialog = false">
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

    % if master.has_perm('process_delivery'):

        ThisPageData.processDeliveryShowDialog = false
        ThisPageData.processDeliveryUuids = []
        ThisPageData.processDeliveryNote = null
        ThisPageData.processDeliverySubmitting = false

        ThisPage.methods.processDeliveryInit = function(items) {
            this.processDeliveryUuids = items.map((item) => item.uuid)
            this.processDeliveryNote = null
            this.processDeliveryShowDialog = true
            this.$nextTick(() => {
                this.$refs.processDeliveryNote.focus()
            })
        }

        ThisPage.methods.processDeliverySubmit = function() {
            this.processDeliverySubmitting = true
            this.$refs.processDeliveryForm.submit()
        }

    % endif

    % if master.has_perm('process_restock'):

        ThisPageData.processRestockShowDialog = false
        ThisPageData.processRestockUuids = []
        ThisPageData.processRestockNote = null
        ThisPageData.processRestockSubmitting = false

        ThisPage.methods.processRestockInit = function(items) {
            this.processRestockUuids = items.map((item) => item.uuid)
            this.processRestockNote = null
            this.processRestockShowDialog = true
            this.$nextTick(() => {
                this.$refs.processRestockNote.focus()
            })
        }

        ThisPage.methods.processRestockSubmit = function() {
            this.processRestockSubmitting = true
            this.$refs.processRestockForm.submit()
        }

    % endif

  </script>
</%def>
