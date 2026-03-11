import { useState, useEffect } from 'react'
import axios from 'axios'
import { Receipt } from 'lucide-react'

const API_BASE_URL = 'http://localhost:8000/api'

export default function Billing() {
    const [allocations, setAllocations] = useState([])
    const [loading, setLoading] = useState(true)

    const fetchAllocations = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/allocations`)
            // Sort: Pending first, then by name
            const sorted = res.data.sort((a, b) => {
                if (a.fee_paid === b.fee_paid) return a.student_name.localeCompare(b.student_name)
                return a.fee_paid ? 1 : -1
            })
            setAllocations(sorted)
            setLoading(false)
        } catch (err) {
            console.error(err)
        }
    }

    useEffect(() => {
        fetchAllocations()
    }, [])

    const toggleFeeStatus = async (id) => {
        try {
            await axios.put(`${API_BASE_URL}/allocations/${id}/toggle-fee`)
            fetchAllocations()
        } catch (err) {
            alert("Failed to update status")
        }
    }

    // Derived concept for "Billing Cycle" based on allocation date to make it more "understandable" as requested
    const getBillingCycle = (dateString) => {
        const d = new Date(dateString)
        const month = d.toLocaleString('default', { month: 'long' })
        const year = d.getFullYear()
        return `${month} ${year}`
    }

    return (
        <div className="animate-fade-in">
            <header style={{ marginBottom: '40px' }}>
                <h1 className="text-gradient" style={{ fontSize: '32px', marginBottom: '8px' }}>Fee Management</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Track payments, billing cycles, and update student fee statuses.</p>
            </header>

            <div className="data-table-container">
                <table style={{ width: '100%' }}>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Student Name</th>
                            <th>Room</th>
                            <th>Billing Cycle</th>
                            <th>Monthly Rent</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan="7" style={{ textAlign: 'center' }}>Loading...</td></tr>
                        ) : allocations.map(a => (
                            <tr key={a.allocation_id}>
                                <td style={{ color: 'var(--text-muted)' }}>#{a.allocation_id}</td>
                                <td style={{ fontWeight: '500' }}>{a.student_name}</td>
                                <td>Room {a.room_number}</td>
                                <td style={{ color: 'var(--text-secondary)' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <Receipt size={14} />
                                        {getBillingCycle(a.allocation_date)}
                                    </div>
                                </td>
                                <td style={{ fontWeight: '600', color: 'var(--text-main)' }}>${a.monthly_rent}</td>
                                <td>
                                    <span className={`badge ${a.fee_paid ? 'badge-success' : 'badge-error'}`}>
                                        {a.fee_paid ? 'Paid' : 'Pending'}
                                    </span>
                                </td>
                                <td>
                                    <button
                                        onClick={() => toggleFeeStatus(a.allocation_id)}
                                        className={`btn ${a.fee_paid ? 'btn-outline' : 'btn-success'}`}
                                        style={{ padding: '6px 16px', fontSize: '13px', borderRadius: '8px' }}
                                    >
                                        {a.fee_paid ? 'Mark Unpaid' : 'Mark Paid'}
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {allocations.length === 0 && !loading && (
                            <tr><td colSpan="7" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No billing records found.</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
