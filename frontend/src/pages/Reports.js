import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Reports = () => {
  const [reportData, setReportData] = useState(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await axios.get('/api/reports'); 
        setReportData(response.data);
      } catch (error) {
        console.error('Error fetching report data:', error);
      }
    };

    fetchReports();
  }, []);

  return (
    <div>
      <h2>Reports Page</h2>
      {reportData ? (
        <div>
          <h3>Report Summary</h3>
          <p>{reportData.summary}</p>
        </div>
      ) : (
        <p>Loading report data...</p>
      )}
    </div>
  );
};

export default Reports;
