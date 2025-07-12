import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [customers, setCustomers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerTransactions, setCustomerTransactions] = useState([]);
  const [customerBalance, setCustomerBalance] = useState(null);
  
  // Form states
  const [customerForm, setCustomerForm] = useState({ name: '', phone: '', notes: '' });
  const [transactionForm, setTransactionForm] = useState({
    customer_id: '',
    work_description: '',
    gold_in: 0,
    gold_out: 0,
    cash_in: 0,
    labour_charge: 0,
    remarks: ''
  });
  const [jobForm, setJobForm] = useState({
    customer_id: '',
    work_description: '',
    status: 'In Progress',
    expected_delivery: ''
  });

  // Fetch data functions
  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers`);
      setCustomers(response.data);
    } catch (error) {
      console.error('Error fetching customers:', error);
    }
  };

  const fetchTransactions = async () => {
    try {
      const response = await axios.get(`${API}/transactions`);
      setTransactions(response.data);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
  };

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API}/jobs`);
      setJobs(response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const fetchCustomerDetails = async (customerId) => {
    try {
      const [transactionsResponse, balanceResponse] = await Promise.all([
        axios.get(`${API}/transactions?customer_id=${customerId}`),
        axios.get(`${API}/customer/${customerId}/balance`)
      ]);
      setCustomerTransactions(transactionsResponse.data);
      setCustomerBalance(balanceResponse.data);
    } catch (error) {
      console.error('Error fetching customer details:', error);
    }
  };

  const handleCustomerClick = (customer) => {
    setSelectedCustomer(customer);
    fetchCustomerDetails(customer.id);
  };

  const handleBackToCustomers = () => {
    setSelectedCustomer(null);
    setCustomerTransactions([]);
    setCustomerBalance(null);
  };

  useEffect(() => {
    fetchDashboardStats();
    fetchCustomers();
    fetchTransactions();
    fetchJobs();
  }, []);

  // Form handlers
  const handleCustomerSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/customers`, customerForm);
      setCustomerForm({ name: '', phone: '', notes: '' });
      fetchCustomers();
      fetchDashboardStats();
      alert('Customer added successfully!');
    } catch (error) {
      console.error('Error adding customer:', error);
      alert('Error adding customer');
    } finally {
      setLoading(false);
    }
  };

  const handleTransactionSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const transactionData = {
        ...transactionForm,
        gold_in: parseFloat(transactionForm.gold_in) || 0,
        gold_out: parseFloat(transactionForm.gold_out) || 0,
        cash_in: parseFloat(transactionForm.cash_in) || 0,
        labour_charge: parseFloat(transactionForm.labour_charge) || 0
      };
      await axios.post(`${API}/transactions`, transactionData);
      setTransactionForm({
        customer_id: '',
        work_description: '',
        gold_in: 0,
        gold_out: 0,
        cash_in: 0,
        labour_charge: 0,
        remarks: ''
      });
      fetchTransactions();
      fetchDashboardStats();
      alert('Transaction added successfully!');
    } catch (error) {
      console.error('Error adding transaction:', error);
      alert('Error adding transaction');
    } finally {
      setLoading(false);
    }
  };

  const handleJobSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const jobData = {
        ...jobForm,
        expected_delivery: jobForm.expected_delivery || null
      };
      await axios.post(`${API}/jobs`, jobData);
      setJobForm({
        customer_id: '',
        work_description: '',
        status: 'In Progress',
        expected_delivery: ''
      });
      fetchJobs();
      fetchDashboardStats();
      alert('Job created successfully!');
    } catch (error) {
      console.error('Error creating job:', error);
      alert('Error creating job');
    } finally {
      setLoading(false);
    }
  };

  const updateJobStatus = async (jobId, newStatus) => {
    try {
      await axios.put(`${API}/jobs/${jobId}?status=${newStatus}`);
      fetchJobs();
      fetchDashboardStats();
    } catch (error) {
      console.error('Error updating job status:', error);
    }
  };

  // Render components
  const renderDashboard = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">📊 Dashboard</h2>
      {dashboardStats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-yellow-100 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-yellow-600">{dashboardStats.total_gold_balance}g</div>
            <div className="text-sm text-gray-600">Gold Balance</div>
          </div>
          <div className="bg-green-100 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">₹{dashboardStats.total_money_balance}</div>
            <div className="text-sm text-gray-600">Money Balance</div>
          </div>
          <div className="bg-blue-100 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-600">{dashboardStats.active_jobs_count}</div>
            <div className="text-sm text-gray-600">Active Jobs</div>
          </div>
          <div className="bg-purple-100 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-purple-600">{dashboardStats.total_customers}</div>
            <div className="text-sm text-gray-600">Customers</div>
          </div>
          <div className="bg-gray-100 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-gray-600">{dashboardStats.total_transactions}</div>
            <div className="text-sm text-gray-600">Transactions</div>
          </div>
        </div>
      )}
    </div>
  );

  const renderCustomers = () => {
    // If a customer is selected, show customer detail view
    if (selectedCustomer) {
      return renderCustomerDetail();
    }

    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">👥 Customer Management</h2>
        
        {/* Add Customer Form */}
        <form onSubmit={handleCustomerSubmit} className="mb-6 bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Add New Customer</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Customer Name"
              className="border rounded-lg px-3 py-2"
              value={customerForm.name}
              onChange={(e) => setCustomerForm({...customerForm, name: e.target.value})}
              required
            />
            <input
              type="tel"
              placeholder="Phone Number"
              className="border rounded-lg px-3 py-2"
              value={customerForm.phone}
              onChange={(e) => setCustomerForm({...customerForm, phone: e.target.value})}
            />
            <input
              type="text"
              placeholder="Notes"
              className="border rounded-lg px-3 py-2"
              value={customerForm.notes}
              onChange={(e) => setCustomerForm({...customerForm, notes: e.target.value})}
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="mt-4 bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Adding...' : 'Add Customer'}
          </button>
        </form>

        {/* Customer List */}
        <div className="overflow-x-auto">
          <p className="text-sm text-gray-600 mb-4">💡 Click on any customer name to view their transaction history</p>
          <table className="w-full border-collapse border border-gray-300">
            <thead className="bg-gray-100">
              <tr>
                <th className="border border-gray-300 px-4 py-2 text-left">Name</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Phone</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Notes</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Added</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr key={customer.id} className="hover:bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2">
                    <button
                      onClick={() => handleCustomerClick(customer)}
                      className="font-medium text-blue-600 hover:text-blue-800 hover:underline text-left"
                    >
                      {customer.name}
                    </button>
                  </td>
                  <td className="border border-gray-300 px-4 py-2">{customer.phone || '-'}</td>
                  <td className="border border-gray-300 px-4 py-2">{customer.notes || '-'}</td>
                  <td className="border border-gray-300 px-4 py-2">{new Date(customer.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderCustomerDetail = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header with back button */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <button
            onClick={handleBackToCustomers}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-2"
          >
            ← Back to Customers
          </button>
          <h2 className="text-2xl font-bold text-gray-800">📋 {selectedCustomer.name}'s Account</h2>
          <p className="text-gray-600">
            {selectedCustomer.phone && `📞 ${selectedCustomer.phone}`}
            {selectedCustomer.notes && ` • ${selectedCustomer.notes}`}
          </p>
        </div>
      </div>

      {/* Customer Balance Summary */}
      {customerBalance && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-yellow-100 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-yellow-600">{customerBalance.gold_balance}g</div>
            <div className="text-sm text-gray-600">Gold Balance</div>
          </div>
          <div className="bg-green-100 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">₹{customerBalance.money_balance}</div>
            <div className="text-sm text-gray-600">Money Balance</div>
          </div>
        </div>
      )}

      {/* Customer Transactions */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Transaction History ({customerTransactions.length} transactions)</h3>
        {customerTransactions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No transactions found for this customer</p>
            <button 
              onClick={() => setActiveTab('transactions')}
              className="mt-2 text-blue-600 hover:text-blue-800"
            >
              Add first transaction →
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300 text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border border-gray-300 px-2 py-2 text-left">Date</th>
                  <th className="border border-gray-300 px-2 py-2 text-left">Work Description</th>
                  <th className="border border-gray-300 px-2 py-2 text-left">Gold In</th>
                  <th className="border border-gray-300 px-2 py-2 text-left">Gold Out</th>
                  <th className="border border-gray-300 px-2 py-2 text-left">Cash In</th>
                  <th className="border border-gray-300 px-2 py-2 text-left">Labour</th>
                  <th className="border border-gray-300 px-2 py-2 text-left">Remarks</th>
                </tr>
              </thead>
              <tbody>
                {customerTransactions.map((transaction) => (
                  <tr key={transaction.id} className="hover:bg-gray-50">
                    <td className="border border-gray-300 px-2 py-2">{new Date(transaction.date).toLocaleDateString()}</td>
                    <td className="border border-gray-300 px-2 py-2 font-medium">{transaction.work_description}</td>
                    <td className="border border-gray-300 px-2 py-2 text-yellow-600">{transaction.gold_in}g</td>
                    <td className="border border-gray-300 px-2 py-2 text-red-600">{transaction.gold_out}g</td>
                    <td className="border border-gray-300 px-2 py-2 text-green-600">₹{transaction.cash_in}</td>
                    <td className="border border-gray-300 px-2 py-2 text-blue-600">₹{transaction.labour_charge}</td>
                    <td className="border border-gray-300 px-2 py-2">{transaction.remarks || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="mt-6 flex gap-4">
        <button 
          onClick={() => {
            setTransactionForm({...transactionForm, customer_id: selectedCustomer.id});
            setActiveTab('transactions');
          }}
          className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600"
        >
          Add Transaction
        </button>
        <button 
          onClick={() => {
            setJobForm({...jobForm, customer_id: selectedCustomer.id});
            setActiveTab('jobs');
          }}
          className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600"
        >
          Create Job
        </button>
      </div>
    </div>
  );

  const renderTransactions = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">💳 Transaction Ledger</h2>
      
      {/* Add Transaction Form */}
      <form onSubmit={handleTransactionSubmit} className="mb-6 bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Add New Transaction</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <select
            className="border rounded-lg px-3 py-2"
            value={transactionForm.customer_id}
            onChange={(e) => setTransactionForm({...transactionForm, customer_id: e.target.value})}
            required
          >
            <option value="">Select Customer</option>
            {customers.map(customer => (
              <option key={customer.id} value={customer.id}>{customer.name}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Work Description"
            className="border rounded-lg px-3 py-2 md:col-span-2"
            value={transactionForm.work_description}
            onChange={(e) => setTransactionForm({...transactionForm, work_description: e.target.value})}
            required
          />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Gold In (g)</label>
            <input
              type="number"
              step="0.001"
              placeholder="0.000"
              className="border rounded-lg px-3 py-2 w-full"
              value={transactionForm.gold_in}
              onChange={(e) => setTransactionForm({...transactionForm, gold_in: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Gold Out (g)</label>
            <input
              type="number"
              step="0.001"
              placeholder="0.000"
              className="border rounded-lg px-3 py-2 w-full"
              value={transactionForm.gold_out}
              onChange={(e) => setTransactionForm({...transactionForm, gold_out: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Cash In (₹)</label>
            <input
              type="number"
              step="0.01"
              placeholder="0.00"
              className="border rounded-lg px-3 py-2 w-full"
              value={transactionForm.cash_in}
              onChange={(e) => setTransactionForm({...transactionForm, cash_in: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Labour Charge (₹)</label>
            <input
              type="number"
              step="0.01"
              placeholder="0.00"
              className="border rounded-lg px-3 py-2 w-full"
              value={transactionForm.labour_charge}
              onChange={(e) => setTransactionForm({...transactionForm, labour_charge: e.target.value})}
            />
          </div>
        </div>
        <input
          type="text"
          placeholder="Remarks (optional)"
          className="border rounded-lg px-3 py-2 w-full mb-4"
          value={transactionForm.remarks}
          onChange={(e) => setTransactionForm({...transactionForm, remarks: e.target.value})}
        />
        <button 
          type="submit" 
          disabled={loading}
          className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 disabled:opacity-50"
        >
          {loading ? 'Adding...' : 'Add Transaction'}
        </button>
      </form>

      {/* Transaction List */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300 text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="border border-gray-300 px-2 py-2 text-left">Date</th>
              <th className="border border-gray-300 px-2 py-2 text-left">Customer</th>
              <th className="border border-gray-300 px-2 py-2 text-left">Work</th>
              <th className="border border-gray-300 px-2 py-2 text-left">Gold In</th>
              <th className="border border-gray-300 px-2 py-2 text-left">Gold Out</th>
              <th className="border border-gray-300 px-2 py-2 text-left">Cash In</th>
              <th className="border border-gray-300 px-2 py-2 text-left">Labour</th>
              <th className="border border-gray-300 px-2 py-2 text-left">Remarks</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((transaction) => (
              <tr key={transaction.id} className="hover:bg-gray-50">
                <td className="border border-gray-300 px-2 py-2">{new Date(transaction.date).toLocaleDateString()}</td>
                <td className="border border-gray-300 px-2 py-2 font-medium">{transaction.customer_name}</td>
                <td className="border border-gray-300 px-2 py-2">{transaction.work_description}</td>
                <td className="border border-gray-300 px-2 py-2 text-yellow-600">{transaction.gold_in}g</td>
                <td className="border border-gray-300 px-2 py-2 text-red-600">{transaction.gold_out}g</td>
                <td className="border border-gray-300 px-2 py-2 text-green-600">₹{transaction.cash_in}</td>
                <td className="border border-gray-300 px-2 py-2 text-blue-600">₹{transaction.labour_charge}</td>
                <td className="border border-gray-300 px-2 py-2">{transaction.remarks || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderJobs = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">🔨 Job Tracker</h2>
      
      {/* Add Job Form */}
      <form onSubmit={handleJobSubmit} className="mb-6 bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Create New Job</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <select
            className="border rounded-lg px-3 py-2"
            value={jobForm.customer_id}
            onChange={(e) => setJobForm({...jobForm, customer_id: e.target.value})}
            required
          >
            <option value="">Select Customer</option>
            {customers.map(customer => (
              <option key={customer.id} value={customer.id}>{customer.name}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Work Description"
            className="border rounded-lg px-3 py-2"
            value={jobForm.work_description}
            onChange={(e) => setJobForm({...jobForm, work_description: e.target.value})}
            required
          />
          <input
            type="date"
            className="border rounded-lg px-3 py-2"
            value={jobForm.expected_delivery}
            onChange={(e) => setJobForm({...jobForm, expected_delivery: e.target.value})}
          />
        </div>
        <button 
          type="submit" 
          disabled={loading}
          className="bg-orange-500 text-white px-6 py-2 rounded-lg hover:bg-orange-600 disabled:opacity-50"
        >
          {loading ? 'Creating...' : 'Create Job'}
        </button>
      </form>

      {/* Job List */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead className="bg-gray-100">
            <tr>
              <th className="border border-gray-300 px-4 py-2 text-left">Customer</th>
              <th className="border border-gray-300 px-4 py-2 text-left">Work Description</th>
              <th className="border border-gray-300 px-4 py-2 text-left">Status</th>
              <th className="border border-gray-300 px-4 py-2 text-left">Expected Delivery</th>
              <th className="border border-gray-300 px-4 py-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id} className="hover:bg-gray-50">
                <td className="border border-gray-300 px-4 py-2 font-medium">{job.customer_name}</td>
                <td className="border border-gray-300 px-4 py-2">{job.work_description}</td>
                <td className="border border-gray-300 px-4 py-2">
                  <span className={`px-2 py-1 rounded text-sm ${
                    job.status === 'In Progress' ? 'bg-yellow-100 text-yellow-800' :
                    job.status === 'Completed' ? 'bg-blue-100 text-blue-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {job.status}
                  </span>
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {job.expected_delivery ? new Date(job.expected_delivery).toLocaleDateString() : '-'}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  <select
                    className="border rounded px-2 py-1 text-sm"
                    value={job.status}
                    onChange={(e) => updateJobStatus(job.id, e.target.value)}
                  >
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                    <option value="Delivered">Delivered</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-yellow-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold">✨ Goldsmith Ledger</h1>
          <p className="text-yellow-100">Digital ledger for your goldsmith business</p>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-md">
        <div className="container mx-auto px-4">
          <div className="flex space-x-8">
            {[
              { id: 'dashboard', label: '📊 Dashboard' },
              { id: 'customers', label: '👥 Customers' },
              { id: 'transactions', label: '💳 Transactions' },
              { id: 'jobs', label: '🔨 Jobs' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-yellow-500 text-yellow-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'customers' && renderCustomers()}
        {activeTab === 'transactions' && renderTransactions()}
        {activeTab === 'jobs' && renderJobs()}
      </main>
    </div>
  );
}

export default App;