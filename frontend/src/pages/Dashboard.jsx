import { useState, useEffect } from 'react'
import axios from 'axios'
import { Building2, Users, Receipt, KeyRound } from 'lucide-react'

const API_BASE_URL = 'http://localhost:8000/api'

export default function Dashboard() {
    const [stats, setStats] = useState({
        total_rooms: 0,
        total_capacity: 0,
        total_occupied: 0,
        total_students: 0,
        pending_fees: 0,
        available_slots: 0
    })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchStats()
    }, [])

    const fetchStats = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/dashboard`)
            setStats(res.data)
            setLoading(false)
        } catch (err) {
            console.error("Failed to load stats", err)
            setLoading(false)
        }
    }

    const StatCard = ({ title, value, icon: Icon, colorClass }) => (
        <div className="glass-card">
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px', gap: '12px' }}>
                <div className={`icon-wrapper ${colorClass}`} style={{ padding: '12px', borderRadius: '12px', background: `var(--${colorClass}-glow)`, color: `var(--${colorClass})` }}>
                    <Icon size={24} />
                </div>
                <h3 style={{ color: 'var(--text-secondary)', fontSize: '14px', fontWeight: '500' }}>{title}</h3>
            </div>
            <div style={{ fontSize: '32px', fontWeight: '700', color: 'var(--text-main)' }}>
                {value}
            </div>
        </div>
    )

    if (loading) return <div className="animate-fade-in"><h2 className="text-gradient">Loading Dashboard...</h2></div>

    return (
        <div className="animate-fade-in">
            <header style={{ marginBottom: '40px' }}>
                <h1 className="text-gradient" style={{ fontSize: '32px', marginBottom: '8px' }}>Welcome back, Manager</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Here's what's happening at HostelPro today.</p>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '24px', marginBottom: '40px' }}>
                <StatCard title="Total Rooms" value={stats.total_rooms} icon={Building2} colorClass="accent" />
                <StatCard title="Occupancy" value={`${stats.total_occupied} / ${stats.total_capacity}`} icon={Users} colorClass="success" />
                <StatCard title="Students" value={stats.total_students} icon={KeyRound} colorClass="warning" />
                <StatCard title="Pending Fees" value={stats.pending_fees} icon={Receipt} colorClass="error" />
            </div>

            <div className="glass-panel" style={{ padding: '32px' }}>
                <h2 style={{ marginBottom: '16px', fontSize: '20px' }}>Quick Overview</h2>
                <div style={{ display: 'flex', gap: '32px', color: 'var(--text-secondary)' }}>
                    <div>
                        <span style={{ display: 'block', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Total Capacity</span>
                        <span style={{ fontSize: '24px', color: 'var(--text-main)', fontWeight: '600' }}>{stats.total_capacity}</span>
                    </div>
                    <div>
                        <span style={{ display: 'block', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Occupied Beds</span>
                        <span style={{ fontSize: '24px', color: 'var(--text-main)', fontWeight: '600' }}>{stats.total_occupied}</span>
                    </div>
                    <div>
                        <span style={{ display: 'block', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Available Slots</span>
                        <span style={{ fontSize: '24px', color: 'var(--success)', fontWeight: '600' }}>{stats.available_slots}</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
