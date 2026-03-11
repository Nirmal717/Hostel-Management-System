import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

export default function Rooms() {
    const [rooms, setRooms] = useState([])
    const [loading, setLoading] = useState(true)
    const [newRoom, setNewRoom] = useState({ room_number: '', capacity: '', status: 'Available' })
    const [error, setError] = useState('')

    useEffect(() => {
        fetchRooms()
    }, [])

    const fetchRooms = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/rooms`)
            setRooms(res.data)
            setLoading(false)
        } catch (err) {
            console.error(err)
        }
    }

    const handleAddRoom = async (e) => {
        e.preventDefault()
        setError('')
        try {
            await axios.post(`${API_BASE_URL}/rooms`, {
                room_number: parseInt(newRoom.room_number),
                capacity: parseInt(newRoom.capacity),
                status: newRoom.status
            })
            setNewRoom({ room_number: '', capacity: '', status: 'Available' })
            fetchRooms()
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to add room')
        }
    }

    const handleDeleteRoom = async (room_number) => {
        if (!window.confirm(`Delete Room ${room_number}? This also deletes its allocations.`)) return
        try {
            await axios.delete(`${API_BASE_URL}/rooms/${room_number}`)
            fetchRooms()
        } catch (err) {
            alert('Failed to delete room')
        }
    }

    return (
        <div className="animate-fade-in">
            <header style={{ marginBottom: '40px' }}>
                <h1 className="text-gradient" style={{ fontSize: '32px', marginBottom: '8px' }}>Rooms Management</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Add new rooms and monitor current inventory.</p>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '32px' }}>
                {/* Form Panel */}
                <div className="glass-panel" style={{ padding: '32px', height: 'fit-content' }}>
                    <h2 style={{ marginBottom: '24px', fontSize: '20px' }}>Add New Room</h2>
                    {error && <div className="badge badge-error" style={{ marginBottom: '16px' }}>{error}</div>}
                    <form onSubmit={handleAddRoom}>
                        <div className="form-group">
                            <label className="form-label">Room Number</label>
                            <input
                                type="number"
                                className="form-control"
                                placeholder="e.g. 101"
                                value={newRoom.room_number}
                                onChange={e => setNewRoom({ ...newRoom, room_number: e.target.value })}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Maximum Capacity</label>
                            <input
                                type="number"
                                className="form-control"
                                placeholder="e.g. 2"
                                value={newRoom.capacity}
                                onChange={e => setNewRoom({ ...newRoom, capacity: e.target.value })}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Status</label>
                            <select
                                className="form-control form-select"
                                value={newRoom.status}
                                onChange={e => setNewRoom({ ...newRoom, status: e.target.value })}
                            >
                                <option value="Available">Available</option>
                                <option value="Maintenance">Maintenance</option>
                                <option value="Inactive">Inactive</option>
                            </select>
                        </div>
                        <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '8px' }}>Save Room</button>
                    </form>
                </div>

                {/* List Panel */}
                <div className="data-table-container">
                    <table style={{ width: '100%' }}>
                        <thead>
                            <tr>
                                <th>Room No</th>
                                <th>Capacity</th>
                                <th>Occupancy</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan="5" style={{ textAlign: 'center' }}>Loading...</td></tr>
                            ) : rooms.map(room => (
                                <tr key={room.room_number}>
                                    <td style={{ fontWeight: '600' }}>{room.room_number}</td>
                                    <td>{room.capacity} beds</td>
                                    <td>
                                        <span style={{ color: room.occupancy >= room.capacity ? 'var(--error)' : 'var(--text-main)' }}>
                                            {room.occupancy} / {room.capacity}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`badge ${room.status === 'Available' ? 'badge-success' : 'badge-warning'}`}>
                                            {room.status}
                                        </span>
                                    </td>
                                    <td>
                                        <button
                                            onClick={() => handleDeleteRoom(room.room_number)}
                                            className="btn btn-danger"
                                            style={{ padding: '6px 12px', fontSize: '13px', borderRadius: '8px' }}
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {rooms.length === 0 && !loading && (
                                <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No rooms found.</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
