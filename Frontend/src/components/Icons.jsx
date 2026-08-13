function Svg({ className = "", children, ...rest }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
      {...rest}
    >
      {children}
    </svg>
  );
}

export function LogoMark({ className = "" }) {
  return (
    <svg
      className={className}
      viewBox="0 0 40 40"
      role="img"
      aria-label="PHARVO logo"
      focusable="false"
    >
      <rect className="logo__tile" x="1" y="1" width="38" height="38" rx="11" />
      <rect className="logo__cross" x="16.7" y="7.5" width="6.6" height="25" rx="3.3" />
      <rect className="logo__cross" x="7.5" y="16.7" width="25" height="6.6" rx="3.3" />
    </svg>
  );
}

export function EyeIcon({ className = "field__icon" }) {
  return (
    <Svg className={className}>
      <path
        d="M1.5 12S5.5 5.5 12 5.5 22.5 12 22.5 12 18.5 18.5 12 18.5 1.5 12 1.5 12Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="12" cy="12" r="3.2" fill="none" stroke="currentColor" strokeWidth="1.8" />
    </Svg>
  );
}

export function EyeOffIcon({ className = "field__icon" }) {
  return (
    <Svg className={className}>
      <path
        d="M4 4l16 16"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <path
        d="M10.6 6.1A9.8 9.8 0 0 1 12 6c6.5 0 10.5 6 10.5 6a17 17 0 0 1-2.6 3.3M6.7 7A16.6 16.6 0 0 0 1.5 12S5.5 18 12 18a9.6 9.6 0 0 0 2.9-.4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

export function AlertIcon({ className = "" }) {
  return (
    <Svg className={className}>
      <circle cx="12" cy="12" r="9.2" fill="none" stroke="currentColor" strokeWidth="1.7" />
      <path
        d="M12 7.5v5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <circle cx="12" cy="16.4" r="1" fill="currentColor" />
    </Svg>
  );
}

export function CheckIcon({ className = "" }) {
  return (
    <Svg className={className}>
      <path
        d="m6 12.5 4 4 8-9"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

export function ShieldCheckIcon({ className = "" }) {
  return (
    <Svg className={className}>
      <path
        d="M12 2 4 5.5v5.4c0 4.9 3.4 9.4 8 10.6 4.6-1.2 8-5.7 8-10.6V5.5L12 2Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path
        d="m8.8 12 2.2 2.2 4.2-4.4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

export function PillIcon({ className = "" }) {
  return (
    <Svg className={className}>
      <path
        d="M8 7.5h8a4.5 4.5 0 0 1 0 9H8a4.5 4.5 0 0 1 0-9Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path d="M12 7.5v9" fill="none" stroke="currentColor" strokeWidth="1.7" />
    </Svg>
  );
}

export function LayersIcon({ className = "" }) {
  return (
    <Svg className={className}>
      <path
        d="m12 3 9 5-9 5-9-5 9-5Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path
        d="m3 13 9 5 9-5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

export function RoleBadgeIcon({ className = "role-badge__icon" }) {
  return (
    <Svg className={className}>
      <rect
        x="4"
        y="8"
        width="16"
        height="9"
        rx="4.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
      />
      <path d="M4 12.5h16" fill="none" stroke="currentColor" strokeWidth="1.7" />
    </Svg>
  );
}
