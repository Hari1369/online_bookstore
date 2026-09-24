/* navbar.js — renders the top nav into <div id="navbar"></div> on every page.
   Django template tags ({% url %}) are NOT processed in static JS files, so the
   URLs and the login state are read from the data-* attributes that base.html
   puts on #navbar (login state comes from Django's session, not localStorage). */

function renderNavbar() {
  const mount = document.getElementById('navbar');
  if (!mount) return;

  const urls = {
    main: mount.dataset.mainUrl || '/',
    cart: mount.dataset.cartUrl || '#',
    orders: mount.dataset.ordersUrl || '#',
    login: mount.dataset.loginUrl || '#',
    signup: mount.dataset.signupUrl || '#',
    logout: mount.dataset.logoutUrl || ''
  };

  // Real login state from Django (set in base.html)
  const isLoggedIn = mount.dataset.authenticated === 'true';
  const displayName = (mount.dataset.userName || 'Account').split(' ')[0];
  const cartCount = Cart.count();

  mount.innerHTML = `
    <nav class="site-nav">
      <div class="wrap">
        <a class="brand" href="${urls.main}">Online Bookstore</a>
        <form class="nav-search" id="navSearchForm" role="search">
          <label for="navSearchInput" class="visually-hidden">Search books</label>
          <input id="navSearchInput" type="search" placeholder="Search titles or authors…" />
        </form>
        <div class="nav-links">
          <a href="${urls.main}">Browse</a>
          <a href="${urls.cart}">Cart${cartCount ? `<span class="cart-count">${cartCount}</span>` : ''}</a>
          ${isLoggedIn ? `<a href="${urls.orders}">Orders</a>` : ''}
          ${isLoggedIn
            ? `<a href="${urls.logout}" id="navLogout">Log out (${escapeHTML(displayName)})</a>`
            : `<a href="${urls.login}">Log in</a><a href="${urls.signup}">Sign up</a>`
          }
        </div>
      </div>
    </nav>`;

  const form = document.getElementById('navSearchForm');
  const params = new URLSearchParams(location.search);
  document.getElementById('navSearchInput').value = params.get('q') || '';
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const q = document.getElementById('navSearchInput').value.trim();
    location.href = urls.main + (q ? '?q=' + encodeURIComponent(q) : '');
  });

  // Also clear the old localStorage session; the link itself goes to Django's logout view.
  const logout = document.getElementById('navLogout');
  if (logout) {
    logout.addEventListener('click', () => { Session.clear(); });
  }
}

document.addEventListener('DOMContentLoaded', renderNavbar);
