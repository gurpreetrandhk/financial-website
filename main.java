import React, { useState, useEffect } from 'react';
import { PieChart, Pie, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { Trash2, PlusCircle, Save, FileText } from 'lucide-react';

// Mock API functions
const saveToDB = (data) => {
  localStorage.setItem('financialData', JSON.stringify(data));
  return Promise.resolve({ success: true });
};

const loadFromDB = () => {
  const data = localStorage.getItem('financialData');
  return Promise.resolve(data ? JSON.parse(data) : []);
};

export default function FinancialTracker() {
  const [transactions, setTransactions] = useState([]);
  const [newTransaction, setNewTransaction] = useState({
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    description: '',
    category: 'spending',
    amount: '',
    type: 'debit'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('chart');
  const [chartType, setChartType] = useState('line');
  const [categoryChartType, setCategoryChartType] = useState('pie'); // Added state for category chart type

  useEffect(() => {
    loadFromDB().then(data => {
      setTransactions(data);
      setIsLoading(false);
    });
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewTransaction({
      ...newTransaction,
      [name]: name === 'amount' ? parseFloat(value) || '' : value
    });
  };

  const addTransaction = () => {
    if (!newTransaction.description || !newTransaction.amount) {
      alert('Please fill in all fields');
      return;
    }

    const updatedTransactions = [
      ...transactions,
      { ...newTransaction, id: Date.now() }
    ];

    setTransactions(updatedTransactions);
    saveToDB(updatedTransactions);

    setNewTransaction({
      id: Date.now(),
      date: new Date().toISOString().split('T')[0],
      description: '',
      category: 'spending',
      amount: '',
      type: 'debit'
    });
  };

  const deleteTransaction = (id) => {
    const updatedTransactions = transactions.filter(t => t.id !== id);
    setTransactions(updatedTransactions);
    saveToDB(updatedTransactions);
  };

  const saveData = () => {
    saveToDB(transactions).then(() => {
      alert('Data saved successfully!');
    });
  };

  // Calculate total balance
  const calculateBalance = () => {
    return transactions.reduce((acc, transaction) => {
      if (transaction.type === 'credit') {
        return acc + transaction.amount;
      } else {
        return acc - transaction.amount;
      }
    }, 0);
  };

  // Group transactions by category for pie chart
    const getCategoryData = () => {
        const categories = {};

        transactions.forEach(transaction => {
            if (!categories[transaction.category]) {
                categories[transaction.category] = 0;
            }
            categories[transaction.category] += transaction.amount;
        });

        return Object.keys(categories).map(category => ({
            name: category,
            value: categories[category],
        }));
    };

  // Group transactions by date for line chart
  const getChartData = () => {
    // Create a map to store daily totals
    const dailyMap = {};

    // Process each transaction
    transactions.forEach(transaction => {
      if (!dailyMap[transaction.date]) {
        dailyMap[transaction.date] = {
          date: transaction.date,
          debit: 0,
          credit: 0,
          balance: 0,
          description: transaction.description
        };
      }

      if (transaction.type === 'debit') {
        dailyMap[transaction.date].debit += transaction.amount;
      } else {
        dailyMap[transaction.date].credit += transaction.amount;
      }
    });

    // Convert to array and sort by date
    const result = Object.values(dailyMap);
    result.sort((a, b) => new Date(a.date) - new Date(b.date));

    // Calculate running balance
    let runningBalance = 0;
    result.forEach(day => {
      runningBalance = runningBalance + day.credit - day.debit;
      day.balance = runningBalance;
    });

    return result;
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  const balance = calculateBalance();
  const chartData = getChartData();
  const categoryData = getCategoryData();

  const categoryColors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'];


  return (
    <div className="p-6 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">Financial Tracker</h1>
        <p className="text-gray-600 text-center">Track your spending, consumption, and savings</p>
      </header>

      <div className="mb-8 p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Add New Transaction</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input
              type="date"
              name="date"
              value={newTransaction.date}
              onChange={handleInputChange}
              className="w-full p-2 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <input
              type="text"
              name="description"
              value={newTransaction.description}
              onChange={handleInputChange}
              placeholder="Transaction description"
              className="w-full p-2 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Amount</label>
            <input
              type="number"
              name="amount"
              value={newTransaction.amount}
              onChange={handleInputChange}
              placeholder="0.00"
              min="0"
              step="0.01"
              className="w-full p-2 border rounded-md"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              name="category"
              value={newTransaction.category}
              onChange={handleInputChange}
              className="w-full p-2 border rounded-md"
            >
              <option value="spending">Spending</option>
              <option value="consumption">Consumption</option>
              <option value="saving">Saving</option>
              <option value="income">Income</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              name="type"
              value={newTransaction.type}
              onChange={handleInputChange}
              className="w-full p-2 border rounded-md"
            >
              <option value="debit">Debit (expense)</option>
              <option value="credit">Credit (income)</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={addTransaction}
              className="flex items-center bg-blue-600 text-white px-4 py-2 rounded-md w-full justify-center"
            >
              <PlusCircle size={16} className="mr-1" />
              Add Transaction
            </button>
          </div>
        </div>
      </div>

      <div className="mb-8 p-6 bg-white rounded-lg shadow-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Financial Summary</h2>
          <div className="flex space-x-4">
            <div
              className={`cursor-pointer px-3 py-1 ${activeTab === 'chart' ? 'bg-blue-100 font-medium rounded-md' : ''}`}
              onClick={() => setActiveTab('chart')}
            >
              Charts
            </div>
            <div
              className={`cursor-pointer px-3 py-1 ${activeTab === 'table' ? 'bg-blue-100 font-medium rounded-md' : ''}`}
              onClick={() => setActiveTab('table')}
            >
              Table
            </div>
          </div>
        </div>

        <div className="mb-6 p-4 bg-gray-50 rounded-md">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-gray-600">Total Debit</p>
              <p className="text-xl font-semibold text-red-600">
                ${transactions.filter(t => t.type === 'debit').reduce((sum, t) => sum + t.amount, 0).toFixed(2)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-gray-600">Total Credit</p>
              <p className="text-xl font-semibold text-green-600">
                ${transactions.filter(t => t.type === 'credit').reduce((sum, t) => sum + t.amount, 0).toFixed(2)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-gray-600">Balance</p>
              <p className={`text-xl font-semibold ${balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${balance.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        {activeTab === 'chart' && (
          <>
            <div className="mb-4 flex justify-end space-x-4">
                <select
                  value={chartType}
                  onChange={(e) => setChartType(e.target.value)}
                  className="p-2 border rounded-md"
                >
                  <option value="line">Line Chart</option>
                  <option value="bar">Bar Chart</option>
                  <option value="pie">Pie Chart</option>
                </select>
                <select
                    value={categoryChartType}
                    onChange={(e) => setCategoryChartType(e.target.value)}
                    className="p-2 border rounded-md"
                  >
                    <option value="pie">Category Pie Chart</option>
                    <option value="bar">Category Bar Chart</option>
                </select>
              </div>

            <div className="h-96 mb-8">
              <ResponsiveContainer width="100%" height="100%">
                {chartType === 'line' ? (
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="debit" stroke="#EF4444" name="Debit" />
                    <Line type="monotone" dataKey="credit" stroke="#10B981" name="Credit" />
                    <Line type="monotone" dataKey="balance" stroke="#3B82F6" name="Balance" />
                  </LineChart>
                ) : chartType === 'bar' ? (
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="debit" fill="#EF4444" name="Debit" />
                    <Bar dataKey="credit" fill="#10B981" name="Credit" />
                  </BarChart>
                ) : (
                  <PieChart>
                    <Pie
                      data={categoryData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={120}
                      //fill="#8884d8"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {categoryData.map((entry, index) => {
                        //const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A569BD', '#5DADE2'];
                        return <Cell key={`cell-${index}`} fill={categoryColors[index % categoryColors.length]} />;
                      })}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                )}
              </ResponsiveContainer>
            </div>
            <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
                {categoryChartType === 'pie' ? (
                <PieChart>
                    <Pie
                    data={categoryData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    //fill="#8884d8"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                    {categoryData.map((entry, index) => {
                        //const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A569BD', '#5DADE2'];
                      return <Cell key={`cell-${index}`} fill={categoryColors[index % categoryColors.length]} />;
                    })}
                    </Pie>
                    <Tooltip />
                </PieChart>
                ) : (
                    <BarChart data={categoryData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value"  fill="#8884d8" name="Category" >
                      {categoryData.map((entry, index) => (
                         <Cell key={`cell-${index}`} fill={categoryColors[index % categoryColors.length]} />
                      ))}
                    </Bar>
                    </BarChart>
                )}
            </ResponsiveContainer>
            </div>
          </>
        )}

        {activeTab === 'table' && (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {transactions.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500">No transactions yet</td>
                  </tr>
                ) : (
                  transactions
                    .sort((a, b) => new Date(b.date) - new Date(a.date))
                    .map(transaction => (
                      <tr key={transaction.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{transaction.date}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{transaction.description}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">{transaction.category}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">{transaction.type}</td>
                        <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${transaction.type === 'debit' ? 'text-red-600' : 'text-green-600'}`}>
                          ${transaction.amount.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => deleteTransaction(transaction.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 size={16} />
                          </button>
                        </td>
                      </tr>
                    ))
                )}
              </tbody>
            </table>
             <p className="mt-4 text-sm text-gray-500">
              This table displays your financial transactions, including the date, description, category, type (debit or credit), and amount.  You can delete transactions using the trash icon.
            </p>
          </div>
        )}
      </div>

      <div className="flex justify-end">
        <button
          onClick={saveData}
          className="flex items-center bg-green-600 text-white px-4 py-2 rounded-md"
        >
          <Save size={16} className="mr-1" />
          Save Data
        </button>
      </div>
    </div>
  );
}

