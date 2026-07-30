import React, { useState } from 'react';
import { UserCheck, LogOut, ShieldCheck, ChevronDown } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function UserMenu() {
  const { user, logout, setIsAuthModalOpen } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  if (!user) {
    return (
      <button className="btn-secondary" style={{ borderRadius: '999px', padding: '6px 14px' }} onClick={() => setIsAuthModalOpen(true)}>
        <ShieldCheck size={14} />
        <span>Sign In</span>
      </button>
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      <button
        className="btn-user-avatar"
        onClick={() => setDropdownOpen(!dropdownOpen)}
      >
        <div className="avatar-circle">
          {user.name.charAt(0).toUpperCase()}
        </div>
        <span className="user-name">{user.name}</span>
        <ChevronDown size={14} />
      </button>

      {dropdownOpen && (
        <div className="user-dropdown-menu" onClick={() => setDropdownOpen(false)}>
          <div className="dropdown-user-info">
            <div className="dropdown-name">{user.name}</div>
            <div className="dropdown-email">{user.email}</div>
            <span className="provider-tag">{user.provider.toUpperCase()}</span>
          </div>

          <div className="dropdown-divider" />

          <button className="dropdown-item" onClick={() => setIsAuthModalOpen(true)}>
            <ShieldCheck size={14} />
            <span>Switch Account / OAuth</span>
          </button>

          <button className="dropdown-item danger" onClick={logout}>
            <LogOut size={14} />
            <span>Sign Out</span>
          </button>
        </div>
      )}
    </div>
  );
}
