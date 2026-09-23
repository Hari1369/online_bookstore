/* orders.js */

const STATUSES = ['pending', 'shipped', 'delivered', 'cancelled'];

function statusPill(status) {
  return `<span class="status-pill status-${status}">${status}</span>`;
}

function orderCardHTML(order, opts) {
  const itemsLine = order.items.map(i => `${i.qty}× ${escapeHTML(i.title)}`).join(', ');
  return `
    <div class="order-card">
      <div class="order-head">
        <div>
          <div class="order-id">${order.id}</div>
          <div style="font-size:.82rem;color:var(--ink-soft);">
            ${new Date(order.date).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
            ${opts.showCustomer ? ' · ' + escapeHTML(order.userName || order.userEmail) : ''}
          </div>
        </div>
        ${statusPill(order.status)}
      </div>
      <div class="order-items">${itemsLine}</div>
      <div class="order-foot">
        <strong>${formatPrice(order.total)}</strong>
        <div class="admin-controls">
          ${opts.admin ? `
            <select data-status="${order.id}" data-email="${order.userEmail}">
              ${STATUSES.map(s => `<option value="${s}" ${s === order.status ? 'selected' : ''}>${s}</option>`).join('')}
            </select>
            <button class="btn btn-danger btn-sm" data-delete="${order.id}" data-email="${order.userEmail}">Delete</button>
          ` : (order.status === 'pending' ? `<button class="btn btn-ghost btn-sm" data-cancel="${order.id}" style="color:var(--error);">Cancel order</button>` : '')}
        </div>
      </div>
    </div>`;
}

function renderOrders() {
  const user = Session.get();
  const root = document.getElementById('ordersRoot');
  const note = document.getElementById('orderNote');

  if (!user) {
    root.innerHTML = `<p class="empty-state">Please <a href="login.html">log in</a> to see your orders.</p>`;
    return;
  }

  const placedId = new URLSearchParams(location.search).get('placed');
  if (placedId) {
    note.innerHTML = `<div class="form-alert show">Order ${escapeHTML(placedId)} placed — thank you.</div>`;
  }

  const admin = Session.isAdmin();
  document.getElementById('ordersHeading').textContent = admin ? 'All orders' : 'Your orders';

  const orders = admin ? Orders.allOrders() : Orders.forUser(user.email).map(o => ({ ...o, userEmail: user.email }));

  if (!orders.length) {
    root.innerHTML = `<p class="empty-state">No orders yet. <a href="index.html">Start browsing</a>.</p>`;
    return;
  }

  orders.sort((a, b) => new Date(b.date) - new Date(a.date));
  root.innerHTML = orders.map(o => orderCardHTML(o, { admin, showCustomer: admin })).join('');

  root.querySelectorAll('[data-status]').forEach(sel => {
    sel.addEventListener('change', () => {
      Orders.updateStatus(sel.dataset.email, sel.dataset.status, sel.value);
      renderOrders();
    });
  });
  root.querySelectorAll('[data-delete]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (confirm('Delete this order permanently?')) {
        Orders.remove(btn.dataset.email, btn.dataset.delete);
        renderOrders();
      }
    });
  });
  root.querySelectorAll('[data-cancel]').forEach(btn => {
    btn.addEventListener('click', () => {
      Orders.updateStatus(user.email, btn.dataset.cancel, 'cancelled');
      renderOrders();
    });
  });
}

document.addEventListener('DOMContentLoaded', renderOrders);
