/* cart-page.js */

function renderCart() {
  const root = document.getElementById('cartRoot');
  const items = Cart.detailed();

  if (!items.length) {
    root.innerHTML = `<p class="empty-state">Your cart is empty. <a href="index.html">Browse the catalogue</a>.</p>`;
    return;
  }

  root.innerHTML = `
    <table class="cart-table">
      <thead><tr><th>Book</th><th>Price</th><th>Quantity</th><th>Subtotal</th><th></th></tr></thead>
      <tbody>
        ${items.map(i => `
          <tr data-row="${i.book.id}">
            <td>
              <div class="cart-item-title">${escapeHTML(i.book.title)}</div>
              <div class="cart-item-author">${escapeHTML(i.book.author)}</div>
            </td>
            <td>${formatPrice(i.book.price)}</td>
            <td>
              <div class="qty-row" style="margin:0;">
                <button type="button" data-minus="${i.book.id}" aria-label="Decrease quantity">−</button>
                <input type="number" min="1" value="${i.qty}" data-qty="${i.book.id}" style="width:48px;">
                <button type="button" data-plus="${i.book.id}" aria-label="Increase quantity">+</button>
              </div>
            </td>
            <td>${formatPrice(i.book.price * i.qty)}</td>
            <td><button class="btn btn-ghost btn-sm" data-remove="${i.book.id}" style="color:var(--error);">Remove</button></td>
          </tr>
        `).join('')}
      </tbody>
    </table>
    <div class="cart-summary">
      <div class="line"><span>Items</span><span>${Cart.count()}</span></div>
      <div class="line total"><span>Total</span><span>${formatPrice(Cart.total())}</span></div>
      <button class="btn btn-primary btn-block" id="checkoutBtn" style="margin-top:16px;">Place order</button>
    </div>`;

  root.querySelectorAll('[data-minus]').forEach(b => b.addEventListener('click', () => bump(b.dataset.minus, -1)));
  root.querySelectorAll('[data-plus]').forEach(b => b.addEventListener('click', () => bump(b.dataset.plus, 1)));
  root.querySelectorAll('[data-qty]').forEach(inp => inp.addEventListener('change', () => {
    Cart.setQty(Number(inp.dataset.qty), Math.max(1, Number(inp.value) || 1));
    renderCart(); renderNavbar();
  }));
  root.querySelectorAll('[data-remove]').forEach(b => b.addEventListener('click', () => {
    Cart.remove(Number(b.dataset.remove));
    renderCart(); renderNavbar();
  }));
  const checkoutBtn = document.getElementById('checkoutBtn');
  if (checkoutBtn) checkoutBtn.addEventListener('click', placeOrder);
}

function bump(id, delta) {
  const items = Cart.items();
  const it = items.find(i => i.bookId === Number(id));
  if (it) Cart.setQty(Number(id), it.qty + delta);
  renderCart(); renderNavbar();
}

function placeOrder() {
  const user = Session.get();
  if (!user) {
    alert('Please log in to place an order.');
    location.href = 'login.html';
    return;
  }
  const items = Cart.detailed();
  if (!items.length) return;
  const order = Orders.create(user.email, items, Cart.total());
  Cart.clear();
  location.href = 'orders.html?placed=' + order.id;
}

document.addEventListener('DOMContentLoaded', renderCart);
