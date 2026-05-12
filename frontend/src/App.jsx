import React, { useState, useEffect } from 'react';
import { LayoutDashboard, CarFront, Users, FileText, CreditCard, X, Menu, Trash2, CheckCircle, Trophy } from 'lucide-react';
import './index.css';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [alert, setAlert] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const showAlert = (message, type = 'success') => {
    setAlert({ message, type });
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(() => setAlert(null), 4000);
  };

  const apiCall = async (endpoint, method = 'GET', body = null) => {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) options.body = JSON.stringify(body);
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, options);
      if (!res.ok) {
        let err;
        try { err = await res.json(); } catch(e) { err = await res.text(); }
        throw new Error(err.detail ? JSON.stringify(err.detail) : 'API Error');
      }
      return res.status === 204 ? null : await res.json();
    } catch (e) {
      showAlert(e.message, 'danger');
      throw e;
    }
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'cars', label: 'Cars Fleet', icon: CarFront },
    { id: 'customers', label: 'Customers', icon: Users },
    { id: 'rentals', label: 'Rentals Ledger', icon: FileText },
    { id: 'payments', label: 'Payments', icon: CreditCard },
  ];

  const handleTabChange = (id) => {
    setCurrentTab(id);
    setIsSidebarOpen(false); // Close sidebar on mobile after clicking
  };

  return (
    <div className="dashboard-layout">
      {/* Mobile Sidebar Overlay */}
      <div
        className={`sidebar-overlay ${isSidebarOpen ? 'open' : ''}`}
        onClick={() => setIsSidebarOpen(false)}
      />

      {/* Sidebar */}
      <aside className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div className="brand">
          <CarFront size={28} /> AutoRent
        </div>
        <nav>
          {tabs.map(t => (
            <button key={t.id} className={`nav-item ${currentTab === t.id ? 'active' : ''}`} onClick={() => handleTabChange(t.id)}>
              <t.icon size={20} /> {t.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Container */}
      <div className="main-wrapper">
        <header className="top-header">
          <button className="menu-toggle" onClick={() => setIsSidebarOpen(true)}>
            <Menu size={24} />
          </button>
          <div style={{ marginLeft: 'auto', fontWeight: '500', color: 'var(--text-muted)' }}>
            Admin Portal
          </div>
        </header>

        {/* Scrollable Content */}
        <main className="main-content" id="main-scroll">
          {alert && (
            <div className={`alert-message alert-${alert.type}`}>
              <span>{alert.message}</span>
              <button style={{background:'none', border:'none', cursor:'pointer', color:'inherit'}} onClick={() => setAlert(null)}>
                <X size={18} />
              </button>
            </div>
          )}

          <div className="fade-in-section" key={currentTab}>
            {currentTab === 'dashboard' && <Dashboard apiCall={apiCall} />}
            {currentTab === 'cars' && <Cars apiCall={apiCall} showAlert={showAlert} />}
            {currentTab === 'customers' && <Customers apiCall={apiCall} showAlert={showAlert} />}
            {currentTab === 'rentals' && <Rentals apiCall={apiCall} showAlert={showAlert} />}
            {currentTab === 'payments' && <Payments apiCall={apiCall} showAlert={showAlert} />}
          </div>
        </main>
      </div>
    </div>
  );
}

// --- Dashboard Component ---
function Dashboard({ apiCall }) {
  const [data, setData] = useState({ revenue: 0, mostRented: null, topCustomers: [], revByMonth: [] });

  useEffect(() => {
    async function load() {
      try {
        const [rev, topC, mostR, revM] = await Promise.all([
          apiCall('/reports/total-revenue'),
          apiCall('/reports/top-customers?limit=5'),
          apiCall('/reports/most-rented-car').catch(() => null),
          apiCall('/reports/revenue-by-month')
        ]);
        setData({
          revenue: rev.total_revenue || 0,
          topCustomers: topC,
          mostRented: mostR,
          revByMonth: revM
        });
      } catch (e) { console.error(e); }
    }
    load();
  }, [apiCall]);

  return (
    <div>
      <h2 className="section-header">Dashboard Overview</h2>

      <div className="card-grid">
        <div className="stat-card primary">
          <h3>Total Revenue</h3>
          <div className="value">${Number(data.revenue).toLocaleString()}</div>
        </div>
        {data.mostRented && (
          <div className="stat-card">
            <h3>Most Popular Car</h3>
            <div className="value" style={{fontSize:'1.8rem'}}>{data.mostRented.brand} {data.mostRented.model}</div>
            <p style={{color:'var(--text-muted)', marginTop:'0.5rem', fontWeight:'500'}}>{data.mostRented.rent_count} total rentals</p>
          </div>
        )}
      </div>

      <div className="card-grid" style={{gridTemplateColumns:'1fr 1fr'}}>
        <div className="content-card">
          <div className="card-header">Top Spenders</div>
          <div className="card-body p-0">
            <div className="table-responsive">
              <table>
                <thead><tr><th>Customer Name</th><th>Lifetime Value</th></tr></thead>
                <tbody>
                  {data.topCustomers.map((c, i) => (
                    <tr key={c.customer_id}>
                      <td style={{fontWeight: i === 0 ? '700' : '500', display: 'flex', alignItems: 'center', gap: '8px'}}>
                        {i === 0 && <Trophy size={16} color="#f59e0b" />} {c.full_name}
                      </td>
                      <td style={{fontWeight: '600', color: 'var(--success)'}}>${c.total_spent}</td>
                    </tr>
                  ))}
                  {data.topCustomers.length === 0 && <tr><td colSpan="2" style={{textAlign:'center'}}>No data available</td></tr>}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div className="content-card">
          <div className="card-header">Monthly Revenue Performance</div>
          <div className="card-body p-0">
            <div className="table-responsive">
              <table>
                <thead><tr><th>Timeline</th><th>Revenue Collected</th></tr></thead>
                <tbody>
                  {data.revByMonth.map(r => (
                    <tr key={r.month}>
                      <td style={{fontWeight:'500'}}>{new Date(r.month).toLocaleString('default', { month: 'long', year: 'numeric' })}</td>
                      <td style={{fontWeight:'600'}}>${r.total_revenue}</td>
                    </tr>
                  ))}
                  {data.revByMonth.length === 0 && <tr><td colSpan="2" style={{textAlign:'center'}}>No data available</td></tr>}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- Status Badge Helper ---
const StatusBadge = ({ status }) => {
  const map = {
    'available': 'success',
    'rented': 'warning',
    'maintenance': 'danger',
    'active': 'success',
    'completed': 'neutral',
    'cancelled': 'danger'
  };
  return <span className={`badge badge-${map[status] || 'neutral'}`}>{status}</span>;
}

// --- Cars Component ---
function Cars({ apiCall, showAlert }) {
  const [cars, setCars] = useState([]);
  const [form, setForm] = useState({ brand: '', model: '', year: 2022, price_per_day: '', status: 'available' });

  const load = async () => setCars(await apiCall('/cars'));
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await apiCall('/cars', 'POST', { ...form, year: Number(form.year), price_per_day: form.price_per_day });
    showAlert('New vehicle added to the fleet.');
    load();
    setForm({ brand: '', model: '', year: 2022, price_per_day: '', status: 'available' });
  };
  const handleDelete = async (id) => {
    if(!window.confirm('Delete this vehicle permanently?')) return;
    await apiCall(`/cars/${id}`, 'DELETE');
    showAlert('Vehicle removed from completely.');
    load();
  };

  return (
    <div>
      <h2 className="section-header">Fleet Management</h2>
      <p style={{color: 'var(--text-muted)', marginBottom: '2rem'}}>Manage your vehicle inventory and statuses.</p>
      <div className="form-card">
        <form onSubmit={handleSubmit} className="form-inline">
          <div className="form-group"><label>Brand</label><input className="form-control" required value={form.brand} onChange={e => setForm({...form, brand: e.target.value})} placeholder="Toyota" /></div>
          <div className="form-group"><label>Model</label><input className="form-control" required value={form.model} onChange={e => setForm({...form, model: e.target.value})} placeholder="Camry" /></div>
          <div className="form-group"><label>Year</label><input className="form-control" type="number" required value={form.year} onChange={e => setForm({...form, year: e.target.value})} /></div>
          <div className="form-group"><label>Price/Day ($)</label><input className="form-control" type="number" step="0.01" required value={form.price_per_day} onChange={e => setForm({...form, price_per_day: e.target.value})} /></div>
          <div className="form-group"><label>Status</label>
            <select className="form-control" value={form.status} onChange={e => setForm({...form, status: e.target.value})}>
              <option value="available">Available</option>
              <option value="rented">Rented</option>
              <option value="maintenance">Maintenance</option>
            </select>
          </div>
          <div className="form-group"><label>&nbsp;</label><button className="btn btn-primary" type="submit" style={{width: '100%'}}>Add Vehicle</button></div>
        </form>
      </div>

      <div className="content-card">
        <div className="card-header">Registered Vehicles</div>
        <div className="card-body p-0">
          <div className="table-responsive">
            <table>
              <thead><tr><th>ID</th><th>Vehicle</th><th>Year</th><th>Rate</th><th>Condition</th><th>Manage</th></tr></thead>
              <tbody>
                {cars.map(c => (
                  <tr key={c.id}>
                    <td>#{c.id}</td>
                    <td><div style={{fontWeight:'600'}}>{c.brand} {c.model}</div></td>
                    <td>{c.year}</td>
                    <td style={{fontWeight:'600'}}>${c.price_per_day}/day</td>
                    <td><StatusBadge status={c.status} /></td>
                    <td><button className="btn btn-danger" onClick={() => handleDelete(c.id)}><Trash2 size={16}/> Remove</button></td>
                  </tr>
                ))}
                {cars.length === 0 && <tr><td colSpan="6" style={{textAlign:'center', padding:'2rem'}}>No vehicles found</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- Customers Component ---
function Customers({ apiCall, showAlert }) {
  const [customers, setCustomers] = useState([]);
  const [form, setForm] = useState({ full_name: '', email: '', phone: '', driver_license_number: '' });

  const load = async () => setCustomers(await apiCall('/customers'));
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await apiCall('/customers', 'POST', form);
    showAlert('Client profile registered successfully.');
    load();
    setForm({ full_name: '', email: '', phone: '', driver_license_number: '' });
  };
  const handleDelete = async (id) => {
    if(!window.confirm('Delete this client record?')) return;
    await apiCall(`/customers/${id}`, 'DELETE');
    showAlert('Client record purged.');
    load();
  };

  return (
    <div>
      <h2 className="section-header">Client Directory</h2>
      <p style={{color: 'var(--text-muted)', marginBottom: '2rem'}}>Database of registered clients and their contact info.</p>
      <div className="form-card">
        <form onSubmit={handleSubmit} className="form-inline">
          <div className="form-group"><label>Full Name</label><input className="form-control" placeholder="John Doe" required value={form.full_name} onChange={e => setForm({...form, full_name: e.target.value})} /></div>
          <div className="form-group"><label>Email Address</label><input className="form-control" type="email" placeholder="john@example.com" required value={form.email} onChange={e => setForm({...form, email: e.target.value})} /></div>
          <div className="form-group"><label>Phone Number</label><input className="form-control" placeholder="+1 234 567 890" required value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} /></div>
          <div className="form-group"><label>Driver's License</label><input className="form-control" placeholder="DL-XXX-YYY" required value={form.driver_license_number} onChange={e => setForm({...form, driver_license_number: e.target.value})} /></div>
          <div className="form-group"><label>&nbsp;</label><button className="btn btn-primary" type="submit" style={{width: '100%'}}>Enroll Client</button></div>
        </form>
      </div>

      <div className="content-card">
        <div className="card-header">Active Profiles</div>
        <div className="card-body p-0">
          <div className="table-responsive">
            <table>
              <thead><tr><th>ID</th><th>Client Info</th><th>Contact Email</th><th>Phone</th><th>License Ref</th><th>Manage</th></tr></thead>
              <tbody>
                {customers.map(c => (
                  <tr key={c.id}>
                    <td>#{c.id}</td>
                    <td style={{fontWeight:'600'}}>{c.full_name}</td>
                    <td><a href={`mailto:${c.email}`} style={{color:'var(--primary)', textDecoration:'none'}}>{c.email}</a></td>
                    <td>{c.phone}</td>
                    <td><span className="badge badge-neutral">{c.driver_license_number}</span></td>
                    <td><button className="btn btn-danger" onClick={() => handleDelete(c.id)}><Trash2 size={16}/> Remove</button></td>
                  </tr>
                ))}
                {customers.length === 0 && <tr><td colSpan="6" style={{textAlign:'center', padding:'2rem'}}>No clients found</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- Rentals Component ---
function Rentals({ apiCall, showAlert }) {
  const [rentals, setRentals] = useState([]);
  const [form, setForm] = useState({ customer_id: '', car_id: '', start_date: '', end_date: '' });

  const load = async () => setRentals(await apiCall('/rentals'));
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await apiCall('/rentals', 'POST', {
      customer_id: Number(form.customer_id), car_id: Number(form.car_id),
      start_date: form.start_date, end_date: form.end_date
    });
    showAlert('Rental agreement initialized.');
    load();
    setForm({ customer_id: '', car_id: '', start_date: '', end_date: '' });
  };
  const handleComplete = async (id) => {
    if(!window.confirm('Process return and mark rental as completed?')) return;
    await apiCall(`/rentals/${id}`, 'PUT', { status: 'completed' });
    showAlert('Rental contract successfully concluded.');
    load();
  };

  return (
    <div>
      <h2 className="section-header">Lease Agreements</h2>
      <p style={{color: 'var(--text-muted)', marginBottom: '2rem'}}>Track active rentals and process newly drafted lease agreements.</p>
      <div className="form-card">
        <form onSubmit={handleSubmit} className="form-inline">
          <div className="form-group"><label>Customer ID</label><input className="form-control" type="number" required value={form.customer_id} onChange={e => setForm({...form, customer_id: e.target.value})} /></div>
          <div className="form-group"><label>Vehicle ID</label><input className="form-control" type="number" required value={form.car_id} onChange={e => setForm({...form, car_id: e.target.value})} /></div>
          <div className="form-group"><label>Pickup Date</label><input className="form-control" type="date" required value={form.start_date} onChange={e => setForm({...form, start_date: e.target.value})} /></div>
          <div className="form-group"><label>Return Date</label><input className="form-control" type="date" required value={form.end_date} onChange={e => setForm({...form, end_date: e.target.value})} /></div>
          <div className="form-group"><label>&nbsp;</label><button className="btn btn-primary" type="submit" style={{width: '100%'}}>Draft Agreement</button></div>
        </form>
      </div>

      <div className="content-card">
        <div className="card-header">Current Transactions</div>
        <div className="card-body p-0">
          <div className="table-responsive">
            <table>
              <thead><tr><th>Trx ID</th><th>References</th><th>Duration</th><th>Final Cost</th><th>State</th><th>Action</th></tr></thead>
              <tbody>
                {rentals.map(r => (
                  <tr key={r.id}>
                    <td style={{fontWeight:'600'}}>TRX-{r.id.toString().padStart(4, '0')}</td>
                    <td>
                      <div style={{display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.85rem'}}>
                        <div style={{display: 'flex', alignItems: 'center', gap: '6px'}}><Users size={14} color="var(--primary)"/> <span style={{fontWeight: '600', color: 'var(--text-main)'}}>Client #{r.customer_id}</span></div>
                        <div style={{display: 'flex', alignItems: 'center', gap: '6px'}}><CarFront size={14} color="var(--primary)"/> <span style={{fontWeight: '600', color: 'var(--text-main)'}}>Vehicle #{r.car_id}</span></div>
                      </div>
                    </td>
                    <td>
                      <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
                        <div>
                          <div style={{fontSize:'0.7rem', color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'0.05em'}}>Pick-up</div>
                          <div style={{fontWeight:'600', fontSize:'0.9rem'}}>{r.start_date}</div>
                        </div>
                        <div style={{color:'var(--text-muted)', fontWeight:'bold'}}>→</div>
                        <div>
                          <div style={{fontSize:'0.7rem', color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'0.05em'}}>Return</div>
                          <div style={{fontWeight:'600', fontSize:'0.9rem'}}>{r.end_date}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{fontWeight:'700', color:'var(--text-main)', fontSize:'1.05rem'}}>${r.total_price}</td>
                    <td><StatusBadge status={r.status} /></td>
                    <td className="table-actions" style={{ verticalAlign: 'middle' }}>
                      <div style={{ display: 'flex', alignItems: 'center', minHeight: '38px' }}>
                        {r.status === 'active' ? (
                          <button className="btn btn-success" onClick={() => handleComplete(r.id)}><CheckCircle size={16}/> Sign Off</button>
                        ) : (
                          <span style={{color:'var(--text-muted)', fontSize:'0.85rem', fontStyle:'italic'}}>Concluded</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {rentals.length === 0 && <tr><td colSpan="6" style={{textAlign:'center', padding:'2rem'}}>No rentals found</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- Payments Component ---
function Payments({ apiCall, showAlert }) {
  const [payments, setPayments] = useState([]);
  const [form, setForm] = useState({ rental_id: '', amount: '', payment_method: 'cash' });

  const load = async () => setPayments(await apiCall('/payments'));
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await apiCall('/payments', 'POST', {
      rental_id: Number(form.rental_id), amount: Number(form.amount), payment_method: form.payment_method
    });
    showAlert('Payment processed successfully. Funds registered.');
    load();
    setForm({ rental_id: '', amount: '', payment_method: 'cash' });
  };
  const handleDelete = async (id) => {
    if(!window.confirm('Delete payment record? This action represents a chargeback.')) return;
    await apiCall(`/payments/${id}`, 'DELETE');
    showAlert('Payment record reversed.');
    load();
  };

  return (
    <div>
      <h2 className="section-header">Financial Ledgers</h2>
      <p style={{color: 'var(--text-muted)', marginBottom: '2rem'}}>Process payments and manage financial records for all transactions.</p>
      <div className="form-card">
        <form onSubmit={handleSubmit} className="form-inline">
          <div className="form-group"><label>Rental ID</label><input className="form-control" type="number" required value={form.rental_id} onChange={e => setForm({...form, rental_id: e.target.value})} placeholder="e.g. 15" /></div>
          <div className="form-group"><label>Amount ($)</label><input className="form-control" type="number" step="0.01" required value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} placeholder="0.00" /></div>
          <div className="form-group"><label>Gateway</label>
            <select className="form-control" value={form.payment_method} onChange={e => setForm({...form, payment_method: e.target.value})}>
              <option value="card">Credit/Debit Card</option>
              <option value="bank_transfer">Wire Transfer</option>
              <option value="cash">Cash Deposit</option>
            </select>
          </div>
          <div className="form-group"><label>&nbsp;</label><button className="btn btn-primary" type="submit" style={{width: '100%'}}>Process Payment</button></div>
        </form>
      </div>

      <div className="content-card">
        <div className="card-header">Processed Invoices</div>
        <div className="card-body p-0">
          <div className="table-responsive">
            <table>
              <thead><tr><th>Invoice No.</th><th>Rental Ref</th><th>Total Paid</th><th>Gateway</th><th>Timestamp</th><th>Action</th></tr></thead>
              <tbody>
                {payments.map(p => (
                  <tr key={p.id}>
                    <td style={{fontWeight:'600'}}>INV-{p.id.toString().padStart(6, '0')}</td>
                    <td>TRX-{p.rental_id}</td>
                    <td style={{fontWeight:'700', color:'var(--success)'}}>${p.amount}</td>
                    <td><span className="badge badge-neutral">{p.payment_method.replace('_', ' ')}</span></td>
                    <td style={{fontSize:'0.85rem'}}>{new Date(p.payment_date).toLocaleString()}</td>
                    <td><button className="btn btn-danger" onClick={() => handleDelete(p.id)}><Trash2 size={16}/> Reverse</button></td>
                  </tr>
                ))}
                {payments.length === 0 && <tr><td colSpan="6" style={{textAlign:'center', padding:'2rem'}}>No payments registered</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
