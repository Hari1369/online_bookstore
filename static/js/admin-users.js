/* admin-users.js — super-admin view of every account in THIS BROWSER's localStorage.
   Users are client-side data (see store.js), so this page can only show accounts
   created in the same browser it's viewed from — it is not a real cross-device
   user table until Users.all() is backed by a server API (e.g. GET /api/users/). */

// store.js doesn't ship a delete method for users; add it here rather than editing
// store.js, since that file may already be wired into the rest of your project.
if (!Users.remove) {
  Users.remove = function (email) {
    const list = this.all().filter(u => u.email.toLowerCase() !== email.toLowerCase());
    this.save(list);
  };
}

function renderAdminUsers() {
  const root = document.getElementById('adminUsersRoot');
  const me = Session.get();

  if (!me || !Session.isAdmin()) {
    root.innerHTML = `<p class="empty-state">This page is for admins only. <a href="login.html">Log in with an admin account</a>.</p>`;
    return;
  }

  root.innerHTML = `
    <div class="field" style="max-width:320px;">
      <label for="userSearch" class="visually-hidden">Search users</label>
      <input id="userSearch" type="search" placeholder="Search by name or email…">
    </div>
    <table class="cart-table" style="margin-top:18px;">
      <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Role</th><th></th></tr></thead>
      <tbody id="userRows"></tbody>
    </table>`;

  const rowsEl = document.getElementById('userRows');
  const searchInput = document.getElementById('userSearch');

  function draw() {
    const q = searchInput.value.trim().toLowerCase();
    const users = Users.all().filter(u =>
      !q || u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    );

    if (!users.length) {
      rowsEl.innerHTML = `<tr><td colspan="5" class="empty-state">No matching users.</td></tr>`;
      return;
    }

    rowsEl.innerHTML = users.map(u => {
      const isSelf = u.email.toLowerCase() === me.email.toLowerCase();
      return `
        <tr>
          <td>${escapeHTML(u.name)}${isSelf ? ' <span style="color:var(--ink-soft);font-size:.8rem;">(you)</span>' : ''}</td>
          <td>${escapeHTML(u.email)}</td>
          <td>${escapeHTML(u.phone || '—')}</td>
          <td>
            <select data-role="${u.email}" ${isSelf ? 'disabled' : ''} style="padding:6px 8px;border-radius:3px;border:1px solid var(--line);">
              <option value="customer" ${u.role !== 'admin' ? 'selected' : ''}>Customer</option>
              <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Admin</option>
            </select>
          </td>
          <td>
            <button class="btn btn-danger btn-sm" data-delete="${u.email}" ${isSelf ? 'disabled title="You can\'t delete your own account"' : ''}>Delete</button>
          </td>
        </tr>`;
    }).join('');

    rowsEl.querySelectorAll('[data-role]').forEach(sel => {
      sel.addEventListener('change', () => {
        Users.update(sel.dataset.role, { role: sel.value });
        draw();
      });
    });
    rowsEl.querySelectorAll('[data-delete]:not([disabled])').forEach(btn => {
      btn.addEventListener('click', () => {
        if (confirm(`Delete the account ${btn.dataset.delete}? This can't be undone.`)) {
          Users.remove(btn.dataset.delete);
          draw();
        }
      });
    });
  }

  searchInput.addEventListener('input', draw);
  draw();
}

document.addEventListener('DOMContentLoaded', renderAdminUsers);
