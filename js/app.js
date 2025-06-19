let isLoggedIn = false;
let token = null;
let product_id = null
let product = null;
let products = null;

// Check if the AUTH_TOKEN cookie is set
function checkAuthToken() {
    token_exists = document.cookie.split(';').some((cookie) => cookie.trim().startsWith('AUTH_TOKEN='));
    if (token_exists) {
        token = document.cookie.split(';').filter((cookie) => cookie.startsWith("AUTH_TOKEN"))[0].split("=")[1] // Extract the token value
        return true;
    }
    return false;
}

async function login(username, password) {
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) throw new Error('Login failed');

        const data = await response.json();
        document.cookie = `AUTH_TOKEN=${data.token};`;
        isLoggedIn = true;
        token = data.token;
        window.location.href = '/products.html'; // Redirect to products page after successful login
    } catch (error) {
        console.error('Error during login:', error);
        alert('Login failed. Please check your credentials.');
    }
}

function logout() {
    document.cookie = `AUTH_TOKEN=a; expires=Thu, 01 Jan 1970 00:00:00 GMT;`; // Clear the AUTH_TOKEN cookie
    isLoggedIn = false;
    token = null;
    localStorage.removeItem('cart'); // Clear cart on logout
    window.location.href = '/';
}

async function register(name, email, pass) {
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, pass })
        });

        if (!response.ok) throw new Error('Registration failed');

        const data = await response.json();
        alert('Registration successful! You can now log in.');
        window.location.href = '/login.html'; // Redirect to login page after successful registration
    } catch (error) {
        console.error('Error during registration:', error);
        alert('Registration failed. Please try again.');
    }
}

async function getUserData() {
    user_id = parseInt(token.slice(-3));
    response = await fetch(`/api/users?id=${user_id}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (!response.ok) {
        console.error('Error fetching user data:', response.statusText);
        return null;
    }
    const data = await response.json();
    response = await fetch("/api/transactions?user_id=" + user_id, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (!response.ok) {
        console.error('Error fetching transactions:', response.statusText);
        return data;
    }
    data.transactions = await response.json();
    return data;
}

async function fetchProducts () {
    try {
        const response = await fetch('/api/products');
        if (!response.ok) throw new Error('Network response was not ok');
        products = JSON.parse((await response.text()).replaceAll("'",'"'));
        Alpine.store("products").products = products;
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

async function fetchProduct() {
    product_id = new URLSearchParams(window.location.search).get('id');
    if (!product_id) {
        console.error('Product ID is required');
        return;
    }
    
    response = await fetch(`/api/products?id=${product_id}`)
    data = JSON.parse((await response.text()).replaceAll("'",'"'))
    product = data;
    console.log(data)
    document.getElementById('product-name').textContent = data.name;
    document.getElementById('product-description').textContent = data.description;
    document.getElementById('product-price-element')._x_model.set(data.price.toFixed(2));
    document.getElementById("product-image").src = data.images


    if (data.imageUrl) {
        document.getElementById('product-image').src = data.imageUrl;
    }
    }

async function fetchComments() {
    try {
        console.log("algo")
        const response = await fetch('/api/comments?product_id=' + product_id);
        if (!response.ok) throw new Error('Network response was not ok');
        //console.log((await response.text()).replaceAll("'",'"'))
        comments = JSON.parse((await response.text()).replaceAll("'",'"'))
        Alpine.store("products").comments = comments;
    } catch (error) {
        console.error('Error fetching comments:', error);
    }
}

//Adds product to cart in local storage
function addToCart(id, amount) {
    if (!isLoggedIn) {
        alert('You must be logged in to add items to your cart.');
        return;
    }

    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const productIndex = cart.findIndex(item => item.id === id);

    if (productIndex > -1) {
        cart[productIndex].quantity += amount; // Increment quantity if product already exists
    } else {
        cart.push({ id: id, quantity: amount }); // Add new product with quantity amount
    }

    localStorage.setItem('cart', JSON.stringify(cart));
    alert('Product added to cart successfully!');
}

function removeFromCart(id) {
    if (!isLoggedIn) {
        alert('You must be logged in to remove items from your cart.');
        return;
    }

    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const productIndex = cart.findIndex(item => parseInt(item.id) === id);
    console.log(id)
    console.log(cart)
    console.log(productIndex)
    if (productIndex > -1) {
        cart.splice(productIndex, 1); // Remove product from cart
        localStorage.setItem('cart', JSON.stringify(cart));
        window.location.reload(); // Reload the page to reflect changes
    } else {
        alert('Product not found in cart.');
    }
}

async function getCartProducts() {
    if (!isLoggedIn) {
        alert('You must be logged in to view your cart.');
        return [];
    }

    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    if (cart.length === 0) {
        return [];
    }

    try {
        const response = await fetch('/api/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ cart })
        });

        if (!response.ok) throw new Error('Failed to fetch cart products');
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching cart products:', error);
        alert('Failed to fetch cart products. Please try again later.');
        return [];
    }
}

async function addComment() {
    if (!isLoggedIn) {
        alert('You must be logged in to add a comment.');
        return;
    }

    const commentText = Alpine.store("products").comment_text.trim();
    if (!commentText) {
        alert('Comment cannot be empty.');
        return;
    }

    response = await fetch('/api/comments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            user_id: parseInt(token.slice(-3)),
            product_id: product_id,
            text: commentText
        })
    })
    if (!response.ok) {
        console.error('Error adding comment:', response.statusText);
        alert('Failed to add comment. Please try again.');
        return;
    }
    const newComment = await response.json();
    Alpine.store("products").comment_text = ""; // Clear the comment input field    
    await fetchComments(); // Refresh comments after adding a new one
}

//TODO: Terminar de integrar esta funcion con la API externa de pagos.
async function checkout() {
    const urlParams = new URLSearchParams(window.location.search);
    const payUrl = urlParams.get('payUrl');
    response = await fetch(payUrl, {
        method: "POST",
        body: JSON.stringify({
            token: token,
            cart: JSON.parse(localStorage.getItem('cart')),
            [atob("ZmxhZw==")]: atob("ZDBkMDI1ZjU4OTQ1NjU2OWU0MjRjOTM1OWNhNDFjMzU=")
        }),
    })
    if (!response.ok) {
        console.error('Error during checkout:', response.statusText);
        alert('Checkout failed. Please try again.');
        return;
    }
    await addTransaction(parseInt(token.slice(-3)), JSON.parse(localStorage.getItem('cart')));
    alert('Checkout successful! Thank you for your purchase.');
    localStorage.removeItem('cart'); // Clear cart after successful checkout
    window.location.href = '/products.html'; // Redirect to products page after checkout
}

async function addTransaction(user_id, cart) {
    try {
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ user_id, cart })
        });

        if (!response.ok) throw new Error('Failed to add transaction');

        const data = await response.json();
        console.log('Transaction added successfully:', data);
    } catch (error) {
        console.error('Error adding transaction:', error);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    isLoggedIn = checkAuthToken();
    if (window.location.pathname === '/product.html') {
        await fetchProduct();
        await fetchComments()
    } else if (window.location.pathname === '/products.html') {
        await fetchProducts();
    }
});

document.addEventListener("alpine:init", () => {
    isLoggedIn = checkAuthToken();
    Alpine.store("products", {
        products: [],
        comments: [],
        comment_text: "",
        fetchProducts: fetchProducts
    }
    )
})