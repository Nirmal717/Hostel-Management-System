import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

export default function Allocations() {
    const [allocations, setAllocations] = useState([])
    const [dropdowns, setDropdowns] = useState({ students: [], rooms: [] })
    const [loading, setLoading] = useState(true)
    const [newAlloc, setNewAlloc] = useState({ student_id: '', room_number: '', monthly_rent: '' })
    const [message, setMessage] = useState({ text: '', type: '' })

    const fetchData = async () => {
        try {
            const [allocRes, dropRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/allocations`),
                axios.get(`${API_BASE_URL}/dropdowns`)
            ])
            setAllocations(allocRes.data)
            setDropdowns(dropRes.data)
            setLoading(false)
        } catch (err) {
            console.error(err)
        }
    }

    useEffect(() => {
        fetchData()
    }, [])

    const handleAllocate = async (e) => {
        e.preventDefault()
        if (!newAlloc.student_id || !newAlloc.room_number || !newAlloc.monthly_rent) {
            return setMessage({ text: 'Please fill all fields', type: 'error' })
        }
        try {
            await axios.post(`${API_BASE_URL}/allocations`, newAlloc)
            setMessage({ text: 'Allocation successful!', type: 'success' })
            setNewAlloc({ student_id: '', room_number: '', monthly_rent: '' })
            fetchData()
        } catch (err) {
            setMessage({ text: err.response?.data?.detail || 'Failed to allocate room', type: 'error' })
        }
    }

    const handleDelete = async (id) => {
        if (!window.confirm("Remove this allocation? This frees up the room.")) return
        try {
            await axios.delete(`${API_BASE_URL}/allocations/${id}`)
            fetchData()
        } catch (err) {
            alert('Failed to delete allocation')
        }
    }

    return (
        <div className="animate-fade-in">
            <header style={{ marginBottom: '40px' }}>
                <h1 className="text-gradient" style={{ fontSize: '32px', marginBottom: '8px' }}>Room Allocations</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Allocate rooms to students and manage existing allocations.</p>
            </header>

            <div className="glass-panel" style={{ padding: '32px', marginBottom: '40px' }}>
                <h2 style={{ marginBottom: '24px', fontSize: '20px' }}>New Allocation</h2>
                {message.text && (
                    <div className={`badge badge-${message.type}`} style={{ marginBottom: '24px', display: 'inline-block', padding: '10px 16px', borderRadius: '8px' }}>
                        {message.text}
                    </div>
                )}
                <form onSubmit={handleAllocate} style={{ display: 'flex', gap: '24px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
                    <div className="form-group" style={{ flex: 1, minWidth: '250px', marginBottom: 0 }}>
                        <label className="form-label">Student</label>
                        <select
                            className="form-control form-select"
                            value={newAlloc.student_id}
                            onChange={e => setNewAlloc({ ...newAlloc, student_id: e.target.value })}
                        >
                            <option value="">-- Select Student --</option>
                            {dropdowns.students.map(s => (
                                <option key={s.student_id} value={s.student_id}>{s.name}</option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group" style={{ flex: 1, minWidth: '250px', marginBottom: 0 }}>
                        <label className="form-label">Room</label>
                        <select
                            className="form-control form-select"
                            value={newAlloc.room_number}
                            onChange={e => setNewAlloc({ ...newAlloc, room_number: e.target.value })}
                        >
                            <option value="">-- Select Room --</option>
                            {dropdowns.rooms.map(r => (
                                <option key={r.room_number} value={r.room_number}>
                                    Room {r.room_number} ({r.capacity - r.occupancy} open)
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group" style={{ flex: 1, minWidth: '150px', marginBottom: 0 }}>
                        <label className="form-label">Monthly Rent ($)</label>
                        <input
                            type="number"
                            className="form-control"
                            placeholder="e.g. 5000"
                            value={newAlloc.monthly_rent}
                            onChange={e => setNewAlloc({ ...newAlloc, monthly_rent: e.target.value })}
                        />
                    </div>
                    <button type="submit" className="btn btn-primary" style={{ height: '52px' }}>Confirm Allocation</button>
                </form>
            </div>

            <div className="data-table-container">
                <table style={{ width: '100%' }}>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Student Name</th>
                            <th>Contact</th>
                            <th>Room</th>
                            <th>Date Allocated</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan="6" style={{ textAlign: 'center' }}>Loading...</td></tr>
                        ) : allocations.map(a => (
                            <tr key={a.allocation_id}>
                                <td style={{ color: 'var(--text-muted)' }}>#{a.allocation_id}</td>
                                <td style={{ fontWeight: '500' }}>{a.student_name}</td>
                                <td style={{ color: 'var(--text-secondary)' }}>{a.contact || 'N/A'}</td>
                                <td style={{ fontWeight: '600' }}>Room {a.room_number}</td>
                                <td style={{ color: 'var(--text-secondary)' }}>{new Date(a.allocation_date).toLocaleDateString()}</td>
                                <td>
                                    <button onClick={() => handleDelete(a.allocation_id)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: '13px', borderRadius: '8px' }}>
                                        Revoke
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {allocations.length === 0 && !loading && (
                            <tr><td colSpan="6" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No allocations found.</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
