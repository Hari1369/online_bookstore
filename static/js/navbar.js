/* navbar.js — renders the top nav into <div id="navbar"></div> on every page */

function renderNavbar() {
  const mount = document.getElementById('navbar');
  if (!mount) return;
  const user = Session.get();
  const cartCount = Cart.count();

  mount.innerHTML = `
    <nav class="site-nav">
      <div class="wrap">
        <a class="brand" href="{% url 'main' %}">Online Bookstore</a>
        <form class="nav-search" id="navSearchForm" role="search">
          <label for="navSearchInput" class="visually-hidden">Search books</label>
          <input id="navSearchInput" type="search" placeholder="Search titles or authors…" />
        </form>
        <div class="nav-links">
          <a href="{% url 'main' %}">Browse</a>
          <a href="{% url 'cart' %}">Cart${cartCount ? `<span class="cart-count">${cartCount}</span>` : ''}</a>
          ${user ? `<a href="{% url 'orders' %}">Orders</a>` : ''}
          ${user
            ? `<a href="#" id="navLogout">Log out (${escapeHTML(user.name.split(' ')[0])})</a>`
            : `<a href="{% url 'login' %}">Log in</a><a href="{% url 'signup' %}">Sign up</a>`
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
    location.href = 'index.html' + (q ? '?q=' + encodeURIComponent(q) : '');
  });

  const logout = document.getElementById('navLogout');
  if (logout) {
    logout.addEventListener('click', (e) => {
      e.preventDefault();
      Session.clear();
      location.href = 'index.html';
    });
  }
}

document.addEventListener('DOMContentLoaded', renderNavbar);
