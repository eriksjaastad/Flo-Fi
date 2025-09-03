// Shared types for the Flo-Fi dashboard

export type Row = {
  Date: Date;
  Merchant: string;
  Category: string;
  Amount: number;
  Account: string;
};

export type RawCSVRow = {
  Date: string;
  Merchant?: string;
  Category?: string;
  Amount: string | number;
  Account?: string;
  [key: string]: any;
};
