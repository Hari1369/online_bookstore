/* product.js — renders a single book's detail page */

function renderProduct() {
  const id = new URLSearchParams(location.search).get('id');
  const book = BookStore.find(id);
  const root = document.getElementById('productRoot');

  if (!book) {
    root.innerHTML = `<div class="section"><p class="empty-state">That book isn't in the catalogue (it may have been removed). <a href="index.html">Back to browsing</a>.</p></div>`;
    return;
  }

  root.innerHTML = `
    <div class="product-layout">
      ${coverHTML(book)}
      <div class="product-info">
        <span class="cat">${CATEGORY_LABELS[book.category]}</span>
        <h1>${escapeHTML(book.title)}</h1>
        <div class="author">by ${escapeHTML(book.author)}</div>
        <p>${escapeHTML(book.description)}</p>
        <div class="price">${formatPrice(book.price)}</div>
        <div class="qty-row">
          <button type="button" id="qtyMinus" aria-label="Decrease quantity">−</button>
          <input id="qtyInput" type="number" min="1" value="1" aria-label="Quantity">
          <button type="button" id="qtyPlus" aria-label="Increase quantity">+</button>
        </div>
        <button class="btn btn-primary" id="addToCartBtn">Add to cart</button>
        <span id="addedNote" style="margin-left:10px; color:var(--teal); display:none;">Added to cart ✓</span>
        <div class="isbn">ISBN ${escapeHTML(book.isbn)}</div>
      </div>
    </div>`;

  const qtyInput = document.getElementById('qtyInput');
  document.getElementById('qtyMinus').addEventListener('click', () => {
    qtyInput.value = Math.max(1, Number(qtyInput.value) - 1);
  });
  document.getElementById('qtyPlus').addEventListener('click', () => {
    qtyInput.value = Number(qtyInput.value) + 1;
  });
  document.getElementById('addToCartBtn').addEventListener('click', () => {
    Cart.add(book.id, Math.max(1, Number(qtyInput.value) || 1));
    renderNavbar();
    const note = document.getElementById('addedNote');
    note.style.display = 'inline';
    setTimeout(() => note.style.display = 'none', 1500);
  });
}

document.addEventListener('DOMContentLoaded', renderProduct);
