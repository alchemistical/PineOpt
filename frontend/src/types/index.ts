export interface OHLCData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface ParsedOHLCData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface ChartData {
  candlestickData: ParsedOHLCData[];
  volumeData?: { time: number; value: number; color?: string }[];
}