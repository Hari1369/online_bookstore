/* store.js
   Small localStorage wrapper that stands in for the DRF API this frontend
   will eventually call (/api/products/, /api/cart/, /api/orders/, /api/auth/).
   Swap the functions in this file for fetch() calls when the backend exists —
   the rest of the app only talks to these functions, never to localStorage directly. */

const DB_KEYS = {
  users: 'bookstore_users',
  currentUser: 'bookstore_current_user',
  customBooks: 'bookstore_custom_books',
  deletedBooks: 'bookstore_deleted_books',
  cart: 'bookstore_cart_',       // + email, one cart per user
  orders: 'bookstore_orders_',   // + email
  resetTokens: 'bookstore_reset_tokens'
};

function readJSON(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (e) {
    return fallback;
  }
}
function writeJSON(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

/* ---------- Users / auth ---------- */
const Users = {
  all() { return readJSON(DB_KEYS.users, []); },
  save(list) { writeJSON(DB_KEYS.users, list); },
  findByEmail(email) {
    return this.all().find(u => u.email.toLowerCase() === email.toLowerCase());
  },
  create(user) {
    const list = this.all();
    list.push(user);
    this.save(list);
  },
  update(email, patch) {
    const list = this.all();
    const idx = list.findIndex(u => u.email.toLowerCase() === email.toLowerCase());
    if (idx > -1) { list[idx] = { ...list[idx], ...patch }; this.save(list); }
  }
};

function seedAdmin() {
  if (!Users.findByEmail('admin@Online Bookstore.test')) {
    Users.create({
      name: 'Store Admin',
      email: 'admin@Online Bookstore.test',
      phone: '',
      password: 'admin123',
      role: 'admin'
    });
  }
}
seedAdmin();

const Session = {
  get() { return readJSON(DB_KEYS.currentUser, null); },
  set(user) { writeJSON(DB_KEYS.currentUser, user ? { name: user.name, email: user.email, role: user.role || 'customer' } : null); },
  clear() { localStorage.removeItem(DB_KEYS.currentUser); },
  isAdmin() { const u = this.get(); return !!u && u.role === 'admin'; }
};

/* ---------- Books (admin CRUD layered over the static catalog) ---------- */
const BookStore = {
  customBooks() { return readJSON(DB_KEYS.customBooks, []); },
  deletedIds() { return readJSON(DB_KEYS.deletedBooks, []); },
  all() {
    const deleted = new Set(this.deletedIds());
    return [...BASE_BOOKS, ...this.customBooks()].filter(b => !deleted.has(b.id));
  },
  find(id) { return this.all().find(b => b.id === Number(id)); },
  add(book) {
    const list = this.customBooks();
    const nextId = Math.max(0, ...BASE_BOOKS.map(b => b.id), ...list.map(b => b.id)) + 1;
    const newBook = { ...book, id: nextId };
    list.push(newBook);
    writeJSON(DB_KEYS.customBooks, list);
    return newBook;
  },
  update(id, patch) {
    const list = this.customBooks();
    const idx = list.findIndex(b => b.id === Number(id));
    if (idx > -1) {
      list[idx] = { ...list[idx], ...patch };
      writeJSON(DB_KEYS.customBooks, list);
    } else {
      // editing a base/seed book: store the override as a custom entry with same id
      list.push({ ...BASE_BOOKS.find(b => b.id === Number(id)), ...patch, id: Number(id) });
      writeJSON(DB_KEYS.customBooks, list);
    }
  },
  remove(id) {
    id = Number(id);
    const list = this.customBooks().filter(b => b.id !== id);
    writeJSON(DB_KEYS.customBooks, list);
    const deleted = this.deletedIds();
    if (BASE_BOOKS.some(b => b.id === id) && !deleted.includes(id)) {
      deleted.push(id);
      writeJSON(DB_KEYS.deletedBooks, deleted);
    }
  }
};

/* ---------- Cart (per logged-in user; falls back to "guest") ---------- */
function cartKey() {
  const u = Session.get();
  return DB_KEYS.cart + (u ? u.email.toLowerCase() : 'guest');
}
const Cart = {
  items() { return readJSON(cartKey(), []); }, // [{bookId, qty}]
  save(items) { writeJSON(cartKey(), items); },
  add(bookId, qty = 1) {
    const items = this.items();
    const existing = items.find(i => i.bookId === bookId);
    if (existing) existing.qty += qty; else items.push({ bookId, qty });
    this.save(items);
  },
  setQty(bookId, qty) {
    let items = this.items();
    if (qty <= 0) { items = items.filter(i => i.bookId !== bookId); }
    else { const it = items.find(i => i.bookId === bookId); if (it) it.qty = qty; }
    this.save(items);
  },
  remove(bookId) { this.save(this.items().filter(i => i.bookId !== bookId)); },
  clear() { this.save([]); },
  count() { return this.items().reduce((n, i) => n + i.qty, 0); },
  detailed() {
    return this.items().map(i => ({ ...i, book: BookStore.find(i.bookId) })).filter(i => i.book);
  },
  total() { return this.detailed().reduce((sum, i) => sum + i.book.price * i.qty, 0); }
};

/* ---------- Orders ---------- */
function ordersKey(email) { return DB_KEYS.orders + email.toLowerCase(); }
const Orders = {
  forUser(email) { return readJSON(ordersKey(email), []); },
  allOrders() {
    return Users.all().flatMap(u => this.forUser(u.email).map(o => ({ ...o, userEmail: u.email, userName: u.name })));
  },
  create(email, items, total) {
    const list = this.forUser(email);
    const order = {
      id: 'MG-' + Date.now().toString().slice(-8),
      date: new Date().toISOString(),
      items: items.map(i => ({ id: i.book.id, title: i.book.title, price: i.book.price, qty: i.qty })),
      total,
      status: 'pending'
    };
    list.unshift(order);
    writeJSON(ordersKey(email), list);
    return order;
  },
  updateStatus(email, orderId, status) {
    const list = this.forUser(email);
    const o = list.find(o => o.id === orderId);
    if (o) { o.status = status; writeJSON(ordersKey(email), list); }
  },
  remove(email, orderId) {
    const list = this.forUser(email).filter(o => o.id !== orderId);
    writeJSON(ordersKey(email), list);
  }
};

/* ---------- Password reset (simulated, no email server available client-side) ---------- */
const ResetTokens = {
  all() { return readJSON(DB_KEYS.resetTokens, {}); },
  issue(email) {
    const tokens = this.all();
    const token = Math.random().toString(36).slice(2, 8).toUpperCase();
    tokens[email.toLowerCase()] = token;
    writeJSON(DB_KEYS.resetTokens, tokens);
    return token;
  },
  verify(email, token) {
    const tokens = this.all();
    return tokens[email.toLowerCase()] === token.toUpperCase();
  },
  clear(email) {
    const tokens = this.all();
    delete tokens[email.toLowerCase()];
    writeJSON(DB_KEYS.resetTokens, tokens);
  }
};
