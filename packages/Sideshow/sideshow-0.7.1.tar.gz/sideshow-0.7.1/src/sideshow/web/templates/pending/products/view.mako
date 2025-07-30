## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="tool_panels()">
  ${parent.tool_panels()}

  <wutta-tool-panel heading="Status" style="white-space: nowrap;">
    <b-field horizontal label="Current Status">
      <span>${instance.status.value}</span>
    </b-field>

    % if instance.status.name == 'READY' and master.has_perm('resolve') and not use_local_products:
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="object-ungroup"
                  @click="resolveInit()">
          Resolve Product
        </b-button>
        <b-modal :active.sync="resolveShowDialog">
          <div class="card">
            <div class="card-content">
              ${h.form(master.get_action_url('resolve', instance), **{'@submit': 'resolveSubmitting = true'})}
              ${h.csrf_token(request)}

              <div style="display: flex; gap: 1rem;">

                <div style="flex-grow: 1;">

                  <p class="block has-text-weight-bold">
                    Please identify the corresponding External Product.
                  </p>
                  <p class="block">
                    All related orders etc. will be updated accordingly.
                  </p>
                  <b-field grouped>
                    <b-field label="Scancode">
                      <span>${instance.scancode or ''}</span>
                    </b-field>
                    <b-field label="Brand">
                      <span>${instance.brand_name or ''}</span>
                    </b-field>
                    <b-field label="Description">
                      <span>${instance.description or ''}</span>
                    </b-field>
                    <b-field label="Size">
                      <span>${instance.size or ''}</span>
                    </b-field>
                  </b-field>
                  <b-field grouped>
                    <b-field label="Vendor Name">
                      <span>${instance.vendor_name or ''}</span>
                    </b-field>
                    <b-field label="Vendor Item Code">
                      <span>${instance.vendor_item_code or ''}</span>
                    </b-field>
                  </b-field>
                </div>

                <div style="flex-grow: 1;">
                  <b-field label="External Product">
                    <div>
                      <sideshow-product-lookup v-model="resolveProductID"
                                               ref="productLookup" />
                      ${h.hidden('product_id', **{':value': 'resolveProductID'})}
                    </div>
                  </b-field>
                </div>

              </div>

              <footer>
                <div class="buttons">
                <b-button @click="resolveShowDialog = false">
                  Cancel
                </b-button>
                <b-button type="is-primary"
                          native-type="submit"
                          icon-pack="fas"
                          icon-left="object-ungroup"
                          :disabled="resolveSubmitting">
                  {{ resolveSubmitting ? "Working, please wait..." : "Resolve" }}
                </b-button>
                </div>
              </footer>

              ${h.end_form()}
            </div>
          </div>
        </b-modal>
    % endif

    % if instance.status.name == 'READY' and master.has_perm('ignore') and not use_local_products:
        <b-button type="is-warning"
                  icon-pack="fas"
                  icon-left="ban"
                  @click="ignoreShowDialog = true">
          Ignore Product
        </b-button>
        <b-modal has-modal-card
                 :active.sync="ignoreShowDialog">
          <div class="modal-card">
            ${h.form(master.get_action_url('ignore', instance), **{'@submit': 'ignoreSubmitting = true'})}
            ${h.csrf_token(request)}

            <header class="modal-card-head">
              <p class="modal-card-title">Ignore Product</p>
            </header>

            <section class="modal-card-body">
              <p class="block has-text-weight-bold">
                Really ignore this product?
              </p>
              <p class="block">
                This will change the product status to "ignored"<br />
                and you will no longer be prompted to resolve it.
              </p>
            </section>

            <footer class="modal-card-foot">
              <b-button @click="ignoreShowDialog = false">
                Cancel
              </b-button>
              <b-button type="is-warning"
                        native-type="submit"
                        icon-pack="fas"
                        icon-left="ban"
                        :disabled="ignoreSubmitting">
                {{ ignoreSubmitting ? "Working, please wait..." : "Ignore" }}
              </b-button>
            </footer>

            ${h.end_form()}
          </div>
        </b-modal>
    % endif
  </wutta-tool-panel>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    % if instance.status.name == 'READY' and master.has_perm('resolve') and not use_local_products:

        ThisPageData.resolveShowDialog = false
        ThisPageData.resolveProductID = null
        ThisPageData.resolveSubmitting = false

        ThisPage.methods.resolveInit = function() {
            this.resolveShowDialog = true
            this.$nextTick(() => {
                this.$refs.productLookup.focus()
            })
        }

    % endif

    % if instance.status.name == 'READY' and master.has_perm('ignore') and not use_local_products:

        ThisPageData.ignoreShowDialog = false
        ThisPageData.ignoreSubmitting = false

    % endif

  </script>
</%def>
