import { LayoutDashboard, Building2, UserPlus, KeyRound, Receipt } from 'lucide-react';

const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'rooms', label: 'Rooms Inventory', icon: Building2 },
    { id: 'students', label: 'Register Student', icon: UserPlus },
    { id: 'allocations', label: 'Allocations', icon: KeyRound },
    { id: 'billing', label: 'Fee Management', icon: Receipt },
];

export default function Sidebar({ activeTab, setActiveTab }) {
    return (
        <aside className="sidebar">
            <div className="logo">
                <Building2 size={28} className="text-gradient" />
                <span>HOSTEL<span style={{ color: 'var(--text-main)' }}>PRO</span></span>
            </div>

            <ul className="nav-links">
                {navItems.map(item => {
                    const Icon = item.icon;
                    return (
                        <li
                            key={item.id}
                            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                            onClick={() => setActiveTab(item.id)}
                        >
                            <Icon size={20} />
                            <span>{item.label}</span>
                        </li>
                    )
                })}
            </ul>
        </aside>
    )
}
