import { OHLCData, ParsedOHLCData } from '../types';
import * as XLSX from 'xlsx';
import Papa from 'papaparse';

export const parseCSV = (file: File): Promise<OHLCData[]> => {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        try {
          const data = results.data as any[];
          const ohlcData = data.map((row) => ({
            time: row.time || row.Time || row.DATE || row.date || row.timestamp,
            open: parseFloat(row.open || row.Open || row.OPEN),
            high: parseFloat(row.high || row.High || row.HIGH),
            low: parseFloat(row.low || row.Low || row.LOW),
            close: parseFloat(row.close || row.Close || row.CLOSE),
            volume: row.volume || row.Volume ? parseFloat(row.volume || row.Volume) : undefined,
          }));
          resolve(ohlcData);
        } catch (error) {
          reject(error);
        }
      },
      error: (error) => reject(error),
    });
  });
};

export const parseExcel = async (file: File): Promise<OHLCData[]> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target?.result as ArrayBuffer);
        const workbook = XLSX.read(data, { type: 'array' });
        const worksheet = workbook.Sheets[workbook.SheetNames[0]];
        const jsonData = XLSX.utils.sheet_to_json(worksheet);
        
        const ohlcData = jsonData.map((row: any) => ({
          time: row.time || row.Time || row.DATE || row.date || row.timestamp || row.Timestamp || row.DateTime || row['Date Time'] || row['date time'],
          open: parseFloat(row.open || row.Open || row.OPEN || row.O || row.o),
          high: parseFloat(row.high || row.High || row.HIGH || row.H || row.h),
          low: parseFloat(row.low || row.Low || row.LOW || row.L || row.l),
          close: parseFloat(row.close || row.Close || row.CLOSE || row.C || row.c),
          volume: row.volume || row.Volume || row.VOLUME || row.V || row.v ? parseFloat(row.volume || row.Volume || row.VOLUME || row.V || row.v) : undefined,
        }));
        
        resolve(ohlcData);
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsArrayBuffer(file);
  });
};

export const convertToChartData = (data: OHLCData[]): ParsedOHLCData[] => {
  return data
    .filter(item => !isNaN(item.open) && !isNaN(item.high) && !isNaN(item.low) && !isNaN(item.close) && item.time)
    .map(item => {
      let timeValue: number;
      
      // Handle Excel serial date numbers
      if (typeof item.time === 'number' && item.time > 40000 && item.time < 100000) {
        // Excel serial date (days since 1900-01-01)
        timeValue = Math.floor((item.time - 25569) * 86400);
      } else {
        // Parse ISO date string or other date formats
        const date = new Date(item.time);
        if (isNaN(date.getTime())) {
          return null;
        }
        timeValue = Math.floor(date.getTime() / 1000);
      }
      
      return {
        time: timeValue,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      };
    })
    .filter((item): item is ParsedOHLCData => item !== null)
    .sort((a, b) => a.time - b.time);
};