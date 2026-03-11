import { useState, useEffect } from 'react'
import axios from 'axios'
import { UserPlus } from 'lucide-react'

const API_BASE_URL = 'http://localhost:8000/api'

export default function Students() {
    const [students, setStudents] = useState([])
    const [loading, setLoading] = useState(true)
    const [newStudent, setNewStudent] = useState({ name: '', contact: '' })
    const [message, setMessage] = useState({ text: '', type: '' })

    useEffect(() => {
        fetchStudents()
    }, [])

    const fetchStudents = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/students`)
            setStudents(res.data)
            setLoading(false)
        } catch (err) {
            console.error(err)
        }
    }

    const handleRegister = async (e) => {
        e.preventDefault()
        setMessage({ text: '', type: '' })
        try {
            await axios.post(`${API_BASE_URL}/students`, newStudent)
            setMessage({ text: `Student ${newStudent.name} registered successfully.`, type: 'success' })
            setNewStudent({ name: '', contact: '' })
            fetchStudents()
        } catch (err) {
            setMessage({ text: err.response?.data?.detail || 'Failed to register student', type: 'error' })
        }
    }

    return (
        <div className="animate-fade-in">
            <header style={{ marginBottom: '40px' }}>
                <h1 className="text-gradient" style={{ fontSize: '32px', marginBottom: '8px' }}>Register Student</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Add new students to the system before allocating rooms.</p>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 450px) 1fr', gap: '32px' }}>
                <div className="glass-panel" style={{ padding: '32px', height: 'fit-content' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
                        <div style={{ padding: '12px', borderRadius: '12px', background: 'var(--accent-glow)', color: 'var(--accent)' }}>
                            <UserPlus size={24} />
                        </div>
                        <h2 style={{ fontSize: '20px' }}>New Registration</h2>
                    </div>

                    {message.text && (
                        <div className={`badge badge-${message.type}`} style={{ marginBottom: '24px', display: 'block', padding: '12px 16px', borderRadius: '12px' }}>
                            {message.text}
                        </div>
                    )}

                    <form onSubmit={handleRegister}>
                        <div className="form-group">
                            <label className="form-label">Full Name</label>
                            <input
                                type="text"
                                className="form-control"
                                placeholder="Enter student's full name"
                                value={newStudent.name}
                                onChange={e => setNewStudent({ ...newStudent, name: e.target.value })}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Contact / Email</label>
                            <input
                                type="text"
                                className="form-control"
                                placeholder="Phone number or email"
                                value={newStudent.contact}
                                onChange={e => setNewStudent({ ...newStudent, contact: e.target.value })}
                            />
                        </div>
                        <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '16px' }}>Register Student</button>
                    </form>
                </div>

                <div className="data-table-container">
                    <table style={{ width: '100%' }}>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Contact</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan="3" style={{ textAlign: 'center' }}>Loading...</td></tr>
                            ) : students.map(s => (
                                <tr key={s.student_id}>
                                    <td style={{ color: 'var(--text-muted)' }}>#{s.student_id}</td>
                                    <td style={{ fontWeight: '500' }}>{s.name}</td>
                                    <td style={{ color: 'var(--text-secondary)' }}>{s.contact || 'N/A'}</td>
                                </tr>
                            ))}
                            {students.length === 0 && !loading && (
                                <tr><td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No students registered yet.</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
