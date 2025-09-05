import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Reports = () => {
  const [reportData, setReportData] = useState(null);

  // 假設你需要從 API 取得報告數據
  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await axios.get('/api/reports'); // 假設 API 路徑是 /api/reports
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
          {/* 你可以根據你的數據結構顯示更多的內容 */}
        </div>
      ) : (
        <p>Loading report data...</p>
      )}
    </div>
  );
};

export default Reports;
