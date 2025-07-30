## -*- coding: utf-8; -*-
<%inherit file="/master/create.mako" />

<%def name="page_content()">
  <br />
  <order-creator></order-creator>
</%def>

<%def name="order_form_buttons()">
  <div class="level">
    <div class="level-left">
    </div>
    <div class="level-right">
      <div class="level-item">
        <div class="buttons">
          <b-button type="is-primary"
                    @click="submitOrder()"
                    :disabled="submittingOrder"
                    icon-pack="fas"
                    icon-left="upload">
            {{ submittingOrder ? "Working, please wait..." : "Submit this Order" }}
          </b-button>
          <b-button @click="startOverEntirely()"
                    icon-pack="fas"
                    icon-left="redo">
            Start Over Entirely
          </b-button>
          <b-button @click="cancelOrder()"
                    type="is-danger"
                    icon-pack="fas"
                    icon-left="trash">
            Cancel this Order
          </b-button>
        </div>
      </div>
    </div>
  </div>
</%def>

<%def name="render_vue_templates()">
  ${parent.render_vue_templates()}
  <script type="text/x-template" id="order-creator-template">
    <div>

      <div style="display: flex; justify-content: space-between; margin-bottom: 1.5rem;">
        <div>
          % if expose_store_id:
              <b-loading v-model="storeLoading" is-full-page />
              <b-field label="Store" horizontal
                       :type="storeID ? null : 'is-danger'">
                <b-select v-model="storeID"
                          @input="storeChanged">
                  <option v-for="store in stores"
                          :key="store.store_id"
                          :value="store.store_id">
                    {{ store.display }}
                  </option>
                </b-select>
              </b-field>
          % endif
        </div>
        ${self.order_form_buttons()}
      </div>

      <${b}-collapse class="panel"
                     :class="customerPanelType"
                     % if request.use_oruga:
                         v-model:open="customerPanelOpen"
                     % else:
                         :open.sync="customerPanelOpen"
                     % endif
                     >

        <template #trigger="props">
          <div class="panel-heading"
               role="button"
               style="cursor: pointer;">

            ## TODO: for some reason buefy will "reuse" the icon
            ## element in such a way that its display does not
            ## refresh.  so to work around that, we use different
            ## structure for the two icons, so buefy is forced to
            ## re-draw

            <b-icon v-if="props.open"
                    pack="fas"
                    icon="caret-down">
            </b-icon>

            <span v-if="!props.open">
              <b-icon pack="fas"
                      icon="caret-right">
              </b-icon>
            </span>

            &nbsp;
            <strong v-html="customerPanelHeader"></strong>
          </div>
        </template>

        <div class="panel-block">
          <b-loading v-model="customerLoading" :is-full-page="false" />
          <div style="width: 100%;">

            <div style="display: flex; flex-direction: row;">
              <div style="flex-grow: 1; margin-right: 1rem;">
                % if request.use_oruga:
                    ## TODO: for some reason o-notification variant is not
                    ## being updated properly, so for now the workaround is
                    ## to maintain a separate component for each variant
                    ## i tried to reproduce the problem in a simple page
                    ## but was unable; this is really a hack but it works..
                    <o-notification v-if="customerStatusType == null"
                                    :closable="false">
                      {{ customerStatusText }}
                    </o-notification>
                    <o-notification v-if="customerStatusType == 'is-warning'"
                                    variant="warning"
                                    :closable="false">
                      {{ customerStatusText }}
                    </o-notification>
                    <o-notification v-if="customerStatusType == 'is-danger'"
                                    variant="danger"
                                    :closable="false">
                      {{ customerStatusText }}
                    </o-notification>
                % else:
                    <b-notification :type="customerStatusType"
                                    position="is-bottom-right"
                                    :closable="false">
                      {{ customerStatusText }}
                    </b-notification>
                % endif
              </div>
            </div>

            <br />
            <div class="field">
              <b-radio v-model="customerIsKnown"
                       :native-value="true">
                Customer is already in the system.
              </b-radio>
            </div>

            <div v-show="customerIsKnown"
                 style="padding-left: 10rem; display: flex;">

              <div style="flex-grow: 1;">

                <b-field label="Customer">
                  <div style="display: flex; gap: 1rem; width: 100%;">
                    <wutta-autocomplete ref="customerAutocomplete"
                                        v-model="customerID"
                                        :display="customerName"
                                        service-url="${url(f'{route_prefix}.customer_autocomplete')}"
                                        placeholder="Enter name or phone number"
                                        @input="customerChanged"
                                        :style="{'flex-grow': customerID ? '0' : '1'}"
                                        expanded />
                    <b-button v-if="customerID"
                              @click="refreshCustomer"
                              icon-pack="fas"
                              icon-left="redo"
                              :disabled="refreshingCustomer">
                      {{ refreshingCustomer ? "Working, please wait..." : "Refresh" }}
                    </b-button>
                  </div>
                </b-field>

                <b-field grouped v-show="customerID"
                         style="margin-top: 2rem;">

                  <b-field label="Phone Number"
                           style="margin-right: 3rem;">
                    <div class="level">
                      <div class="level-left">
                        <div class="level-item">
                          <div v-if="orderPhoneNumber">
                            <p>{{ orderPhoneNumber }}</p>
                          </div>
                          <p v-if="!orderPhoneNumber"
                                class="has-text-danger">
                            (no valid phone number on file)
                          </p>
                        </div>
                      </div>
                    </div>
                  </b-field>

                  <b-field label="Email Address">
                    <div class="level">
                      <div class="level-left">
                        <div class="level-item">
                          <div v-if="orderEmailAddress">
                            <p>{{ orderEmailAddress }}</p>
                          </div>
                          <span v-if="!orderEmailAddress"
                                class="has-text-danger">
                            (no valid email address on file)
                          </span>
                        </div>
                      </div>
                    </div>
                  </b-field>

                </b-field>
              </div>
            </div>

            <br />
            <div class="field">
              <b-radio v-model="customerIsKnown"
                       :native-value="false">
                Customer is not yet in the system.
              </b-radio>
            </div>

            <div v-if="!customerIsKnown"
                 style="padding-left: 10rem; display: flex;">
              <div>
                <b-field grouped>
                  <b-field label="First Name">
                    <span
                      ## class="has-text-success"
                      >
                      {{ newCustomerFirstName }}
                    </span>
                  </b-field>
                  <b-field label="Last Name">
                    <span
                      ## class="has-text-success"
                      >
                      {{ newCustomerLastName }}
                    </span>
                  </b-field>
                </b-field>
                <b-field grouped>
                  <b-field label="Phone Number">
                    <span
                      ## class="has-text-success"
                      >
                      {{ newCustomerPhone }}
                    </span>
                  </b-field>
                  <b-field label="Email Address">
                    <span
                      ## class="has-text-success"
                      >
                      {{ newCustomerEmail }}
                    </span>
                  </b-field>
                </b-field>
              </div>

              <div>
                <b-button type="is-primary"
                          @click="editNewCustomerInit()"
                          icon-pack="fas"
                          icon-left="edit">
                  Edit New Customer
                </b-button>
              </div>

              <${b}-modal has-modal-card
                          % if request.use_oruga:
                              v-model:active="editNewCustomerShowDialog"
                          % else:
                              :active.sync="editNewCustomerShowDialog"
                          % endif
                          >
                <div class="modal-card">

                  <header class="modal-card-head">
                    <p class="modal-card-title">Edit New Customer</p>
                  </header>

                  <section class="modal-card-body">
                    <b-field grouped>
                      <b-field label="First Name">
                        <b-input v-model.trim="editNewCustomerFirstName"
                                 ref="editNewCustomerInput">
                        </b-input>
                      </b-field>
                      <b-field label="Last Name">
                        <b-input v-model.trim="editNewCustomerLastName">
                        </b-input>
                      </b-field>
                    </b-field>
                    <b-field grouped>
                      <b-field label="Phone Number">
                        <b-input v-model.trim="editNewCustomerPhone"></b-input>
                      </b-field>
                      <b-field label="Email Address">
                        <b-input v-model.trim="editNewCustomerEmail"></b-input>
                      </b-field>
                    </b-field>
                  </section>

                  <footer class="modal-card-foot">
                    <b-button type="is-primary"
                              icon-pack="fas"
                              icon-left="save"
                              :disabled="editNewCustomerSaveDisabled"
                              @click="editNewCustomerSave()">
                      {{ editNewCustomerSaving ? "Working, please wait..." : "Save" }}
                    </b-button>
                    <b-button @click="editNewCustomerShowDialog = false">
                      Cancel
                    </b-button>
                  </footer>
                </div>
              </${b}-modal>

            </div>
          </div>
        </div> <!-- panel-block -->
      </${b}-collapse>

      <${b}-collapse class="panel"
                  open>

        <template #trigger="props">
          <div class="panel-heading"
               role="button"
               style="cursor: pointer;">

            ## TODO: for some reason buefy will "reuse" the icon
            ## element in such a way that its display does not
            ## refresh.  so to work around that, we use different
            ## structure for the two icons, so buefy is forced to
            ## re-draw

            <b-icon v-if="props.open"
                    pack="fas"
                    icon="caret-down">
            </b-icon>

            <span v-if="!props.open">
              <b-icon pack="fas"
                      icon="caret-right">
              </b-icon>
            </span>

            &nbsp;
            <strong v-html="itemsPanelHeader"></strong>
          </div>
        </template>

        <div class="panel-block">
          <div>
            <div class="buttons">
              <b-button type="is-primary"
                        icon-pack="fas"
                        icon-left="plus"
                        @click="showAddItemDialog()">
                Add Item
              </b-button>
              % if allow_past_item_reorder:
                  <b-button v-if="customerIsKnown && customerID"
                            icon-pack="fas"
                            icon-left="plus"
                            @click="showAddPastItem()">
                    Add Past Item
                  </b-button>

                  <${b}-modal
                    % if request.use_oruga:
                        v-model:active="pastItemsShowDialog"
                    % else:
                        :active.sync="pastItemsShowDialog"
                    % endif
                    >
                    <div class="card">
                      <div class="card-content">

                        <${b}-table :data="pastItems"
                                    icon-pack="fas"
                                    :loading="pastItemsLoading"
                                    % if request.use_oruga:
                                        v-model:selected="pastItemsSelected"
                                    % else:
                                        :selected.sync="pastItemsSelected"
                                    % endif
                                    sortable
                                    paginated
                                    per-page="5"
                                    ## :debounce-search="1000"
                                    >

                          <${b}-table-column label="Scancode"
                                          field="key"
                                          v-slot="props"
                                          sortable>
                            {{ props.row.scancode }}
                          </${b}-table-column>

                          <${b}-table-column label="Brand"
                                          field="brand_name"
                                          v-slot="props"
                                          sortable
                                          searchable>
                            {{ props.row.brand_name }}
                          </${b}-table-column>

                          <${b}-table-column label="Description"
                                          field="description"
                                          v-slot="props"
                                          sortable
                                          searchable>
                            {{ props.row.description }}
                            {{ props.row.size }}
                          </${b}-table-column>

                          <${b}-table-column label="Unit Price"
                                          field="unit_price_reg_display"
                                          v-slot="props"
                                          sortable>
                            {{ props.row.unit_price_reg_display }}
                          </${b}-table-column>

                          <${b}-table-column label="Sale Price"
                                          field="sale_price"
                                          v-slot="props"
                                          sortable>
                            <span class="has-background-warning">
                              {{ props.row.sale_price_display }}
                            </span>
                          </${b}-table-column>

                          <${b}-table-column label="Sale Ends"
                                          field="sale_ends"
                                          v-slot="props"
                                          sortable>
                            <span class="has-background-warning">
                              {{ props.row.sale_ends_display }}
                            </span>
                          </${b}-table-column>

                          <${b}-table-column label="Department"
                                          field="department_name"
                                          v-slot="props"
                                          sortable
                                          searchable>
                            {{ props.row.department_name }}
                          </${b}-table-column>

                          <${b}-table-column label="Vendor"
                                          field="vendor_name"
                                          v-slot="props"
                                          sortable
                                          searchable>
                            {{ props.row.vendor_name }}
                          </${b}-table-column>

                          <template #empty>
                            <div class="content has-text-grey has-text-centered">
                              <p>
                                <b-icon
                                  pack="fas"
                                  icon="sad-tear"
                                  size="is-large">
                                </b-icon>
                              </p>
                              <p>Nothing here.</p>
                            </div>
                          </template>
                        </${b}-table>

                        <div class="buttons">
                          <b-button @click="pastItemsShowDialog = false">
                            Cancel
                          </b-button>
                          <b-button type="is-primary"
                                    icon-pack="fas"
                                    icon-left="plus"
                                    @click="pastItemsAddSelected()"
                                    :disabled="!pastItemsSelected">
                            Add Selected Item
                          </b-button>
                        </div>

                      </div>
                    </div>
                  </${b}-modal>

              % endif
            </div>

            <${b}-modal
              % if request.use_oruga:
                  v-model:active="editItemShowDialog"
              % else:
                  :active.sync="editItemShowDialog"
              % endif
              :can-cancel="['escape', 'x']"
              >
              <div class="card">
                <div class="card-content">
                  <b-loading v-model="editItemLoading" :is-full-page="false" />

                  <${b}-tabs :animated="false"
                             % if request.use_oruga:
                                 v-model="itemDialogTab"
                                 type="toggle"
                             % else:
                                 v-model="itemDialogTabIndex"
                                 type="is-boxed is-toggle"
                             % endif
                             >

                    <${b}-tab-item label="Product"
                                   value="product">

                      <div class="field">
                        <b-radio v-model="productIsKnown"
                                 :native-value="true">
                          Product is already in the system.
                        </b-radio>
                      </div>

                      <div v-show="productIsKnown"
                           style="padding-left: 3rem; display: flex; gap: 1rem;">

                        <div style="flex-grow: 1;">
                          <b-field label="Product">
                            <sideshow-product-lookup v-model="productID"
                                                     ref="productLookup"
                                                     :display="productDisplay"
                                                     @input="productChanged" />
                          </b-field>

                          <div v-if="productID">

                            <b-field grouped>
                              <b-field label="Scancode">
                                <span>{{ productScancode }}</span>
                              </b-field>

                              <b-field label="Unit Size">
                                <span>{{ productSize || '' }}</span>
                              </b-field>

                              <b-field label="Case Size">
                                <span>{{ productCaseQuantity }}</span>
                              </b-field>

                              <b-field label="Reg. Price"
                                       v-if="productSalePriceDisplay">
                                <span>{{ productUnitRegularPriceDisplay }}</span>
                              </b-field>

                              <b-field label="Unit Price"
                                       v-if="!productSalePriceDisplay">
                                <span>{{ productUnitPriceDisplay }}</span>
                              </b-field>

                              <b-field label="Sale Price"
                                       v-if="productSalePriceDisplay">
                                <span class="has-background-warning">
                                  {{ productSalePriceDisplay }}
                                </span>
                              </b-field>

                              <b-field label="Sale Ends"
                                       v-if="productSaleEndsDisplay">
                                <span class="has-background-warning">
                                  {{ productSaleEndsDisplay }}
                                </span>
                              </b-field>

                            </b-field>

                          </div>
                        </div>

