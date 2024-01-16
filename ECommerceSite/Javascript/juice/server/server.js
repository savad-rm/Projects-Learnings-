const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

// Sample juice data
const juices = [
    { id: 1, name: 'Orange Juice', price: 2.50 },
    { id: 2, name: 'Apple Juice', price: 3.00 },
    // Add more juice items as needed
];

// Cart data (for simplicity, use an in-memory cart)
const carts = {};

app.use(bodyParser.json());

// Endpoint to get juice information
app.get('/juices/:id', (req, res) => {
    const juiceId = parseInt(req.params.id);
    const juice = juices.find(j => j.id === juiceId);

    if (juice) {
        res.json(juice);
    } else {
        res.status(404).json({ error: 'Juice not found' });
    }
});

// Endpoint to add items to the cart
app.post('/cart/:id', (req, res) => {
    const juiceId = parseInt(req.params.id);
    const quantity = parseInt(req.body.quantity);

    if (!Number.isInteger(quantity) || quantity <= 0) {
        return res.status(400).json({ error: 'Invalid quantity' });
    }

    const juice = juices.find(j => j.id === juiceId);

    if (!juice) {
        return res.status(404).json({ error: 'Juice not found' });
    }

    const cart = carts[req.sessionID] || [];
    const existingCartItem = cart.find(item => item.id === juiceId);

    if (existingCartItem) {
        existingCartItem.quantity += quantity;
    } else {
        cart.push({ id: juiceId, name: juice.name, price: juice.price, quantity });
    }

    carts[req.sessionID] = cart;

    res.json({ success: true });
});

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
