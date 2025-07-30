## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="render_grid_tag()">
  % if master.has_perm('process_contact'):
      ${grid.render_vue_tag(**{'@process-contact-success': "processContactSuccessInit", '@process-contact-failure': "processContactFailureInit"})}
  % else:
      ${grid.render_vue_tag()}
  % endif
</%def>

<%def name="page_content()">
  ${parent.page_content()}

  % if master.has_perm('process_contact'):

      <${b}-modal has-modal-card
                  % if request.use_oruga:
                      v-model:active="processContactSuccessShowDialog"
                  % else:
                      :active.sync="processContactSuccessShowDialog"
                  % endif
                  >
        <div class="modal-card">
          ${h.form(url(f'{route_prefix}.process_contact_success'), ref='processContactSuccessForm')}
          ${h.csrf_token(request)}
          ${h.hidden('item_uuids', **{':value': 'processContactSuccessUuids.join()'})}

          <header class="modal-card-head">
            <p class="modal-card-title">Process Contact Success</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              This will mark {{ processContactSuccessUuids.length }}
              item{{ processContactSuccessUuids.length > 1 ? 's' : '' }}
              as being "contacted".
            </p>
            <b-field horizontal label="Note">
              <b-input name="note"
                       v-model="processContactSuccessNote"
                       ref="processContactSuccessNote"
                       type="textarea" />
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <b-button type="is-primary"
                      @click="processContactSuccessSubmit()"
                      :disabled="processContactSuccessSubmitting"
                      icon-pack="fas"
                      icon-left="save">
              {{ processContactSuccessSubmitting ? "Working, please wait..." : "Save" }}
            </b-button>
            <b-button @click="processContactSuccessShowDialog = false">
              Cancel
            </b-button>
          </footer>

          ${h.end_form()}
        </div>
      </${b}-modal>

      <${b}-modal has-modal-card
                  % if request.use_oruga:
                      v-model:active="processContactFailureShowDialog"
                  % else:
                      :active.sync="processContactFailureShowDialog"
                  % endif
                  >
        <div class="modal-card">
          ${h.form(url(f'{route_prefix}.process_contact_failure'), ref='processContactFailureForm')}
          ${h.csrf_token(request)}
          ${h.hidden('item_uuids', **{':value': 'processContactFailureUuids.join()'})}

          <header class="modal-card-head">
            <p class="modal-card-title">Process Contact Failure</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              This will mark {{ processContactFailureUuids.length }}
              item{{ processContactFailureUuids.length > 1 ? 's' : '' }}
              as being "contact failed".
            </p>
            <b-field horizontal label="Note">
              <b-input name="note"
                       v-model="processContactFailureNote"
                       ref="processContactFailureNote"
                       type="textarea" />
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <b-button type="is-primary"
                      @click="processContactFailureSubmit()"
                      :disabled="processContactFailureSubmitting"
                      icon-pack="fas"
                      icon-left="save">
              {{ processContactFailureSubmitting ? "Working, please wait..." : "Save" }}
            </b-button>
            <b-button @click="processContactFailureShowDialog = false">
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
  % if master.has_perm('process_contact'):
      <script>

        ThisPageData.processContactSuccessShowDialog = false
        ThisPageData.processContactSuccessUuids = []
        ThisPageData.processContactSuccessNote = null
        ThisPageData.processContactSuccessSubmitting = false

        ThisPage.methods.processContactSuccessInit = function(items) {
            this.processContactSuccessUuids = items.map((item) => item.uuid)
            this.processContactSuccessNote = null
            this.processContactSuccessShowDialog = true
            this.$nextTick(() => {
                this.$refs.processContactSuccessNote.focus()
            })
        }

        ThisPage.methods.processContactSuccessSubmit = function() {
            this.processContactSuccessSubmitting = true
            this.$refs.processContactSuccessForm.submit()
        }

        ThisPageData.processContactFailureShowDialog = false
        ThisPageData.processContactFailureUuids = []
        ThisPageData.processContactFailureNote = null
        ThisPageData.processContactFailureSubmitting = false

        ThisPage.methods.processContactFailureInit = function(items) {
            this.processContactFailureUuids = items.map((item) => item.uuid)
            this.processContactFailureNote = null
            this.processContactFailureShowDialog = true
            this.$nextTick(() => {
                this.$refs.processContactFailureNote.focus()
            })
        }

        ThisPage.methods.processContactFailureSubmit = function() {
            this.processContactFailureSubmitting = true
            this.$refs.processContactFailureForm.submit()
        }

      </script>
  % endif
</%def>
