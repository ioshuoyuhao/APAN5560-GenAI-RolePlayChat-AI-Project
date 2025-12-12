import { Link, NavLink, Outlet } from 'react-router-dom';

/**
 * Main application layout with navigation sidebar
 */
export default function Layout() {
  const navItems = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/discover', label: 'Discover', icon: '🔍' },
    { path: '/characters', label: 'Characters', icon: '👤' },
    { path: '/chat', label: 'Chat', icon: '💬' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div className="min-h-screen flex">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-dark-900 border-r border-dark-700 flex flex-col">
        {/* Logo */}
        <div className="p-4 border-b border-dark-700">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl">🎭</span>
            <span className="text-xl font-bold text-primary-400">RPGChat.AI</span>
          </Link>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    isActive ? 'nav-link-active flex items-center gap-3' : 'nav-link flex items-center gap-3'
                  }
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-dark-700 text-dark-500 text-sm">
          <p>v0.1.0 - Under Development</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 bg-dark-950">
        <Outlet />
      </main>
    </div>
  );
}

