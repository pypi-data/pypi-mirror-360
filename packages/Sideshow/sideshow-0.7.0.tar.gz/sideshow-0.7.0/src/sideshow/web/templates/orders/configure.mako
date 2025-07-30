## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Stores</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="sideshow.orders.expose_store_id"
                  v-model="simpleSettings['sideshow.orders.expose_store_id']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show/choose the Store ID for each order
      </b-checkbox>
    </b-field>

    <b-field v-show="simpleSettings['sideshow.orders.expose_store_id']"
             label="Default Store ID">
      <b-input name="sideshow.orders.default_store_id"
               v-model="simpleSettings['sideshow.orders.default_store_id']"
               @input="settingsNeedSaved = true"
               style="width: 25rem;" />
    </b-field>

  </div>

  <h3 class="block is-size-3">Customers</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field label="Customer Source">
      <b-select name="sideshow.orders.use_local_customers"
                  v-model="simpleSettings['sideshow.orders.use_local_customers']"
                  @input="settingsNeedSaved = true">
        <option value="true">Local Customers (in Sideshow)</option>
        <option value="false">External Customers (e.g. in POS)</option>
      </b-select>
    </b-field>

  </div>

  <h3 class="block is-size-3">Products</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field label="Product Source">
      <b-select name="sideshow.orders.use_local_products"
                  v-model="simpleSettings['sideshow.orders.use_local_products']"
                  @input="settingsNeedSaved = true">
        <option value="true">Local Products (in Sideshow)</option>
        <option value="false">External Products (e.g. in POS)</option>
      </b-select>
    </b-field>

    <b-field label="New/Unknown Products"
             message="If set, user can enter details of an arbitrary new &quot;pending&quot; product.">
      <b-checkbox name="sideshow.orders.allow_unknown_products"
                  v-model="simpleSettings['sideshow.orders.allow_unknown_products']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow creating orders for new/unknown products
      </b-checkbox>
    </b-field>

    <div v-show="simpleSettings['sideshow.orders.allow_unknown_products']"
         style="padding-left: 2rem;">

      <p class="block">
        Require these fields for new product:
      </p>

      <div class="block"
           style="margin-left: 2rem;">
        % for field in pending_product_fields:
            <b-field>
              <b-checkbox name="sideshow.orders.unknown_product.fields.${field}.required"
                          v-model="simpleSettings['sideshow.orders.unknown_product.fields.${field}.required']"
                          native-value="true"
                          @input="settingsNeedSaved = true">
                ${field}
              </b-checkbox>
            </b-field>
        % endfor
      </div>

    </div>
  </div>

  <h3 class="block is-size-3">Pricing</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="sideshow.orders.allow_item_discounts"
                  v-model="simpleSettings['sideshow.orders.allow_item_discounts']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow per-item discounts
      </b-checkbox>
    </b-field>

    <b-field v-show="simpleSettings['sideshow.orders.allow_item_discounts']">
      <b-checkbox name="sideshow.orders.allow_item_discounts_if_on_sale"
                  v-model="simpleSettings['sideshow.orders.allow_item_discounts_if_on_sale']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow discount even if item is on sale
      </b-checkbox>
    </b-field>

    <div v-show="simpleSettings['sideshow.orders.allow_item_discounts']"
         class="block"
         style="display: flex; gap: 0.5rem; align-items: center;">
      <span>Global default item discount</span>
      <b-input name="sideshow.orders.default_item_discount"
               v-model="simpleSettings['sideshow.orders.default_item_discount']"
               @input="settingsNeedSaved = true"
               style="width: 5rem;" />
      <span>%</span>
    </div>

    <div v-show="simpleSettings['sideshow.orders.allow_item_discounts']"
         style="width: 50%;">
      <div style="display: flex; gap: 1rem; align-items: center;">
        <p>Per-Department default item discounts</p>
        <div>
          <b-button type="is-primary"
                    @click="deptItemDiscountInit()"
                    icon-pack="fas"
                    icon-left="plus">
            Add
          </b-button>
          <input type="hidden" name="dept_item_discounts" :value="JSON.stringify(deptItemDiscounts)" />
          <${b}-modal has-modal-card
                      % if request.use_oruga:
                          v-model:active="deptItemDiscountShowDialog"
                      % else:
                          :active.sync="deptItemDiscountShowDialog"
                      % endif
                      >
            <div class="modal-card">

              <header class="modal-card-head">
                <p class="modal-card-title">Default Discount for Department</p>
              </header>

              <section class="modal-card-body">
                <div style="display: flex; gap: 1rem;">
                  <b-field label="Dept. ID"
                           :type="deptItemDiscountDeptID ? null : 'is-danger'">
                    <b-input v-model="deptItemDiscountDeptID"
                             ref="deptItemDiscountDeptID"
                             style="width: 6rem;;" />
                  </b-field>
                  <b-field label="Department Name"
                           :type="deptItemDiscountDeptName ? null : 'is-danger'"
                           style="flex-grow: 1;">
                    <b-input v-model="deptItemDiscountDeptName" />
                  </b-field>
                  <b-field label="Discount"
                           :type="deptItemDiscountPercent ? null : 'is-danger'">
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                      <b-input v-model="deptItemDiscountPercent"
                               ref="deptItemDiscountPercent"
                               style="width: 6rem;" />
                      <span>%</span>
                    </div>
                  </b-field>
                </div>
              </section>

              <footer class="modal-card-foot">
                <b-button type="is-primary"
                          icon-pack="fas"
                          icon-left="save"
                          :disabled="deptItemDiscountSaveDisabled"
                          @click="deptItemDiscountSave()">
                  Save
                </b-button>
                <b-button @click="deptItemDiscountShowDialog = false">
                  Cancel
                </b-button>
              </footer>
            </div>
          </${b}-modal>
        </div>
      </div>
      <${b}-table :data="deptItemDiscounts">
        <${b}-table-column field="department_id"
                           label="Dept. ID"
                           v-slot="props">
          {{ props.row.department_id }}
        </${b}-table-column>
        <${b}-table-column field="department_name"
                           label="Department Name"
                           v-slot="props">
          {{ props.row.department_name }}
        </${b}-table-column>
        <${b}-table-column field="default_item_discount"
                           label="Discount"
                           v-slot="props">
          {{ props.row.default_item_discount }} %
        </${b}-table-column>
        <${b}-table-column label="Actions"
                           v-slot="props">
          <a href="#" @click.prevent="deptItemDiscountInit(props.row)">
            <i class="fas fa-edit" />
            Edit
          </a>
          <a href="#" @click.prevent="deptItemDiscountDelete(props.row)"
             class="has-text-danger">
            <i class="fas fa-trash" />
            Delete
          </a>
        </${b}-table-column>
      </${b}-table>
    </div>
  </div>

  <h3 class="block is-size-3">Batches</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field label="New Order Batch Handler">
      <input type="hidden"
             name="wutta.batch.neworder.handler.spec"
             :value="simpleSettings['wutta.batch.neworder.handler.spec']" />
      <b-select v-model="simpleSettings['wutta.batch.neworder.handler.spec']"
                @input="settingsNeedSaved = true">
        <option :value="null">(use default)</option>
        <option v-for="handler in batchHandlers"
                :key="handler.spec"
                :value="handler.spec">
          {{ handler.spec }}
        </option>
      </b-select>
    </b-field>
  </div>