##                         <img v-if="productID"
##                              :src="productImageURL"
##                              style="max-height: 150px; max-width: 150px; "/>

                      </div>

                      <br />
                      <div class="field">
                        <b-radio v-model="productIsKnown"
                                 % if not allow_unknown_products:
                                     disabled
                                 % endif
                                 :native-value="false">
                          Product is not yet in the system.
                        </b-radio>
                      </div>

                      <div v-show="!productIsKnown"
                           style="padding-left: 5rem;">

                        <div style="display: flex; gap: 1rem;">

                          <b-field label="Brand"
                                   % if 'brand_name' in pending_product_required_fields:
                                   :type="pendingProduct.brand_name ? null : 'is-danger'"
                                   % endif
                                   style="width: 100%;">
                            <b-input v-model="pendingProduct.brand_name" />
                          </b-field>

                          <b-field label="Description"
                                   % if 'description' in pending_product_required_fields:
                                   :type="pendingProduct.description ? null : 'is-danger'"
                                   % endif
                                   style="width: 100%;">
                            <b-input v-model="pendingProduct.description" />
                          </b-field>

                          <b-field label="Unit Size"
                                   % if 'size' in pending_product_required_fields:
                                   :type="pendingProduct.size ? null : 'is-danger'"
                                   % endif
                                   style="width: 100%;">
                            <b-input v-model="pendingProduct.size" />
                          </b-field>

                        </div>

                        <div style="display: flex; gap: 1rem;">

                          <b-field label="Scancode"
                                   % if 'scancode' in pending_product_required_fields:
                                   :type="pendingProduct.scancode ? null : 'is-danger'"
                                   % endif
                                   style="width: 100%;">
                            <b-input v-model="pendingProduct.scancode" />
                          </b-field>

                          <b-field label="Dept. ID"
                                   % if 'department_id' in pending_product_required_fields:
                                   :type="pendingProduct.department_id ? null : 'is-danger'"
                                   % endif
                                   style="width: 15rem;">
                            <b-input v-model="pendingProduct.department_id"
                                     @input="updateDiscount" />
                          </b-field>

                          <b-field label="Department Name"
                                   % if 'department_name' in pending_product_required_fields:
                                   :type="pendingProduct.department_name ? null : 'is-danger'"
                                   % endif
                                   style="width: 100%;">
                            <b-input v-model="pendingProduct.department_name" />
                          </b-field>

                          <b-field label="Special Order">
                            <b-checkbox v-model="pendingProduct.special_order" />
                          </b-field>

                        </div>

                        <div style="display: flex; gap: 1rem;">

                          <b-field label="Vendor"
                                   % if 'vendor_name' in pending_product_required_fields:
                                   :type="pendingProduct.vendor_name ? null : 'is-danger'"
                                   % endif
                                   style="width: 100%;">
                            <b-input v-model="pendingProduct.vendor_name">
                            </b-input>
                          </b-field>

                          <b-field label="Vendor Item Code"
                                   % if 'vendor_item_code' in pending_product_required_fields:
                                   :type="pendingProduct.vendor_item_code ? null : 'is-danger'"
                                   % endif
                                   style="width: 100%;">
                            <b-input v-model="pendingProduct.vendor_item_code">
                            </b-input>
                          </b-field>

                          <b-field label="Case Size"
                                   % if 'case_size' in pending_product_required_fields:
                                   :type="pendingProduct.case_size ? null : 'is-danger'"
                                   % endif
                                   style="width: 100%;">
                            <b-input v-model="pendingProduct.case_size"
                                     type="number" step="0.01" />
                          </b-field>

                        </div>

                        <div style="display: flex; gap: 1rem;">

                          <b-field label="Unit Cost"
                                   % if 'unit_cost' in pending_product_required_fields:
                                   :type="pendingProduct.unit_cost ? null : 'is-danger'"
                                   % endif
                                   style="width: 100%;">
                            <b-input v-model="pendingProduct.unit_cost"
                                     type="number" step="0.01" />
                          </b-field>

                          <b-field label="Unit Reg. Price"
                                   % if 'unit_price_reg' in pending_product_required_fields:
                                   :type="pendingProduct.unit_price_reg ? null : 'is-danger'"
                                   % endif
                                   style="width: 100%;">
                            <b-input v-model="pendingProduct.unit_price_reg"
                                     type="number" step="0.01">
                            </b-input>
                          </b-field>

                          <b-field label="Gross Margin"
                                   style="width: 100%;">
                            <span class="control">
                              {{ pendingProductGrossMargin }}
                            </span>
                          </b-field>

                        </div>

                        <b-field label="Notes">
                          <b-input v-model="pendingProduct.notes"
                                   type="textarea"
                                   expanded />
                        </b-field>

                      </div>
                    </${b}-tab-item>

                    <${b}-tab-item label="Quantity"
                                   value="quantity">

                      <div style="display: flex; gap: 1rem; white-space: nowrap;">

                        <div style="flex-grow: 1;">
                          <b-field grouped>
                            <b-field label="Product" horizontal>
                              <span :class="productIsKnown ? null : 'has-text-success'"
                                    ## nb. hack to force refresh for vue3
                                    :key="refreshProductDescription">
                                {{ productIsKnown ? productDisplay : (pendingProduct.brand_name || '') + ' ' + (pendingProduct.description || '') + ' ' + (pendingProduct.size || '') }}
                              </span>
                            </b-field>
                          </b-field>

                          <b-field grouped>

                            <b-field label="Unit Size">
                              <span :class="productIsKnown ? null : 'has-text-success'">
                                {{ productIsKnown ? productSize : pendingProduct.size }}
                              </span>
                            </b-field>

                            <b-field label="Reg. Price"
                                     v-if="productSalePriceDisplay">
                              <span>
                                {{ productUnitRegularPriceDisplay }}
                              </span>
                            </b-field>

                            <b-field label="Unit Price"
                                     v-if="!productSalePriceDisplay">
                              <span :class="productIsKnown ? null : 'has-text-success'">
                                {{ productIsKnown ? productUnitPriceDisplay : (pendingProduct.unit_price_reg ? '$' + pendingProduct.unit_price_reg : '') }}
                              </span>
                            </b-field>

                            <b-field label="Sale Price"
                                     v-if="productSalePriceDisplay">
                              <span class="has-background-warning"
                                    :class="productIsKnown ? null : 'has-text-success'">
                                {{ productSalePriceDisplay }}
                              </span>
                            </b-field>

                            <b-field label="Sale Ends"
                                     v-if="productSaleEndsDisplay">
                              <span class="has-background-warning"
                                    :class="productIsKnown ? null : 'has-text-success'">
                                {{ productSaleEndsDisplay }}
                              </span>
                            </b-field>

                            <b-field label="Case Size">
                              <span :class="productIsKnown ? null : 'has-text-success'">
                                {{ productIsKnown ? productCaseQuantity : pendingProduct.case_size }}
                              </span>
                            </b-field>

                            <b-field label="Case Price">
                              <span :class="{'has-text-success': !productIsKnown, 'has-background-warning': !!productSalePriceDisplay}">
                                {{ getCasePriceDisplay() }}
                              </span>
                            </b-field>

                          </b-field>

                          <b-field grouped>

                            <b-field label="Quantity" horizontal>
                              <b-input v-model="productQuantity"
                                       @input="refreshTotalPrice += 1"
                                       style="width: 5rem;" />
                            </b-field>

                            <b-select v-model="productUOM"
                                      @input="refreshTotalPrice += 1">
                              <option v-for="choice in productUnitChoices"
                                      :key="choice.key"
                                      :value="choice.key"
                                      v-html="choice.value">
                              </option>
                            </b-select>

                          </b-field>

                          <div style="display: flex; gap: 1rem;">
                            % if allow_item_discounts:
                                <b-field label="Discount" horizontal>
                                  <div class="level">
                                    <div class="level-item">
                                      ## TODO: needs numeric-input component
                                      <b-input v-model="productDiscountPercent"
                                               @input="refreshTotalPrice += 1"
                                               style="width: 5rem;"
                                               :disabled="!allowItemDiscount" />
                                    </div>
                                    <div class="level-item">
                                      <span>&nbsp;%</span>
                                    </div>
                                  </div>
                                </b-field>
                            % endif
                            <b-field label="Total Price" horizontal expanded
                                     :key="refreshTotalPrice">
                              <span :class="productSalePriceDisplay ? 'has-background-warning': null">
                                {{ getItemTotalPriceDisplay() }}
                              </span>
                            </b-field>
                          </div>

                        </div>
                      </div>

                    </${b}-tab-item>
                  </${b}-tabs>

                  <div class="buttons">
                    <b-button @click="editItemShowDialog = false">
                      Cancel
                    </b-button>
                    <b-button type="is-primary"
                              @click="itemDialogSave()"
                              :disabled="itemDialogSaveDisabled"
                              icon-pack="fas"
                              icon-left="save">
                      {{ itemDialogSaving ? "Working, please wait..." : (this.editItemRow ? "Update Item" : "Add Item") }}
                    </b-button>
                  </div>

                </div>
              </div>
            </${b}-modal>

            <${b}-table v-if="items.length"
                     :data="items"
                     :row-class="(row, i) => row.product_id ? null : 'has-text-success'">

              <${b}-table-column label="Scancode"
                              v-slot="props">
                {{ props.row.product_scancode }}
              </${b}-table-column>

              <${b}-table-column label="Brand"
                              v-slot="props">
                {{ props.row.product_brand }}
              </${b}-table-column>

              <${b}-table-column label="Description"
                              v-slot="props">
                {{ props.row.product_description }}
              </${b}-table-column>

              <${b}-table-column label="Size"
                              v-slot="props">
                {{ props.row.product_size }}
              </${b}-table-column>

              <${b}-table-column label="Department"
                              v-slot="props">
                {{ props.row.department_name }}
              </${b}-table-column>

              <${b}-table-column label="Quantity"
                              v-slot="props">
                <span v-html="props.row.order_qty_display"></span>
              </${b}-table-column>

              <${b}-table-column label="Unit Price"
                              v-slot="props">
                <span
                  ##:class="props.row.pricing_reflects_sale ? 'has-background-warning' : null"
                  >
                  {{ props.row.unit_price_quoted_display }}
                </span>
              </${b}-table-column>

              % if allow_item_discounts:
                  <${b}-table-column label="Discount"
                                     v-slot="props">
                    {{ props.row.discount_percent }}{{ props.row.discount_percent ? " %" : "" }}
                  </${b}-table-column>
              % endif

              <${b}-table-column label="Total"
                              v-slot="props">
                <span :class="props.row.pricing_reflects_sale ? 'has-background-warning' : null">
                  {{ props.row.total_price_display }}
                </span>
              </${b}-table-column>

              <${b}-table-column label="Vendor"
                              v-slot="props">
                {{ props.row.vendor_name }}
              </${b}-table-column>

              <${b}-table-column field="actions"
                              label="Actions"
                              v-slot="props">
                <a href="#"
                   @click.prevent="editItemInit(props.row)">

                  % if request.use_oruga:
                      <span class="icon-text">
                        <o-icon icon="edit" />
                        <span>Edit</span>
                      </span>
                  % else:
                      <i class="fas fa-edit"></i>
                      Edit
                  % endif
                </a>
                &nbsp;

                <a href="#"
                   % if request.use_oruga:
                       class="has-text-danger"
                   % else:
                       class="grid-action has-text-danger"
                   % endif
                   @click.prevent="deleteItem(props.index)">
                  % if request.use_oruga:
                      <span class="icon-text">
                        <o-icon icon="trash" />
                        <span>Delete</span>
                      </span>
                  % else:
                      <i class="fas fa-trash"></i>
                      Delete
                  % endif
                </a>
                &nbsp;
              </${b}-table-column>

            </${b}-table>
          </div>
        </div>
      </${b}-collapse>

      ${self.order_form_buttons()}

      ${h.form(request.current_route_url(), ref='batchActionForm')}
      ${h.csrf_token(request)}
      ${h.hidden('action', **{'v-model': 'batchAction'})}
      ${h.end_form()}

    </div>
  </script>
  <script>

    const OrderCreator = {
        template: '#order-creator-template',
        mixins: [WuttaRequestMixin],

        data() {

            ## TODO
            const defaultUnitChoices = ${json.dumps(default_uom_choices)|n}
            const defaultUOM = ${json.dumps(default_uom)|n}

            return {
                batchAction: null,

                batchTotalPriceDisplay: ${json.dumps(normalized_batch['total_price_display'])|n},

                % if expose_store_id:
                    stores: ${json.dumps(stores)|n},
                    storeID: ${json.dumps(batch.store_id)|n},
                    storeLoading: false,
                % endif

                customerPanelOpen: false,
                customerLoading: false,
                customerIsKnown: ${json.dumps(customer_is_known)|n},
                customerID: ${json.dumps(customer_id)|n},
                customerName: ${json.dumps(customer_name)|n},
                orderPhoneNumber: ${json.dumps(phone_number)|n},
                orderEmailAddress: ${json.dumps(email_address)|n},
                refreshingCustomer: false,

                newCustomerFullName: ${json.dumps(new_customer_full_name or None)|n},
                newCustomerFirstName: ${json.dumps(new_customer_first_name or None)|n},
                newCustomerLastName: ${json.dumps(new_customer_last_name or None)|n},
                newCustomerPhone: ${json.dumps(new_customer_phone or None)|n},
                newCustomerEmail: ${json.dumps(new_customer_email or None)|n},

                editNewCustomerShowDialog: false,
                editNewCustomerFirstName: null,
                editNewCustomerLastName: null,
                editNewCustomerPhone: null,
                editNewCustomerEmail: null,
                editNewCustomerSaving: false,

                items: ${json.dumps(order_items)|n},

                editItemRow: null,
                editItemShowDialog: false,
                editItemLoading: false,
                itemDialogSaving: false,
                % if request.use_oruga:
                    itemDialogTab: 'product',
                % else:
                    itemDialogTabIndex: 0,
                % endif

                productIsKnown: true,
                selectedProduct: null,
                productID: null,
                productDisplay: null,
                productScancode: null,
                productSize: null,
                productCaseQuantity: null,
                productUnitPrice: null,
                productUnitPriceDisplay: null,
                productUnitRegularPriceDisplay: null,
                productCasePrice: null,
                productCasePriceDisplay: null,
                productSalePrice: null,
                productSalePriceDisplay: null,
                productSaleEndsDisplay: null,
                ## TODO?
                ## productSpecialOrder: false,
                productURL: null,
                productImageURL: null,
                productQuantity: null,
                defaultUnitChoices: defaultUnitChoices,
                productUnitChoices: defaultUnitChoices,
                defaultUOM: defaultUOM,
                productUOM: defaultUOM,
                productCaseSize: null,

                % if allow_item_discounts:
                    defaultItemDiscount: ${json.dumps(default_item_discount)|n},
                    deptItemDiscounts: ${json.dumps(dept_item_discounts)|n},
                    allowDiscountsIfOnSale: ${json.dumps(allow_item_discounts_if_on_sale)|n},
                    productDiscountPercent: null,
                % endif

                pendingProduct: {},
                pendingProductRequiredFields: ${json.dumps(pending_product_required_fields)|n},
                ## TODO
                ## departmentOptions: ${json.dumps(department_options)|n},
                departmentOptions: [],

                % if allow_past_item_reorder:
                    pastItemsShowDialog: false,
                    pastItemsLoading: false,
                    pastItems: [],
                    pastItemsSelected: null,
                % endif

                // nb. hack to force refresh for vue3
                refreshProductDescription: 1,
                refreshTotalPrice: 1,

                submittingOrder: false,
            }
        },

        computed: {

            customerPanelHeader() {
                let text = "Customer"

                if (this.customerName) {
                    text = "Customer: " + this.customerName
                }

                if (!this.customerPanelOpen) {
                    text += ' <p class="' + this.customerHeaderClass + '" style="display: inline-block; float: right;">' + this.customerStatusText + '</p>'
                }

                return text
            },

            customerHeaderClass() {
                if (!this.customerPanelOpen) {
                    if (this.customerStatusType == 'is-danger') {
                        return 'has-text-white'
                    }
                }
            },

            customerPanelType() {
                if (!this.customerPanelOpen) {
                    return this.customerStatusType
                }
            },

            customerStatusType() {
                return this.customerStatusTypeAndText.type
            },

            customerStatusText() {
                return this.customerStatusTypeAndText.text
            },

            customerStatusTypeAndText() {
                let phoneNumber = null
                if (this.customerIsKnown) {
                    if (!this.customerID) {
                        return {
                            type: 'is-danger',
                            text: "Please identify the customer.",
                        }
                    }
                    if (!this.orderPhoneNumber) {
                        return {
                            type: 'is-warning',
                            text: "Please provide a phone number for the customer.",
                        }
                    }
                    phoneNumber = this.orderPhoneNumber
                } else { // customer is not known
                    if (!this.customerName) {
                        return {
                            type: 'is-danger',
                            text: "Please identify the customer.",
                        }
                    }
                    if (!this.newCustomerPhone) {
                        return {
                            type: 'is-warning',
                            text: "Please provide a phone number for the customer.",
                        }
                    }
                    phoneNumber = this.newCustomerPhone
                }

                let phoneDigits = phoneNumber.replace(/\D/g, '')
                if (!phoneDigits.length || (phoneDigits.length != 7 && phoneDigits.length != 10)) {
                    return {
                        type: 'is-warning',
                        text: "The phone number does not appear to be valid.",
                    }
                }

                return {
                    type: null,
                    text: "Customer info looks okay.",
                }
            },

            editNewCustomerSaveDisabled() {
                if (this.editNewCustomerSaving) {
                    return true
                }
                if (!(this.editNewCustomerFirstName && this.editNewCustomerLastName)) {
                    return true
                }
                if (!(this.editNewCustomerPhone || this.editNewCustomerEmail)) {
                    return true
                }
                return false
            },

            itemsPanelHeader() {
                let text = "Items"

                if (this.items.length) {
                    text = "Items: " + this.items.length.toString() + " for " + this.batchTotalPriceDisplay
                }

                return text
            },

            % if allow_item_discounts:

                allowItemDiscount() {
                    if (!this.allowDiscountsIfOnSale) {
                        if (this.productSalePriceDisplay) {
                            return false
                        }
                    }
                    return true
                },

            % endif

            pendingProductGrossMargin() {
                let cost = this.pendingProduct.unit_cost
                let price = this.pendingProduct.unit_price_reg
                if (cost && price) {
                    let margin = (price - cost) / price
                    return (100 * margin).toFixed(2).toString() + " %"
                }
            },

            itemDialogSaveDisabled() {

                if (this.itemDialogSaving) {
                    return true
                }

                if (this.productIsKnown) {
                    if (!this.productID) {
                        return true
                    }

                } else {
                    for (let field of this.pendingProductRequiredFields) {
                        if (!this.pendingProduct[field]) {
                            return true
                        }
                    }
                }

                if (!this.productUOM) {
                    return true
                }

                return false
            },
        },

        mounted() {
            if (this.customerStatusType) {
                this.customerPanelOpen = true
            }
        },

        watch: {

            customerIsKnown: function(val) {

                if (val) {
                    // user clicks "customer is in the system"

                    // clear customer
                    this.customerChanged(null)

                    // focus customer autocomplete
                    this.$nextTick(() => {
                        this.$refs.customerAutocomplete.focus()
                    })

                } else {
                    // user clicks "customer is NOT in the system"

                    // remove true customer; set pending (or null)
                    this.setPendingCustomer()
                }
            },
        },

        methods: {

            startOverEntirely() {
                const msg = "Are you sure you want to start over entirely?\n\n"
                      + "This will totally delete this order and start a new one."
                if (!confirm(msg)) {
                    return
                }
                this.batchAction = 'start_over'
                this.$nextTick(function() {
                    this.$refs.batchActionForm.submit()
                })
            },

            cancelOrder() {
                const msg = "Are you sure you want to cancel?\n\n"
                      + "This will totally delete the current order."
                if (!confirm(msg)) {
                    return
                }
                this.batchAction = 'cancel_order'
                this.$nextTick(function() {
                    this.$refs.batchActionForm.submit()
                })
            },

            submitBatchData(params, success, failure) {
                const url = ${json.dumps(request.current_route_url())|n}

                this.wuttaPOST(url, params, response => {
                    if (success) {
                        success(response)
                    }
                }, response => {
                    if (failure) {
                        failure(response)
                    }
                })
            },

            submitOrder() {
                this.submittingOrder = true

                const params = {
                    action: 'submit_order',
                }

                this.submitBatchData(params, response => {
                    if (response.data.next_url) {
                        location.href = response.data.next_url
                    } else {
                        location.reload()
                    }
                }, response => {
                    this.submittingOrder = false
                })
            },

            % if expose_store_id:

                storeChanged(storeID) {
                    this.storeLoading = true
                    const params = {
                        action: 'set_store',
                        store_id: storeID,
                    }
                    this.submitBatchData(params, ({data}) => {
                        this.storeLoading = false
                    }, response => {
                        this.$buefy.toast.open({
                            message: "Update failed: " + (response.data.error || "(unknown error)"),
                            type: 'is-danger',
                            duration: 2000, // 2 seconds
                        })
                        this.storeLoading = false
                    })
                },

            % endif

            customerChanged(customerID, callback) {
                this.customerLoading = true
                this.pastItems = []

                const params = {}
                if (customerID) {
                    params.action = 'assign_customer'
                    params.customer_id = customerID
                } else {
                    params.action = 'unassign_customer'
                }

                this.submitBatchData(params, ({data}) => {
                    this.customerID = data.customer_id
                    this.customerName = data.customer_name
                    this.orderPhoneNumber = data.phone_number
                    this.orderEmailAddress = data.email_address
                    if (callback) {
                        callback()
                    }
                    this.customerLoading = false
                }, response => {
                    this.customerLoading = false
                    this.$buefy.toast.open({
                        message: "Update failed: " + (response.data.error || "(unknown error)"),
                        type: 'is-danger',
                        duration: 2000, // 2 seconds
                    })
                })
            },

            refreshCustomer() {
                this.refreshingCustomer = true
                this.customerChanged(this.customerID, () => {
                    this.refreshingCustomer = false
                    this.$buefy.toast.open({
                        message: "Customer info has been refreshed.",
                        type: 'is-success',
                        duration: 3000, // 3 seconds
                    })
                })
            },

            editNewCustomerInit() {
                this.editNewCustomerFirstName = this.newCustomerFirstName
                this.editNewCustomerLastName = this.newCustomerLastName
                this.editNewCustomerPhone = this.newCustomerPhone
                this.editNewCustomerEmail = this.newCustomerEmail
                this.editNewCustomerShowDialog = true
                this.$nextTick(() => {
                    this.$refs.editNewCustomerInput.focus()
                })
            },

            % if allow_item_discounts:

                updateDiscount(deptID) {
                    if (deptID) {
                        // nb. our map requires ID as string
                        deptID = deptID.toString()
                    }
                    const i = Object.keys(this.deptItemDiscounts).indexOf(deptID)
                    if (i == -1) {
                        this.productDiscountPercent = this.defaultItemDiscount
                    } else {
                        this.productDiscountPercent = this.deptItemDiscounts[deptID]
                    }
                },

            % endif

            editNewCustomerSave() {
                this.editNewCustomerSaving = true

                const params = {
                    action: 'set_pending_customer',
                    first_name: this.editNewCustomerFirstName,
                    last_name: this.editNewCustomerLastName,
                    phone_number: this.editNewCustomerPhone,
                    email_address: this.editNewCustomerEmail,
                }

                this.submitBatchData(params, response => {
                    this.customerName = response.data.new_customer_full_name
                    this.newCustomerFullName = response.data.new_customer_full_name
                    this.newCustomerFirstName = response.data.new_customer_first_name
                    this.newCustomerLastName = response.data.new_customer_last_name
                    this.newCustomerPhone = response.data.phone_number
                    this.orderPhoneNumber = response.data.phone_number
                    this.newCustomerEmail = response.data.email_address
                    this.orderEmailAddress = response.data.email_address
                    this.editNewCustomerShowDialog = false
                    this.editNewCustomerSaving = false
                }, response => {
                    this.$buefy.toast.open({
                        message: "Save failed: " + (response.data.error || "(unknown error)"),
                        type: 'is-danger',
                        duration: 2000, // 2 seconds
                    })
                    this.editNewCustomerSaving = false
                })

            },

            // remove true customer; set pending customer if present
            // (else null). this happens when user clicks "customer is
            // NOT in the system"
            setPendingCustomer() {

                let params
                if (this.newCustomerFirstName) {
                    params = {
                        action: 'set_pending_customer',
                        first_name: this.newCustomerFirstName,
                        last_name: this.newCustomerLastName,
                        phone_number: this.newCustomerPhone,
                        email_address: this.newCustomerEmail,
                    }
                } else {
                    params = {
                        action: 'unassign_customer',
                    }
                }

                this.submitBatchData(params, ({data}) => {
                    this.customerID = data.customer_id
                    this.customerName = data.new_customer_full_name
                    this.orderPhoneNumber = data.phone_number
                    this.orderEmailAddress = data.email_address
                }, response => {
                    this.$buefy.toast.open({
                        message: "Update failed: " + (response.data.error || "(unknown error)"),
                        type: 'is-danger',
                        duration: 2000, // 2 seconds
                    })
                })
            },

            getCasePriceDisplay() {
                if (this.productIsKnown) {
                    return this.productCasePriceDisplay
                }

                let casePrice = this.getItemCasePrice()
                if (casePrice) {
                    return "$" + casePrice
                }
            },

            getItemUnitPrice() {
                if (this.productIsKnown) {
                    return this.productSalePrice || this.productUnitPrice
                }
                return this.pendingProduct.unit_price_reg
            },

            getItemCasePrice() {
                if (this.productIsKnown) {
                    return this.productCasePrice
                }

                if (this.pendingProduct.unit_price_reg) {
                    if (this.pendingProduct.case_size) {
                        let casePrice = this.pendingProduct.unit_price_reg * this.pendingProduct.case_size
                        casePrice = casePrice.toFixed(2)
                        return casePrice
                    }
                }
            },

            getItemTotalPriceDisplay() {
                let basePrice = null
                if (this.productUOM == '${app.enum.ORDER_UOM_CASE}') {
                    basePrice = this.getItemCasePrice()
                } else {
                    basePrice = this.getItemUnitPrice()
                }

                if (basePrice) {
                    let totalPrice = basePrice * this.productQuantity
                    if (totalPrice) {
                        % if allow_item_discounts:
                            if (this.productDiscountPercent) {
                                totalPrice *= (100 - this.productDiscountPercent) / 100
                            }
                        % endif
                        totalPrice = totalPrice.toFixed(2)
                        return "$" + totalPrice
                    }
                }
            },

            clearProduct() {
                this.productID = null
                this.productDisplay = null
                this.productScancode = null
                this.productSize = null
                this.productCaseQuantity = null
                this.productUnitPrice = null
                this.productUnitPriceDisplay = null
                this.productUnitRegularPriceDisplay = null
                this.productCasePrice = null
                this.productCasePriceDisplay = null
                this.productSalePrice = null
                this.productSalePriceDisplay = null
                this.productSaleEndsDisplay = null
                this.productUnitChoices = this.defaultUnitChoices

                % if allow_item_discounts:
                    this.productDiscountPercent = this.defaultItemDiscount
                % endif
            },

            productChanged(productID) {
                if (productID) {
                    this.editItemLoading = true
                    const params = {
                        action: 'get_product_info',
                        product_id: productID,
                    }
                    // nb. it is possible for the handler to "swap"
                    // the product selection, i.e. user chooses a "per
                    // LB" item but the handler only allows selling by
                    // the "case" item.  so we do not assume the uuid
                    // received above is the correct one, but just use
                    // whatever came back from handler
                    this.submitBatchData(params, ({data}) => {
                        this.selectedProduct = data

                        this.productID = data.product_id
                        this.productScancode = data.scancode
                        this.productDisplay = data.full_description
                        this.productSize = data.size
                        this.productCaseQuantity = data.case_size

                        // TODO: what is the difference here
                        this.productUnitPrice = data.unit_price_reg
                        this.productUnitPriceDisplay = data.unit_price_reg_display
                        this.productUnitRegularPriceDisplay = data.unit_price_display

                        this.productCasePrice = data.case_price_quoted
                        this.productCasePriceDisplay = data.case_price_quoted_display

                        this.productSalePrice = data.unit_price_sale
                        this.productSalePriceDisplay = data.unit_price_sale_display
                        this.productSaleEndsDisplay = data.sale_ends_display

                        % if allow_item_discounts:
                            if (this.allowItemDiscount) {
                                if (data?.default_item_discount != null) {
                                    this.productDiscountPercent = data.default_item_discount
                                } else {
                                    this.updateDiscount(data?.department_id)
                                }
                            } else {
                                this.productDiscountPercent = null
                            }
                        % endif

                        // this.setProductUnitChoices(data.uom_choices)

                        % if request.use_oruga:
                            this.itemDialogTab = 'quantity'
                        % else:
                            this.itemDialogTabIndex = 1
                        % endif

                        // nb. hack to force refresh for vue3
                        this.refreshProductDescription += 1
                        this.refreshTotalPrice += 1

                        this.editItemLoading = false

                    }, response => {
                        this.clearProduct()
                        this.editItemLoading = false
                    })
                } else {
                    this.clearProduct()
                }
            },

## TODO
##             productLookupSelected(selected) {
##                 // TODO: this still is a hack somehow, am sure of it.
##                 // need to clean this up at some point
##                 this.selectedProduct = selected
##                 this.clearProduct()
##                 this.productChanged(selected)
##             },

            copyPendingProductAttrs(from, to) {
                to.scancode = from.scancode
                to.brand_name = from.brand_name
                to.description = from.description
                to.size = from.size
                to.department_id = from.department_id
                to.department_name = from.department_name
                to.unit_price_reg = from.unit_price_reg
                to.vendor_name = from.vendor_name
                to.vendor_item_code = from.vendor_item_code
                to.unit_cost = from.unit_cost
                to.case_size = from.case_size
                to.notes = from.notes
                to.special_order = from.special_order
            },

            showAddItemDialog() {
                this.customerPanelOpen = false
                this.editItemRow = null
                this.productIsKnown = true
                ## this.selectedProduct = null
                this.productID = null
                this.productDisplay = null
                this.productScancode = null
                this.productSize = null
                this.productCaseQuantity = null
                this.productUnitPrice = null
                this.productUnitPriceDisplay = null
                this.productUnitRegularPriceDisplay = null
                this.productCasePrice = null
                this.productCasePriceDisplay = null
                this.productSalePrice = null
                this.productSalePriceDisplay = null
                this.productSaleEndsDisplay = null
                ## this.productSpecialOrder = false

                this.pendingProduct = {}

                this.productQuantity = 1
                this.productUnitChoices = this.defaultUnitChoices
                this.productUOM = this.defaultUOM

                % if allow_item_discounts:
                    this.productDiscountPercent = this.defaultItemDiscount
                % endif

                % if request.use_oruga:
                    this.itemDialogTab = 'product'
                % else:
                    this.itemDialogTabIndex = 0
                % endif
                this.editItemShowDialog = true
                this.$nextTick(() => {
                    this.$refs.productLookup.focus()
                })
            },

            editItemInit(row) {
                this.editItemRow = row

                this.productIsKnown = !!row.product_id
                this.productID = row.product_id

                if (row.product_id) {
                    this.selectedProduct = {
                        product_id: row.product_id,
                        full_description: row.product_full_description,
                        url: row.product_url,
                    }
                } else {
                    this.selectedProduct = null
                }

                // nb. must construct new object before updating data
                // (otherwise vue does not notice the changes?)
                let pending = {}
                if (row.pending_product) {
                    this.copyPendingProductAttrs(row.pending_product, pending)
                }
                this.pendingProduct = pending

                this.productDisplay = row.product_full_description
                this.productScancode = row.product_scancode
                this.productSize = row.product_size
                this.productCaseQuantity = row.case_size
                this.productUnitPrice = row.unit_price_quoted
                this.productUnitPriceDisplay = row.unit_price_quoted_display
                this.productUnitRegularPriceDisplay = row.unit_price_reg_display
                this.productCasePrice = row.case_price_quoted
                this.productCasePriceDisplay = row.case_price_quoted_display
                this.productSalePrice = row.sale_price
                this.productSalePriceDisplay = row.unit_price_sale_display
                this.productSaleEndsDisplay = row.sale_ends_display
                ## this.productSpecialOrder = row.special_order

                this.productQuantity = row.order_qty
                this.productUnitChoices = row?.order_uom_choices || this.defaultUnitChoices
                this.productUOM = row.order_uom

                % if allow_item_discounts:
                    this.productDiscountPercent = row.discount_percent
                % endif

                // nb. hack to force refresh for vue3
                this.refreshProductDescription += 1
                this.refreshTotalPrice += 1

                % if request.use_oruga:
                    this.itemDialogTab = 'quantity'
                % else:
                    this.itemDialogTabIndex = 1
                % endif
                this.editItemShowDialog = true
            },

            deleteItem(index) {
                if (!confirm("Are you sure you want to delete this item?")) {
                    return
                }

                let params = {
                    action: 'delete_item',
                    uuid: this.items[index].uuid,
                }
                this.submitBatchData(params, response => {
                    if (response.data.error) {
                        this.$buefy.toast.open({
                            message: "Delete failed:  " + response.data.error,
                            type: 'is-warning',
                            duration: 2000, // 2 seconds
                        })
                    } else {
                        this.items.splice(index, 1)
                        this.batchTotalPriceDisplay = response.data.batch.total_price_display
                    }
                })
            },

            % if allow_past_item_reorder:

                showAddPastItem() {
                    this.pastItemsSelected = null
                    if (!this.pastItems.length) {
                        this.pastItemsLoading = true
                        const params = {action: 'get_past_products'}
                        this.submitBatchData(params, ({data}) => {
                            this.pastItems = data
                            this.pastItemsLoading = false
                        })
                    }
                    this.pastItemsShowDialog = true
                },

                pastItemsAddSelected() {
                    this.pastItemsShowDialog = false
                    const selected = this.pastItemsSelected

                    this.editItemRow = null
                    this.productIsKnown = true
                    this.productID = selected.product_id

                    this.selectedProduct = {
                        product_id: selected.product_id,
                        full_description: selected.full_description,
                        // url: selected.product_url,
                    }

                    this.productDisplay = selected.full_description
                    this.productScancode = selected.scancode
                    this.productSize = selected.size
                    this.productCaseQuantity = selected.case_size
                    this.productUnitPrice = selected.unit_price_quoted
                    this.productUnitPriceDisplay = selected.unit_price_quoted_display
                    this.productUnitRegularPriceDisplay = selected.unit_price_reg_display
                    this.productCasePrice = selected.case_price_quoted
                    this.productCasePriceDisplay = selected.case_price_quoted_display
                    this.productSalePrice = selected.unit_price_sale
                    this.productSalePriceDisplay = selected.unit_price_sale_display
                    this.productSaleEndsDisplay = selected.sale_ends_display
                    this.productSpecialOrder = selected.special_order

                    this.productQuantity = 1
                    this.productUnitChoices = selected?.order_uom_choices || this.defaultUnitChoices
                    this.productUOM = selected?.order_uom || this.defaultUOM

                    % if allow_item_discounts:
                        this.updateDiscount(selected.department_id)
                    % endif

                    // nb. hack to force refresh for vue3
                    this.refreshProductDescription += 1
                    this.refreshTotalPrice += 1

                    % if request.use_oruga:
                        this.itemDialogTab = 'quantity'
                    % else:
                        this.itemDialogTabIndex = 1
                    % endif
                    this.editItemShowDialog = true
                },

            % endif

            itemDialogAttemptSave() {
                this.itemDialogSaving = true
                this.editItemLoading = true

                const params = {
                    order_qty: parseFloat(this.productQuantity),
                    order_uom: this.productUOM,
                }

                if (this.productIsKnown) {
                    params.product_info = this.productID
                } else {
                    params.product_info = this.pendingProduct
                }

                % if allow_item_discounts:
                    if (this.productDiscountPercent) {
                        params.discount_percent = parseFloat(this.productDiscountPercent)
                    }
                % endif

                if (this.editItemRow) {
                    params.action = 'update_item'
                    params.uuid = this.editItemRow.uuid
                } else {
                    params.action = 'add_item'
                }

                this.submitBatchData(params, response => {

                    if (params.action == 'add_item') {
                        this.items.push(response.data.row)

                    } else { // update_item
                        // must update each value separately, instead of
                        // overwriting the item record, or else display will
                        // not update properly
                        for (let [key, value] of Object.entries(response.data.row)) {
                            this.editItemRow[key] = value
                        }
                    }

                    // also update the batch total price
                    this.batchTotalPriceDisplay = response.data.batch.total_price_display

                    this.itemDialogSaving = false
                    this.editItemLoading = false
                    this.editItemShowDialog = false
                }, response => {
                    this.itemDialogSaving = false
                    this.editItemLoading = false
                })
            },

            itemDialogSave() {
                this.itemDialogAttemptSave()
            },
        },
    }

  </script>
</%def>

<%def name="make_vue_components()">
  ${parent.make_vue_components()}
  <script>
    Vue.component('order-creator', OrderCreator)
  </script>
</%def>
