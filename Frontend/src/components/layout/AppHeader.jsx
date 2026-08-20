import { useState } from "react";
import AppIcon from "../icons/AppIcon";

const NOTIFICATIONS = [
  ["Low Stock: Napa 500mg", "8 boxes remaining — below minimum", "5 min ago", "danger"],
  ["New Order #1028", "Online order received — ৳2,400", "18 min ago", "primary"],
  ["Expiry Warning", "Cefixime 200mg expires in 30 days", "1h ago", "warning"],
];

export default function AppHeader({ title = "Medicines", subtitle = "Medicine catalog and pricing management", onMenuClick }) {
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  return (
    <header className="pharvo-header">
      <button type="button" className="pharvo-header-menu" onClick={onMenuClick} aria-label="Open navigation">
        <AppIcon name="menu" size={20} />
      </button>

      <div className="pharvo-header-copy">
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>

      <label className="pharvo-header-search">
        <span className="sr-only">Search</span>
        <AppIcon name="search" size={14} />
        <input placeholder="Search medicines, orders…" />
      </label>

      <div className="pharvo-header-popover-wrap">
        <button
          type="button"
          className={`pharvo-header-icon-button${notificationsOpen ? " is-active" : ""}`}
          aria-label="Notifications"
          aria-expanded={notificationsOpen}
          onClick={() => { setNotificationsOpen((value) => !value); setProfileOpen(false); }}
        >
          <AppIcon name="bell" size={18} strokeWidth={1.75} />
          <span className="pharvo-notification-dot" />
        </button>
        {notificationsOpen ? (
          <div className="pharvo-popover pharvo-notifications-popover">
            <div className="pharvo-popover-title-row">
              <strong>Notifications</strong><span className="pharvo-popover-count">5</span>
            </div>
            {NOTIFICATIONS.map(([titleText, body, time, tone]) => (
              <div className="pharvo-notification-item" key={titleText}>
                <span className={`pharvo-notification-status is-${tone}`} />
                <div><strong>{titleText}</strong><span>{body}</span></div>
                <time>{time}</time>
              </div>
            ))}
          </div>
        ) : null}
      </div>

      <div className="pharvo-header-popover-wrap">
        <button
          type="button"
          className={`pharvo-profile-button${profileOpen ? " is-active" : ""}`}
          aria-expanded={profileOpen}
          onClick={() => { setProfileOpen((value) => !value); setNotificationsOpen(false); }}
        >
          <span className="pharvo-profile-avatar">OA</span>
          <span className="pharvo-profile-copy"><strong>Owner / Admin</strong><small>admin@pharvo.com</small></span>
          <AppIcon name="chevronDown" size={13} />
        </button>
        {profileOpen ? (
          <div className="pharvo-popover pharvo-profile-popover">
            <div className="pharvo-profile-popover-head"><strong>Owner / Admin</strong><span>admin@pharvo.com</span></div>
            <button type="button"><AppIcon name="users" size={15} /> Profile Settings</button>
            <button type="button"><AppIcon name="notifications" size={15} /> Notifications</button>
            <button type="button" className="is-danger"><AppIcon name="signout" size={15} /> Sign Out</button>
          </div>
        ) : null}
      </div>
    </header>
  );
}
