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
let product = {};

// Given an empty product object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let x = (product) => {

    // This is the Vue data.
    product.data = {
        images: [],
        selected: 0,
    };

    product.update_selected = (index) => {
        product.data.selected = product.data.images[index];
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue product in a single blow.
    product.methods = {
        update_selected: product.update_selected,
    };

    // This creates the Vue instance.
    product.vue = new Vue({
        el: "#vue-product",
        data: product.data,
        methods: product.methods,
        delimiters: ["[[", "]]"]
    });

    // And this initializes it.
    product.init = () => {
        sendRequest("", 'get')
            .then(function (response) {
                product.data.images = response.data.product.images;
            })
            .then(() => {
                product.data.selected = product.data.images[0];
            }).catch(e => {
        });
    };

    // Call to the initializer.
    product.init();
};

// This takes the (empty) product object, and initializes it,
// putting all the code x
x(product);
