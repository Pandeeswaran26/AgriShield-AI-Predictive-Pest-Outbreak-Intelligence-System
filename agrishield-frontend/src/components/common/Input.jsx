export function Input({ label, error, className = "", ...props }) {
  return (
    <div className={className}>
      {label && <label className="mb-1.5 block text-sm font-medium">{label}</label>}
      <input className="input-field" {...props} />
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  );
}

export function Select({ label, error, options = [], placeholder, className = "", ...props }) {
  return (
    <div className={className}>
      {label && <label className="mb-1.5 block text-sm font-medium">{label}</label>}
      <select className="input-field" {...props}>
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value ?? opt} value={opt.value ?? opt}>
            {opt.label ?? opt}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  );
}

export default Input;
