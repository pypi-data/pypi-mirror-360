
<%def name="make_sideshow_components()">
  ${self.make_sideshow_product_lookup_component()}
</%def>

<%def name="make_sideshow_product_lookup_component()">
  <script type="text/x-template" id="sideshow-product-lookup-template">
    <wutta-autocomplete ref="autocomplete"
                        v-model="productID"
                        :display="display"
                        placeholder="Enter brand, description etc."
                        :service-url="serviceUrl"
                        @input="val => $emit('input', val)" />
  </script>
  <script>
    const SideshowProductLookup = {
        template: '#sideshow-product-lookup-template',

        props: {

            // this should contain the productID, or null
            // caller specifies this as `v-model`
            // component emits @input event when value changes
            value: String,

            // caller must specify initial display string, if the
            // (v-model) value is not empty when component loads
            display: String,

            // the url from which search results are obtained
            serviceUrl: {
                type: String,
                default: '${url('orders.product_autocomplete')}',
            },
        },

        data() {
            return {
                productID: this.value,
            }
        },

        methods: {

            focus() {
                this.$refs.autocomplete.focus()
            },

        },
    }
    Vue.component('sideshow-product-lookup', SideshowProductLookup)
  </script>
</%def>
