/* main.js — homepage: search, category filter, sort, admin product CRUD */

const COLOR_SWATCHES = ["#3F6B62","#A9812F","#6B4C6B","#2E5266","#7A4A2B","#455A64","#556B4F","#33475B"];

function currentFilters() {
  const params = new URLSearchParams(location.search);
  return { q: (params.get('q') || '').trim().toLowerCase(), cat: params.get('cat') || 'all' };
}

function setFilters({ q, cat }) {
  const params = new URLSearchParams();
  if (q) params.set('q', q);
  if (cat && cat !== 'all') params.set('cat', cat);
  const qs = params.toString();
  history.replaceState(null, '', 'index.html' + (qs ? '?' + qs : ''));
}

function renderAdminBar() {
  const bar = document.getElementById('adminBar');
  if (!Session.isAdmin()) { bar.innerHTML = ''; return; }
  bar.innerHTML = `
    <div class="admin-bar">
      <span>You're signed in as admin — you can add, edit or remove books.</span>
      <button class="btn btn-primary btn-sm" id="addBookBtn">Add book</button>
    </div>`;
  document.getElementById('addBookBtn').addEventListener('click', () => openBookModal());
}

function renderGrid() {
  const { q, cat } = currentFilters();
  document.querySelectorAll('.chip').forEach(c => c.classList.toggle('active', c.dataset.cat === cat));
  document.getElementById('resultsHeading').textContent =
    cat === 'all' ? 'All books' : CATEGORY_LABELS[cat];

  let books = BookStore.all().filter(b => {
    const matchesCat = cat === 'all' || b.category === cat;
    const matchesQ = !q || b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q);
    return matchesCat && matchesQ;
  });

  const sort = document.getElementById('priceSort').value;
  if (sort === 'asc') books = books.sort((a, b) => a.price - b.price);
  if (sort === 'desc') books = books.sort((a, b) => b.price - a.price);

  const grid = document.getElementById('bookGrid');
  if (!books.length) {
    grid.innerHTML = `<p class="empty-state">No books match “${escapeHTML(q)}”. Try another search or category.</p>`;
    return;
  }

  grid.innerHTML = books.map(b => `
    <div class="book-card">
      <a href="product.html?id=${b.id}">${coverHTML(b)}</a>
      <div class="meta">
        <span class="cat">${CATEGORY_LABELS[b.category]}</span>
        <a href="product.html?id=${b.id}" class="title" style="color:inherit;text-decoration:none;">${escapeHTML(b.title)}</a>
        <span class="author">${escapeHTML(b.author)}</span>
        <span class="price">${formatPrice(b.price)}</span>
      </div>
      <div class="row-actions">
        <button class="btn btn-outline btn-sm" data-add="${b.id}" style="flex:1;">Add to cart</button>
        ${Session.isAdmin() ? `
          <button class="btn btn-ghost btn-sm" data-edit="${b.id}">Edit</button>
          <button class="btn btn-ghost btn-sm" data-del="${b.id}" style="color:var(--error);">Delete</button>` : ''}
      </div>
    </div>
  `).join('');

  grid.querySelectorAll('[data-add]').forEach(btn => {
    btn.addEventListener('click', () => {
      Cart.add(Number(btn.dataset.add), 1);
      renderNavbar();
      btn.textContent = 'Added ✓';
      setTimeout(() => btn.textContent = 'Add to cart', 900);
    });
  });
  grid.querySelectorAll('[data-edit]').forEach(btn => {
    btn.addEventListener('click', () => openBookModal(BookStore.find(btn.dataset.edit)));
  });
  grid.querySelectorAll('[data-del]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (confirm('Remove this book from the catalogue?')) {
        BookStore.remove(btn.dataset.del);
        renderGrid();
      }
    });
  });
}

function openBookModal(book) {
  const isEdit = !!book;
  const root = document.getElementById('modalRoot');
  root.innerHTML = `
    <div style="position:fixed;inset:0;background:rgba(29,43,38,.5);display:flex;align-items:center;justify-content:center;padding:20px;z-index:50;" id="modalOverlay">
      <div style="background:var(--card);max-width:440px;width:100%;padding:28px;border-radius:4px;max-height:90vh;overflow:auto;">
        <h2>${isEdit ? 'Edit book' : 'Add a book'}</h2>
        <form id="bookForm">
          <div class="field"><label>Title</label><input required name="title" value="${book ? escapeHTML(book.title) : ''}"></div>
          <div class="field"><label>Author</label><input required name="author" value="${book ? escapeHTML(book.author) : ''}"></div>
          <div class="field"><label>Price (USD)</label><input required name="price" type="number" step="0.01" min="0" value="${book ? book.price : ''}"></div>
          <div class="field"><label>ISBN</label><input required name="isbn" value="${book ? escapeHTML(book.isbn) : ''}"></div>
          <div class="field"><label>Category</label>
            <select name="category" style="width:100%;padding:10px;border-radius:3px;border:1px solid var(--line);">
              ${Object.entries(CATEGORY_LABELS).map(([v, l]) => `<option value="${v}" ${book && book.category === v ? 'selected' : ''}>${l}</option>`).join('')}
            </select>
          </div>
          <div class="field"><label>Description</label><input name="description" value="${book ? escapeHTML(book.description) : ''}"></div>
          <div class="field"><label>Cover color</label>
            <div style="display:flex;gap:8px;">
              ${COLOR_SWATCHES.map(c => `<label style="width:26px;height:26px;border-radius:50%;background:${c};cursor:pointer;border:2px solid ${book && book.color === c ? 'var(--ink)' : 'transparent'};display:inline-block;">
                <input type="radio" name="color" value="${c}" ${(book ? book.color === c : c === COLOR_SWATCHES[0]) ? 'checked' : ''} class="visually-hidden"></label>`).join('')}
            </div>
          </div>
          <div style="display:flex;gap:10px;margin-top:18px;">
            <button type="submit" class="btn btn-primary" style="flex:1;">${isEdit ? 'Save changes' : 'Add book'}</button>
            <button type="button" class="btn btn-outline" id="modalCancel">Cancel</button>
          </div>
        </form>
      </div>
    </div>`;

  document.getElementById('modalCancel').addEventListener('click', () => root.innerHTML = '');
  document.getElementById('modalOverlay').addEventListener('click', (e) => { if (e.target.id === 'modalOverlay') root.innerHTML = ''; });
  document.getElementById('bookForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const data = {
      title: fd.get('title').trim(),
      author: fd.get('author').trim(),
      price: parseFloat(fd.get('price')),
      isbn: fd.get('isbn').trim(),
      category: fd.get('category'),
      description: fd.get('description').trim(),
      color: fd.get('color') || COLOR_SWATCHES[0]
    };
    if (isEdit) BookStore.update(book.id, data); else BookStore.add(data);
    root.innerHTML = '';
    renderGrid();
  });
}

document.addEventListener('DOMContentLoaded', () => {
  renderAdminBar();
  renderGrid();
  document.getElementById('categoryChips').addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    const { q } = currentFilters();
    setFilters({ q, cat: chip.dataset.cat });
    renderGrid();
  });
  document.getElementById('priceSort').addEventListener('change', renderGrid);
});
