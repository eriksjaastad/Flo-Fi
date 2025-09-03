
"use client";
import { useState } from "react";
import Papa from "papaparse";
import Dashboard from "@/components/Dashboard";

// Shared types
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

export default function Page() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const validateDate = (dateStr: any): Date | null => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return isNaN(date.getTime()) ? null : date;
  };

  const sanitizeString = (str: any): string => {
    if (typeof str !== 'string') return String(str || '');
    return str.replace(/<[^>]*>/g, '').trim(); // Remove HTML tags
  };

  const validateAmount = (amount: any): number => {
    const num = Number(amount);
    return isNaN(num) ? 0 : num;
  };

  function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    
    // File size check (10MB limit)
    if (f.size > 10 * 1024 * 1024) {
      setErr('File too large. Please upload a file smaller than 10MB.');
      return;
    }
    
    setIsLoading(true);
    setErr(null);
    
    Papa.parse<RawCSVRow>(f, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (res) => {
        setIsLoading(false);
        
        if (res.errors.length > 0) {
          setErr(`CSV parsing errors: ${res.errors.map(e => e.message).join(', ')}`);
          return;
        }
        
        // Validate required columns
        const requiredColumns = ['Date', 'Amount'];
        const firstRow = res.data[0];
        if (!firstRow) {
          setErr('CSV file appears to be empty.');
          return;
        }
        
        const missingColumns = requiredColumns.filter(col => !(col in firstRow));
        if (missingColumns.length > 0) {
          setErr(`Missing required columns: ${missingColumns.join(', ')}`);
          return;
        }
        
        // Process and validate data
        const validRows: Row[] = [];
        const errors: string[] = [];
        
        res.data.forEach((r, index) => {
          const date = validateDate(r.Date);
          if (!date) {
            errors.push(`Row ${index + 1}: Invalid date`);
            return;
          }
          
          const row: Row = {
            Date: date,
            Amount: validateAmount(r.Amount),
            Category: sanitizeString(r.Category),
            Merchant: sanitizeString(r.Merchant),
            Account: sanitizeString(r.Account),
          };
          
          validRows.push(row);
        });
        
        if (errors.length > 5) {
          setErr(`Too many validation errors (${errors.length}). Please check your CSV format.`);
          return;
        }
        
        if (errors.length > 0) {
          console.warn('CSV validation warnings:', errors);
        }
        
        if (validRows.length === 0) {
          setErr('No valid data rows found in CSV.');
          return;
        }
        
        setRows(validRows);
        setErr(null);
        
        // Safe localStorage with error handling
        try {
          const dataToStore = {
            data: validRows,
            timestamp: Date.now(),
            version: '1.0'
          };
          localStorage.setItem("monarch_csv_cached", JSON.stringify(dataToStore));
        } catch (storageError) {
          console.warn('Failed to cache data locally:', storageError);
          // Don't show error to user as this is not critical
        }
      },
      error: (e) => {
        setIsLoading(false);
        setErr(`Failed to parse CSV: ${String(e)}`);
      }
    });
  }

  function loadCache() {
    try {
      const raw = localStorage.getItem("monarch_csv_cached");
      if (!raw) {
        setErr('No cached data found.');
        return;
      }
      
      const cached = JSON.parse(raw);
      
      // Handle both old and new cache formats
      let data: Row[];
      if (cached.version && cached.data) {
        // New format
        data = cached.data;
      } else {
        // Old format (direct array)
        data = cached;
      }
      
      // Restore Date objects
      const restoredData = data.map((d: any): Row => ({
        ...d,
        Date: new Date(d.Date),
        Amount: validateAmount(d.Amount),
        Category: sanitizeString(d.Category),
        Merchant: sanitizeString(d.Merchant),
        Account: sanitizeString(d.Account),
      }));
      
      setRows(restoredData);
      setErr(null);
    } catch (e) {
      console.error('Cache load error:', e);
      setErr('Failed to load cached data. Please upload a new CSV file.');
      // Clear corrupted cache
      localStorage.removeItem("monarch_csv_cached");
    }
  }

  return (
    <main className="p-6 md:p-10 max-w-6xl mx-auto">
      <header className="mb-6">
        <h1 className="text-3xl font-bold">Personal Finance Playground</h1>
        <p className="opacity-80">Upload your Monarch CSV. Charts render locally in your browser. No scraping, no secrets.</p>
      </header>

      {!rows && (
        <div className="rounded-2xl bg-[var(--card)] p-6 mb-6">
          <div className="flex gap-4 items-center">
            <div className="flex flex-col gap-2">
              <label htmlFor="csv-upload" className="text-sm font-medium">
                Upload CSV File
              </label>
              <input 
                id="csv-upload"
                type="file" 
                accept=".csv,text/csv" 
                onChange={onFile} 
                disabled={isLoading}
                className="block file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-white/10 file:text-white hover:file:bg-white/20 disabled:opacity-50" 
                aria-describedby="csv-help"
              />
            </div>
            <button 
              onClick={loadCache} 
              disabled={isLoading}
              className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Load previously uploaded CSV data"
            >
              {isLoading ? 'Loading...' : 'Load last CSV'}
            </button>
          </div>
          {err && (
            <div role="alert" className="text-red-400 mt-3 p-3 bg-red-400/10 rounded-lg">
              <strong>Error:</strong> {err}
            </div>
          )}
          {isLoading && (
            <div className="text-blue-400 mt-3 p-3 bg-blue-400/10 rounded-lg">
              Processing CSV file...
            </div>
          )}
          <p id="csv-help" className="opacity-70 mt-4 text-sm">
            Tip: Export from Monarch → Settings → Data → Export CSV. Maximum file size: 10MB.
          </p>
        </div>
      )}

      {rows && <Dashboard rows={rows} />}
    </main>
  );
}
