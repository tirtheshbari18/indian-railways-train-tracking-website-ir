import React, { useState } from 'react';
import { X, Upload, CheckCircle2, AlertOctagon, FileText, Download, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { ImportValidationResult, ImportResult } from '../types';

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ImportModal: React.FC<ImportModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [entityType, setEntityType] = useState<'stations' | 'trains' | 'timetables'>('stations');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [validationResult, setValidationResult] = useState<ImportValidationResult | null>(null);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setValidationResult(null);
      setImportResult(null);
      setErrorMessage(null);
    }
  };

  const handleValidate = async () => {
    if (!selectedFile) return;
    setIsValidating(true);
    setErrorMessage(null);
    try {
      const res = await api.validateImport(entityType, selectedFile);
      setValidationResult(res);
    } catch (err: any) {
      setErrorMessage(err.message || 'File validation failed');
    } finally {
      setIsValidating(false);
    }
  };

  const handleExecute = async () => {
    if (!selectedFile) return;
    setIsExecuting(true);
    setErrorMessage(null);
    try {
      const res = await api.executeImport(entityType, selectedFile);
      setImportResult(res);
      onSuccess();
    } catch (err: any) {
      setErrorMessage(err.message || 'Import execution failed');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleDownloadTemplate = async (format: 'csv' | 'json') => {
    try {
      const content = await api.getImportTemplate(entityType, format);
      const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${entityType}_template.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to download template');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Upload className="w-5 h-5 text-amber-500" />
              <span>Bulk Data Import Console (CSV & JSON)</span>
            </h3>
            <p className="text-xs text-slate-400">Validated 2-stage import engine with audit trail recording</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm">
          {/* Entity Type Picker */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Select Dataset Category
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'stations', label: '1. Railway Stations', desc: 'Codes, zones, coordinates' },
                { id: 'trains', label: '2. Express Trains', desc: 'Numbers, routes, types' },
                { id: 'timetables', label: '3. Timetable Halts', desc: 'Stop sequences, timings' },
              ].map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => {
                    setEntityType(item.id as any);
                    setSelectedFile(null);
                    setValidationResult(null);
                    setImportResult(null);
                  }}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    entityType === item.id
                      ? 'bg-amber-950/40 border-amber-500 text-amber-300'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  <div className="font-semibold text-xs">{item.label}</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">{item.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Template Downloads */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs">
            <span className="text-slate-400 flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-slate-500" />
              Download standard schema template:
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => handleDownloadTemplate('csv')}
                className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-mono text-[11px] flex items-center gap-1"
              >
                <Download className="w-3 h-3" />
                <span>CSV Template</span>
              </button>
              <button
                type="button"
                onClick={() => handleDownloadTemplate('json')}
                className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-mono text-[11px] flex items-center gap-1"
              >
                <Download className="w-3 h-3" />
                <span>JSON Template</span>
              </button>
            </div>
          </div>

          {/* File Picker */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Upload File (.csv or .json)
            </label>
            <div className="border-2 border-dashed border-slate-700 hover:border-amber-500/60 rounded-xl p-6 text-center bg-slate-950/60 transition-colors">
              <input
                type="file"
                accept=".csv,.json"
                onChange={handleFileChange}
                className="hidden"
                id="file-import-input"
              />
              <label htmlFor="file-import-input" className="cursor-pointer">
                <Upload className="w-8 h-8 text-amber-500 mx-auto mb-2" />
                <div className="font-semibold text-slate-200">
                  {selectedFile ? selectedFile.name : 'Click to select or drag CSV / JSON file'}
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  Supported extensions: .csv, .json (max 10MB)
                </div>
              </label>
            </div>
          </div>

          {/* Error Message */}
          {errorMessage && (
            <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
              <AlertOctagon className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Validation Result Stage */}
          {validationResult && (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {validationResult.is_valid ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <AlertOctagon className="w-5 h-5 text-rose-400" />
                  )}
                  <span className="font-bold text-sm text-slate-200">
                    {validationResult.is_valid ? 'Validation Passed' : 'Validation Found Errors'}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs font-mono">
                  <span>Total: <strong>{validationResult.total_rows}</strong></span>
                  <span className="text-emerald-400">Valid: <strong>{validationResult.valid_rows_count}</strong></span>
                  <span className="text-rose-400">Errors: <strong>{validationResult.error_rows_count}</strong></span>
                </div>
              </div>

              {/* Errors List if any */}
              {validationResult.errors.length > 0 && (
                <div className="mt-2 max-h-36 overflow-y-auto space-y-1.5 pr-1">
                  <div className="text-xs font-semibold text-rose-400 mb-1">Row Errors Detail:</div>
                  {validationResult.errors.map((err, i) => (
                    <div key={i} className="text-xs p-2 rounded bg-rose-950/40 border border-rose-900/60 text-rose-300 flex items-start gap-2">
                      <span className="font-mono font-bold text-rose-200">Row {err.row_index}:</span>
                      <span>[{err.field}] {err.message}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Preview */}
              {validationResult.preview.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-slate-400 mb-1.5">Parsed Preview (First 5 records):</div>
                  <div className="overflow-x-auto">
                    <pre className="text-[11px] font-mono bg-slate-900 p-2.5 rounded-lg border border-slate-800 text-amber-300 max-h-32 overflow-y-auto">
                      {JSON.stringify(validationResult.preview, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Import Result */}
          {importResult && (
            <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/60 text-emerald-200 text-xs flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <div className="font-bold text-sm text-emerald-300 mb-1">Import Completed Successfully</div>
                <p>{importResult.message}</p>
                <div className="mt-2 text-slate-400 font-mono">
                  New records: {importResult.imported_count} • Updated: {importResult.updated_count}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer Buttons */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-slate-950">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-900 transition-colors"
          >
            Cancel
          </button>

          <div className="flex items-center gap-3">
            {selectedFile && !validationResult && (
              <button
                type="button"
                onClick={handleValidate}
                disabled={isValidating}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-amber-400 border border-slate-700 transition-all flex items-center gap-1.5"
              >
                {isValidating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : null}
                <span>Stage 1: Validate Schema</span>
              </button>
            )}

            {validationResult && validationResult.valid_rows_count > 0 && !importResult && (
              <button
                type="button"
                onClick={handleExecute}
                disabled={isExecuting}
                className="px-5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 transition-all shadow-md shadow-amber-500/20 flex items-center gap-1.5"
              >
                {isExecuting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : null}
                <span>Stage 2: Commit Valid Records ({validationResult.valid_rows_count})</span>
              </button>
            )}

            {importResult && (
              <button
                type="button"
                onClick={onClose}
                className="px-5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all"
              >
                Done
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
