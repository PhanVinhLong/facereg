
import React from 'react';
import { LineChart, PieChart } from 'react-chartkick';
import 'chart.js';

import {
  Card, CardHeader, CardBody
} from "../../../_metronic/_partials/controls";

import detectionAPI from '../../utils/DetectionAPI';

export function DashboardPage() {

  const [detections, setDetections] = React.useState([]);
  const [chartData, setChartData] = React.useState({});
  const [pieChartData, setPieChartData] = React.useState([]);

  React.useEffect(() => {
    async function fetchData() {
      const result = await detectionAPI.getDetections();
      setDetections(result.data);

      let tmpData = {};
      let toDay = new Date();
      let startDay = new Date();
      startDay.setDate(startDay.getDate() - 15);
      tmpData[`${startDay.getFullYear()}-${startDay.getMonth()}-${startDay.getDate()}`] = 0;
      tmpData[`${toDay.getFullYear()}-${toDay.getMonth()}-${toDay.getDate()}`] = 0;

      let tmpPieData = {};

      result.data.forEach(d => {
        let dt = new Date(d.created_time);
        let key = `${dt.getFullYear()}-${dt.getMonth()}-${dt.getDate()}`
        if (dt >= startDay && dt <= toDay) {
          if (!(key in tmpData))
            tmpData[key] = 1;
          else
            tmpData[key] = tmpData[key] + 1;
        }
        if (!(d.detection_type in tmpPieData))
          tmpPieData[d.detection_type] = 1;
        else
          tmpPieData[d.detection_type] = tmpPieData[d.detection_type] + 1;
      });
      console.log(tmpPieData)
      setChartData(tmpData);
      setPieChartData(tmpPieData);
    }
    fetchData();
  }, []);

  return (
    <div>
      <Card>
        <CardHeader title={`Dashboard`} />
        <CardBody>
          <LineChart data={chartData} />
          <br />
          <div className="h5 text-center">
            Detection requests in 15 days
          </div>
          <br />
          <br />
          <br />
          <PieChart data={pieChartData} />
          <br />
          <div className="h5 text-center">
            Detection requests by types
          </div>
        </CardBody>
      </Card>
    </div>
  );
}