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



    const qtyInput = document.getElementById("qtyInput");
    const qtyMinus = document.getElementById("qtyMinus");
    const qtyPlus = document.getElementById("qtyPlus");
    const addToCartBtn = document.getElementById("addToCartBtn");
    const addedNote = document.getElementById("addedNote");

    qtyMinus.addEventListener("click", function () {
        var quantity = Number(qtyInput.value);
        if (quantity > 1) {
            quantity = quantity - 1;
        }
        qtyInput.value = quantity;
    });


    qtyPlus.addEventListener("click", function () {
        var quantity = Number(qtyInput.value);
        quantity = quantity + 1;
        qtyInput.value = quantity;
    });


    addToCartBtn.addEventListener("click", function () {
        var quantity = Number(qtyInput.value);
        if (quantity < 1 || isNaN(quantity)) {
            quantity = 1;
        }
        Cart.add(book.id, quantity);
        renderNavbar();
        addedNote.style.display = "inline";
        setTimeout(function () {
            addedNote.style.display = "none";
        }, 1500);
    });
}

document.addEventListener('DOMContentLoaded', renderProduct);
