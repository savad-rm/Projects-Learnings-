document.addEventListener('DOMContentLoaded', function () {
    const juiceListContainer = document.getElementById('juice-list');
    const cartContainer = document.getElementById('cart');
    const cartItemsContainer = document.getElementById('cart-items');
    const totalAmountContainer = document.getElementById('total-amount');

    // Sample juice data
    const juices = [
        { id: 1, name: 'Orange Juice', price: 2.50, image: 'orange.jpg' },
        { id: 2, name: 'Apple Juice', price: 3.00, image: 'apple.jpg' },
        // Add more juice items as needed
    ];

    // Initialize the juice list
    juices.forEach(juice => {
        const juiceItem = document.createElement('div');
        juiceItem.className = 'juice-item';
        juiceItem.innerHTML = `
            <img src="${juice.image}" alt="${juice.name}" width="100">
            <p>${juice.name}</p>
            <p>$${juice.price.toFixed(2)}</p>
            <input type="number" id="quantity-${juice.id}" placeholder="Quantity" min="1">
            <button onclick="addToCart(${juice.id})">Add to Cart</button>
        `;
        juiceListContainer.appendChild(juiceItem);
    });

    // Initialize the shopping cart
    let cart = [];

    // Function to add items to the cart
    window.addToCart = function (juiceId) {
        const quantityInput = document.getElementById(`quantity-${juiceId}`);
        const quantity = parseInt(quantityInput.value);

        if (quantity > 0) {
            const juice = juices.find(j => j.id === juiceId);
            const cartItem = { id: juice.id, name: juice.name, price: juice.price, quantity };

            const existingCartItem = cart.find(item => item.id === juiceId);
            if (existingCartItem) {
                existingCartItem.quantity += quantity;
            } else {
                cart.push(cartItem);
            }

            updateCartDisplay();
        }
    };

    // Function to update the cart display
    function updateCartDisplay() {
        cartItemsContainer.innerHTML = '';
        let totalAmount = 0;

        cart.forEach(item => {
            const cartItemElement = document.createElement('li');
            cartItemElement.className = 'cart-item';
            cartItemElement.innerHTML = `
                <span>${item.name} x${item.quantity}</span>
                <span>$${(item.price * item.quantity).toFixed(2)}</span>
            `;
            cartItemsContainer.appendChild(cartItemElement);

            totalAmount += item.price * item.quantity;
        });

        totalAmountContainer.textContent = totalAmount.toFixed(2);
    }
});