</%def>

<%def name="modify_vue_vars()">
  ${parent.modify_vue_vars()}
  <script>

    ThisPageData.batchHandlers = ${json.dumps(batch_handlers)|n}

    ThisPageData.deptItemDiscounts = ${json.dumps(dept_item_discounts)|n}
    ThisPageData.deptItemDiscountShowDialog = false
    ThisPageData.deptItemDiscountRow = null
    ThisPageData.deptItemDiscountDeptID = null
    ThisPageData.deptItemDiscountDeptName = null
    ThisPageData.deptItemDiscountPercent = null

    ThisPage.computed.deptItemDiscountSaveDisabled = function() {
        if (!this.deptItemDiscountDeptID) {
            return true
        }
        if (!this.deptItemDiscountDeptName) {
            return true
        }
        if (!this.deptItemDiscountPercent) {
            return true
        }
        return false
    }

    ThisPage.methods.deptItemDiscountDelete = function(row) {
        const i = this.deptItemDiscounts.indexOf(row)
        this.deptItemDiscounts.splice(i, 1)
        this.settingsNeedSaved = true
    }

    ThisPage.methods.deptItemDiscountInit = function(row) {
        this.deptItemDiscountRow = row
        this.deptItemDiscountDeptID = row?.department_id
        this.deptItemDiscountDeptName = row?.department_name
        this.deptItemDiscountPercent = row?.default_item_discount
        this.deptItemDiscountShowDialog = true
        this.$nextTick(() => {
            if (row) {
                this.$refs.deptItemDiscountPercent.focus()
            } else {
                this.$refs.deptItemDiscountDeptID.focus()
            }
        })
    }

    ThisPage.methods.deptItemDiscountSave = function() {
        if (this.deptItemDiscountRow) {
            this.deptItemDiscountRow.department_id = this.deptItemDiscountDeptID
            this.deptItemDiscountRow.department_name = this.deptItemDiscountDeptName
            this.deptItemDiscountRow.default_item_discount = this.deptItemDiscountPercent
        } else {
            this.deptItemDiscounts.push({
                department_id: this.deptItemDiscountDeptID,
                department_name: this.deptItemDiscountDeptName,
                default_item_discount: this.deptItemDiscountPercent,
            })
        }
        this.deptItemDiscountShowDialog = false
        this.settingsNeedSaved = true
    }

  </script>
</%def>
