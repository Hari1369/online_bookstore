/* navbar.js */

function renderNavbar() {
  const mount = document.getElementById('navbar');
  if (!mount) return;

  const urls = {
    main: mount.dataset.mainUrl || '/',
    cart: mount.dataset.cartUrl || '#',
    orders: mount.dataset.ordersUrl || '#',
    login: mount.dataset.loginUrl || '#',
    signup: mount.dataset.signupUrl || '#',
    logout: mount.dataset.logoutUrl || '',
    users: mount.dataset.usersUrl || '#',
    product: mount.dataset.productUrl || '#',
    category: mount.dataset.categoryUrl || '#',
    productUpdatePage: mount.dataset.productUpdatePageUrl || '#'
  };
  const isLoggedIn = mount.dataset.authenticated === 'true';
  const isAdmin = mount.dataset.isAdmin === 'true';
  const displayName = (mount.dataset.userName || 'Account').split(' ')[0];
  const cartCount = typeof Cart !== 'undefined' ? Cart.count() : 0;

  mount.innerHTML = `
    <nav class="site-nav">
      <div class="wrap">
        <a class="brand" href="${urls.main}">Online Bookstore</a>
        <form class="nav-search" id="navSearchForm" role="search" action="${urls.main}" method="GET">
          <label for="navSearchInput" class="visually-hidden">Search books</label>
          <input id="navSearchInput" name="q" type="search" placeholder="Search titles or authors…" />
        </form>
        <div class="nav-links">
          <a href="${urls.main}">Browse</a>
          <a href="${urls.cart}">Cart${cartCount ? `<span class="cart-count">${cartCount}</span>` : ''}</a>
          ${isLoggedIn ? `<a href="${urls.orders}">Orders</a>` : ''}
          ${isAdmin ? `<a href="${urls.product}">Add Book</a>` : ''}
          ${isAdmin ? `<a href="${urls.productUpdatePage}">Manage Books</a>` : ''}
          ${isAdmin ? `<a href="${urls.category}">Categories</a>` : ''}
          ${isAdmin ? `<a href="${urls.users}">Users</a>` : ''}
          ${isLoggedIn
            ? `<a href="${urls.logout}" id="navLogout">Log out (${escapeHTML(displayName)})</a>`
            : `<a href="${urls.login}">Log in</a><a href="${urls.signup}">Sign up</a>`
          }
        </div>
      </div>
    </nav>`;

  const searchInput = document.getElementById('navSearchInput');
  const params = new URLSearchParams(window.location.search);
  const currentQuery = params.get('q') || '';
  
  if (searchInput) {
    searchInput.value = currentQuery;
  }

  const form = document.getElementById('navSearchForm');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const query = searchInput.value.trim();
      const redirectUrl = urls.main + (query ? '?q=' + encodeURIComponent(query) : '');
      window.location.href = redirectUrl;
    });
  }

  const logout = document.getElementById('navLogout');
  if (logout && typeof Session !== 'undefined') {
    logout.addEventListener('click', () => { Session.clear(); });
  }
}

function escapeHTML(str) {
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}

document.addEventListener('DOMContentLoaded', renderNavbar);