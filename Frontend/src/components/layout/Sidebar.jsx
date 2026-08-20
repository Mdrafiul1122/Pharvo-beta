import AppIcon from "../icons/AppIcon";

const MAIN_ITEMS = [
  ["dashboard", "Dashboard"],
  ["sales", "POS / Sales"],
  ["medicines", "Medicines"],
  ["inventory", "Inventory"],
  ["customers", "Customers / CRM"],
  ["orders", "Orders"],
  ["reports", "Reports & Analytics"],
];

const ADMIN_ITEMS = [
  ["notifications", "Notifications"],
  ["audit", "Audit Log"],
  ["users", "User Management"],
  ["settings", "Settings"],
];

function NavGroup({ title, items, activePage, onNavigate }) {
  return (
    <div className="pharvo-sidebar-group">
      <p className="pharvo-sidebar-label">{title}</p>
      <div className="pharvo-sidebar-items">
        {items.map(([id, label]) => (
          <button
            type="button"
            key={id}
            className={`pharvo-sidebar-item${activePage === id ? " is-active" : ""}`}
            onClick={() => onNavigate?.(id)}
            aria-current={activePage === id ? "page" : undefined}
          >
            <AppIcon name={id} size={20} strokeWidth={1.75} />
            <span>{label}</span>
            {id === "notifications" ? <span className="pharvo-sidebar-badge">5</span> : null}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function Sidebar({ activePage = "medicines", mobileOpen = false, onClose, onNavigate }) {
  return (
    <>
      {mobileOpen ? <button className="pharvo-sidebar-backdrop" type="button" aria-label="Close navigation" onClick={onClose} /> : null}
      <aside className={`pharvo-sidebar${mobileOpen ? " is-open" : ""}`} aria-label="Application navigation">
        <div className="pharvo-sidebar-brand">
          <div className="pharvo-sidebar-logo" aria-hidden="true"><AppIcon name="medicines" size={20} strokeWidth={2.4} /></div>
          <div>
            <div className="pharvo-sidebar-brand-name">PHARVO</div>
            <div className="pharvo-sidebar-brand-subtitle">Pharmacy Management</div>
          </div>
          <button className="pharvo-sidebar-mobile-close" type="button" onClick={onClose} aria-label="Close navigation">
            <AppIcon name="close" size={18} />
          </button>
        </div>

        <nav className="pharvo-sidebar-nav">
          <NavGroup title="Main Menu" items={MAIN_ITEMS} activePage={activePage} onNavigate={onNavigate} />
          <NavGroup title="Administration" items={ADMIN_ITEMS} activePage={activePage} onNavigate={onNavigate} />
        </nav>

        <div className="pharvo-sidebar-footer">
          <button type="button" className="pharvo-portal-button">
            <AppIcon name="smartphone" size={15} /> Customer Portal
          </button>
          <button type="button" className="pharvo-signout-button">
            <AppIcon name="signout" size={16} /> Sign Out
          </button>
        </div>
      </aside>
    </>
  );
}
