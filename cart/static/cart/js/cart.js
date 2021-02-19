function sendRequest(url, method, data) {
    return axios({
        method: method,
        url: url,
        data: data,
        xsrfCookieName: 'csrftoken',
        xsrfHeaderName: 'X-CSRFTOKEN',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
        }
    })
}
// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let cart = {};
const DOMAIN_NAME= '127.0.0.1:8000';

// Given an empty cart object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let i = (cart) => {

    // This is the Vue data.
    cart.data = {
        cart: [],
        subtotal: 0,
        count: 0,
        stripe: 0,
    };

    cart.increment_item = (index, item_id) => {
        sendRequest("http://" + DOMAIN_NAME + "/add_cart/" + item_id, 'get')
            .then(function (response) {
                cart.vue.cart[index][1].quantity+= 1;
                cart.data.count+= 1;
                cart.data.subtotal+= parseFloat(cart.data.cart[index][1].unit_price);
            });
    };

    cart.decrement_item = (index, item_id) => {
        if (cart.vue.cart[index][1].quantity > 0) {
            sendRequest("http://" + DOMAIN_NAME + "/remove_from_cart/" + item_id, 'get')
                .then(function (response) {
                        cart.vue.cart[index][1].quantity-= 1;
                        cart.data.count-= 1;
                        cart.data.subtotal-= parseFloat(cart.data.cart[index][1].unit_price);
                    });
        }
    };

    cart.checkout = () => {
        fetch("/create_checkout_session/")
        .then((result) => { return result.json(); })
        .then((data) => {
            console.log(data)
            return cart.data.stripe.redirectToCheckout({sessionId: data.sessionId})
        })
        .then((res) => {
        });
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue cart in a single blow.
    cart.methods = {
        increment_item: cart.increment_item,
        decrement_item: cart.decrement_item,
        checkout: cart.checkout,
    };

    // This creates the Vue instance.
    cart.vue = new Vue({
        el: "#vue-cart",
        data: cart.data,
        methods: cart.methods,
        delimiters: ["[[", "]]"]
    });

    // And this initializes it.
    cart.init = () => {
        sendRequest("", 'get')
            .then(function (response) {
                cart.vue.cart = response.data.cart;
            })
            .then(() => {
                for (let i = 0; i < cart.data.cart.length; i++) {
                    cart.data.count+= cart.data.cart[i][1].quantity;
                    cart.data.subtotal+= parseFloat(cart.data.cart[i][1].total_price);
                }
            }).catch(e => {
        });
        fetch("/config/")
        .then((result) => { return result.json(); })
        .then((data) => {
            cart.data.stripe = Stripe(data.publicKey);
        });
    };

    // Call to the initializer.
    cart.init();
};

// This takes the (empty) cart object, and initializes it,
// putting all the code i
i(cart);
