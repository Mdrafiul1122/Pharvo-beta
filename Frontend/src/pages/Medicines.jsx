import { useMemo, useState } from "react";
import AppShell from "../components/layout/AppShell";
import AppIcon from "../components/icons/AppIcon";
import "../styles/medicines.css";

// Temporary visual-only fixtures adapted from the Figma reference.
// Replace with server-backed medicine data during API integration.
const INITIAL_MEDICINES = [
  { id: "m1", name: "Napa 500mg", generic: "Paracetamol", manufacturer: "Beximco Pharma", category: "Analgesic", form: "Tablet", strength: "500mg", pcPrice: 2, stripPrice: 20, boxPrice: 200, stock: 1340, minStock: 500, expiry: "2026-12-31", restricted: false, active: true },
  { id: "m2", name: "Napa Extra", generic: "Paracetamol+Caffeine", manufacturer: "Beximco Pharma", category: "Analgesic", form: "Tablet", strength: "500/65mg", pcPrice: 3, stripPrice: 30, boxPrice: 300, stock: 980, minStock: 400, expiry: "2026-10-15", restricted: false, active: true },
  { id: "m3", name: "Seclo 20mg", generic: "Esomeprazole", manufacturer: "Eskayef", category: "Antacid", form: "Capsule", strength: "20mg", pcPrice: 8, stripPrice: 80, boxPrice: 480, stock: 890, minStock: 300, expiry: "2027-03-20", restricted: false, active: true },
  { id: "m4", name: "Sergel 20mg", generic: "Esomeprazole", manufacturer: "Square Pharma", category: "Antacid", form: "Capsule", strength: "20mg", pcPrice: 10, stripPrice: 100, boxPrice: 600, stock: 760, minStock: 300, expiry: "2026-11-30", restricted: false, active: true },
  { id: "m5", name: "Fexo 120mg", generic: "Fexofenadine", manufacturer: "Square Pharma", category: "Antihistamine", form: "Tablet", strength: "120mg", pcPrice: 15, stripPrice: 150, boxPrice: 1500, stock: 42, minStock: 200, expiry: "2026-09-20", restricted: false, active: true },
  { id: "m6", name: "Amoxicillin 250mg", generic: "Amoxicillin", manufacturer: "Incepta Pharma", category: "Antibiotic", form: "Capsule", strength: "250mg", pcPrice: 8, stripPrice: 80, boxPrice: 800, stock: 560, minStock: 300, expiry: "2026-08-30", restricted: false, active: true },
  { id: "m7", name: "Metformin 500mg", generic: "Metformin HCl", manufacturer: "Opsonin", category: "Diabetic", form: "Tablet", strength: "500mg", pcPrice: 5, stripPrice: 50, boxPrice: 500, stock: 1200, minStock: 400, expiry: "2027-06-30", restricted: false, active: true },
  { id: "m8", name: "Cefixime 200mg", generic: "Cefixime", manufacturer: "Incepta Pharma", category: "Antibiotic", form: "Capsule", strength: "200mg", pcPrice: 25, stripPrice: 250, boxPrice: 1250, stock: 34, minStock: 150, expiry: "2026-10-01", restricted: false, active: true },
  { id: "m9", name: "Vitamin D3 1000IU", generic: "Cholecalciferol", manufacturer: "ACI Limited", category: "Supplement", form: "Tablet", strength: "1000IU", pcPrice: 12, stripPrice: 120, boxPrice: 720, stock: 670, minStock: 200, expiry: "2027-01-31", restricted: false, active: true },
  { id: "m10", name: "ORS Sachet", generic: "Oral Rehydration Salts", manufacturer: "Renata Pharma", category: "Other", form: "Powder", strength: "Standard", pcPrice: 12, stripPrice: 12, boxPrice: 120, stock: 2000, minStock: 500, expiry: "2027-12-31", restricted: false, active: true },
  { id: "m11", name: "Tramadol 50mg", generic: "Tramadol HCl", manufacturer: "Square Pharma", category: "Analgesic", form: "Capsule", strength: "50mg", pcPrice: 18, stripPrice: 180, boxPrice: 1800, stock: 450, minStock: 200, expiry: "2027-04-30", restricted: true, active: true },
  { id: "m12", name: "Aspirin 75mg", generic: "Acetylsalicylic Acid", manufacturer: "Beximco Pharma", category: "Cardiac", form: "Tablet", strength: "75mg", pcPrice: 3, stripPrice: 42, boxPrice: 300, stock: 500, minStock: 200, expiry: "2027-02-28", restricted: false, active: true },
  { id: "m13", name: "Clopidogrel 75mg", generic: "Clopidogrel", manufacturer: "Renata Pharma", category: "Cardiac", form: "Tablet", strength: "75mg", pcPrice: 28, stripPrice: 392, boxPrice: 2800, stock: 280, minStock: 100, expiry: "2027-05-31", restricted: false, active: true },
  { id: "m14", name: "Omeprazole 20mg", generic: "Omeprazole", manufacturer: "ACI Limited", category: "Antacid", form: "Capsule", strength: "20mg", pcPrice: 6, stripPrice: 60, boxPrice: 360, stock: 0, minStock: 200, expiry: "2026-09-05", restricted: false, active: true },
  { id: "m15", name: "Insulin Glargine", generic: "Insulin Glargine", manufacturer: "Sanofi-Aventis", category: "Diabetic", form: "Injection", strength: "100IU/mL", pcPrice: 350, stripPrice: 350, boxPrice: 1750, stock: 8, minStock: 30, expiry: "2026-09-30", restricted: false, active: true },
  { id: "m16", name: "Metronidazole 400mg", generic: "Metronidazole", manufacturer: "Eskayef", category: "Antibiotic", form: "Tablet", strength: "400mg", pcPrice: 4, stripPrice: 40, boxPrice: 400, stock: 800, minStock: 300, expiry: "2026-12-15", restricted: false, active: true },
  { id: "m17", name: "Ranitidine 150mg", generic: "Ranitidine HCl", manufacturer: "Opsonin", category: "Antacid", form: "Tablet", strength: "150mg", pcPrice: 5, stripPrice: 50, boxPrice: 500, stock: 350, minStock: 200, expiry: "2026-08-22", restricted: false, active: false },
  { id: "m18", name: "Azithromycin 500mg", generic: "Azithromycin", manufacturer: "Incepta Pharma", category: "Antibiotic", form: "Tablet", strength: "500mg", pcPrice: 35, stripPrice: 105, boxPrice: 630, stock: 9, minStock: 50, expiry: "2026-10-30", restricted: false, active: true },
  { id: "m19", name: "Pantoprazole 40mg", generic: "Pantoprazole Sodium", manufacturer: "Beximco Pharma", category: "Antacid", form: "Tablet", strength: "40mg", pcPrice: 7, stripPrice: 98, boxPrice: 700, stock: 120, minStock: 200, expiry: "2027-07-31", restricted: false, active: true },
  { id: "m20", name: "Atorvastatin 20mg", generic: "Atorvastatin Calcium", manufacturer: "Square Pharma", category: "Cardiac", form: "Tablet", strength: "20mg", pcPrice: 15, stripPrice: 210, boxPrice: 1500, stock: 145, minStock: 200, expiry: "2027-09-30", restricted: false, active: true },
];

const MED_CATEGORIES = ["Analgesic", "Antacid", "Antibiotic", "Antihistamine", "Cardiac", "Diabetic", "Supplement", "Other"];
const MED_FORMS = ["Tablet", "Capsule", "Injection", "Powder", "Syrup", "Drop", "Gel", "Cream"];

function daysLeft(value) {
  const expiry = new Date(`${value}T00:00:00`);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.ceil((expiry.getTime() - today.getTime()) / 86400000);
}

function formatDate(value) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "2-digit",
  });
}

function Badge({ children, tone = "neutral", dot = false }) {
  return (
    <span className={`medicine-badge medicine-badge--${tone}`}>
      {dot ? <span className="medicine-badge-dot" aria-hidden="true" /> : null}
      {children}
    </span>
  );
}

function ModalShell({ children, onClose, labelledBy, className = "" }) {
  return (
    <div className="medicine-modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <section className={`medicine-modal ${className}`} role="dialog" aria-modal="true" aria-labelledby={labelledBy}>
        {children}
      </section>
    </div>
  );
}

function FormField({ label, children, span = 1 }) {
  return (
    <label className={`medicine-form-field medicine-form-field--span-${span}`}>
      <span>{label}</span>
      {children}
    </label>
  );
}

function MedicineFormModal({ mode, form, setForm, onSave, onClose }) {
  const isAdd = mode === "add";
  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }));
  const updateNumber = (field, value) => update(field, value === "" ? "" : Number(value));

  return (
    <ModalShell onClose={onClose} labelledBy="medicine-form-title" className="medicine-modal--form">
      <header className="medicine-modal-header">
        <div>
          <h2 id="medicine-form-title">{isAdd ? "Add New Medicine" : "Edit Medicine"}</h2>
          <p>Fill in the medicine details below</p>
        </div>
        <button type="button" className="medicine-modal-close" onClick={onClose} aria-label="Close dialog"><AppIcon name="close" size={18} /></button>
      </header>

      <div className="medicine-modal-body">
        <div className="medicine-form-grid">
          <FormField label="Medicine Name *" span={3}>
            <input value={form.name ?? ""} onChange={(e) => update("name", e.target.value)} placeholder="e.g. Napa 500mg" />
          </FormField>
          <FormField label="Generic Name" span={2}>
            <input value={form.generic ?? ""} onChange={(e) => update("generic", e.target.value)} placeholder="e.g. Paracetamol" />
          </FormField>
          <FormField label="Strength">
            <input value={form.strength ?? ""} onChange={(e) => update("strength", e.target.value)} placeholder="e.g. 500mg" />
          </FormField>
          <FormField label="Manufacturer" span={2}>
            <input value={form.manufacturer ?? ""} onChange={(e) => update("manufacturer", e.target.value)} placeholder="e.g. Beximco Pharma" />
          </FormField>
          <FormField label="Category">
            <select value={form.category ?? "Analgesic"} onChange={(e) => update("category", e.target.value)}>
              {MED_CATEGORIES.map((item) => <option key={item}>{item}</option>)}
            </select>
          </FormField>
          <FormField label="Dosage Form">
            <select value={form.form ?? "Tablet"} onChange={(e) => update("form", e.target.value)}>
              {MED_FORMS.map((item) => <option key={item}>{item}</option>)}
            </select>
          </FormField>
          <FormField label="PC Price (৳)">
            <input type="number" min="0" value={form.pcPrice ?? ""} onChange={(e) => updateNumber("pcPrice", e.target.value)} placeholder="0.00" />
          </FormField>
          <FormField label="Strip Price (৳)">
            <input type="number" min="0" value={form.stripPrice ?? ""} onChange={(e) => updateNumber("stripPrice", e.target.value)} placeholder="0.00" />
          </FormField>
          <FormField label="Box Price (৳)">
            <input type="number" min="0" value={form.boxPrice ?? ""} onChange={(e) => updateNumber("boxPrice", e.target.value)} placeholder="0.00" />
          </FormField>
          <FormField label="Stock Quantity (pcs)">
            <input type="number" min="0" value={form.stock ?? ""} onChange={(e) => updateNumber("stock", e.target.value)} placeholder="0" />
          </FormField>
          <FormField label="Minimum Stock Level">
            <input type="number" min="0" value={form.minStock ?? ""} onChange={(e) => updateNumber("minStock", e.target.value)} placeholder="100" />
          </FormField>
          <FormField label="Expiry Date *">
            <input type="date" value={form.expiry ?? ""} onChange={(e) => update("expiry", e.target.value)} />
          </FormField>
        </div>

        <div className="medicine-form-checks">
          <label><input type="checkbox" checked={Boolean(form.restricted)} onChange={(e) => update("restricted", e.target.checked)} /> Controlled / Restricted Medicine</label>
          {!isAdd ? <label><input type="checkbox" checked={form.active !== false} onChange={(e) => update("active", e.target.checked)} /> Active Status</label> : null}
        </div>
      </div>

      <footer className="medicine-modal-footer">
        <button type="button" className="medicine-secondary-button" onClick={onClose}>Cancel</button>
        <button type="button" className="medicine-primary-button" onClick={onSave}>{isAdd ? "Add Medicine" : "Save Changes"}</button>
      </footer>
    </ModalShell>
  );
}

function MedicineViewModal({ medicine, onClose, onEdit }) {
  const remaining = daysLeft(medicine.expiry);
  return (
    <ModalShell onClose={onClose} labelledBy="medicine-view-title" className="medicine-modal--view">
      <header className="medicine-modal-header medicine-modal-header--top">
        <div>
          <div className="medicine-view-title-line">
            <h2 id="medicine-view-title">{medicine.name}</h2>
            {medicine.restricted ? <span className="medicine-controlled-label">RESTRICTED</span> : null}
          </div>
          <p>{medicine.generic} · {medicine.strength} · {medicine.form}</p>
        </div>
        <button type="button" className="medicine-modal-close" onClick={onClose} aria-label="Close dialog"><AppIcon name="close" size={18} /></button>
      </header>

      <div className="medicine-modal-body medicine-view-body">
        <section>
          <h3 className="medicine-section-label">Pricing</h3>
          <div className="medicine-price-grid">
            {[['PC Price', `৳${medicine.pcPrice}`], ['Strip Price', `৳${medicine.stripPrice.toLocaleString()}`], ['Box Price', `৳${medicine.boxPrice.toLocaleString()}`]].map(([label, value]) => (
              <div className="medicine-price-card" key={label}><span>{label}</span><strong>{value}</strong></div>
            ))}
          </div>
        </section>
        <section>
          <h3 className="medicine-section-label">Details</h3>
          <div className="medicine-details-grid">
            <div><span>Manufacturer</span><strong>{medicine.manufacturer}</strong></div>
            <div><span>Category</span><strong>{medicine.category}</strong></div>
            <div><span>Dosage Form</span><strong>{medicine.form}</strong></div>
            <div><span>Current Stock</span><strong>{medicine.stock.toLocaleString()} pcs</strong></div>
            <div><span>Min. Stock Level</span><strong>{medicine.minStock.toLocaleString()} pcs</strong></div>
            <div><span>Expiry Date</span><strong>{formatDate(medicine.expiry)} {remaining > 0 ? `(${remaining}d)` : "(EXPIRED)"}</strong></div>
          </div>
        </section>
        <div className="medicine-view-badges">
          <Badge tone={medicine.active ? "success" : "neutral"} dot>{medicine.active ? "Active" : "Inactive"}</Badge>
          {medicine.restricted ? <Badge tone="danger" dot>Controlled / Restricted</Badge> : null}
          {remaining > 0 && remaining <= 30 ? <Badge tone="warning" dot>Expiring Soon</Badge> : null}
          {remaining <= 0 ? <Badge tone="danger" dot>Expired</Badge> : null}
          {medicine.stock === 0 ? <Badge tone="danger" dot>Out of Stock</Badge> : null}
          {medicine.stock > 0 && medicine.stock < medicine.minStock ? <Badge tone="amber" dot>Low Stock</Badge> : null}
        </div>
      </div>

      <footer className="medicine-modal-footer">
        <button type="button" className="medicine-secondary-button" onClick={onClose}>Close</button>
        <button type="button" className="medicine-primary-button medicine-button-with-icon" onClick={onEdit}><AppIcon name="edit" size={14} /> Edit Medicine</button>
      </footer>
    </ModalShell>
  );
}

function DeleteMedicineModal({ medicine, onClose, onConfirm }) {
  return (
    <ModalShell onClose={onClose} labelledBy="delete-medicine-title" className="medicine-modal--delete">
      <div className="medicine-delete-body">
        <div className="medicine-delete-icon"><AppIcon name="trash" size={20} /></div>
        <h2 id="delete-medicine-title">Delete {medicine.name}?</h2>
        <p>This will permanently remove this medicine from your catalog. This action cannot be undone.</p>
      </div>
      <div className="medicine-delete-actions">
        <button type="button" className="medicine-secondary-button" onClick={onClose}>Cancel</button>
        <button type="button" className="medicine-danger-button" onClick={onConfirm}>Delete Medicine</button>
      </div>
    </ModalShell>
  );
}

function MedicineRow({ medicine, onView, onEdit, onDelete }) {
  const remaining = daysLeft(medicine.expiry);
  const stockTone = medicine.stock === 0 ? "danger" : medicine.stock < medicine.minStock * 0.3 ? "danger" : medicine.stock < medicine.minStock ? "warning" : "normal";
  const expiryTone = remaining <= 30 ? "danger" : remaining <= 60 ? "warning" : "normal";

  return (
    <tr>
      <td className="medicine-name-cell">
        <div className="medicine-name-line">
          <strong>{medicine.name}</strong>
          {medicine.restricted ? <span className="medicine-controlled-label">CTRL</span> : null}
        </div>
        <span>{medicine.form}</span>
      </td>
      <td className="medicine-muted-cell">{medicine.generic}</td>
      <td>{medicine.manufacturer}</td>
      <td><Badge tone="blue">{medicine.category}</Badge></td>
      <td className="medicine-muted-cell">{medicine.strength}</td>
      <td className="medicine-price-cell">৳{medicine.pcPrice}</td>
      <td>৳{medicine.stripPrice.toLocaleString()}</td>
      <td>৳{medicine.boxPrice.toLocaleString()}</td>
      <td><strong className={`medicine-stock medicine-stock--${stockTone}`}>{medicine.stock.toLocaleString()}</strong></td>
      <td><span className={`medicine-expiry medicine-expiry--${expiryTone}`}>{formatDate(medicine.expiry)}</span></td>
      <td><Badge tone={medicine.active ? "success" : "neutral"} dot>{medicine.active ? "Active" : "Inactive"}</Badge></td>
      <td>
        <div className="medicine-row-actions">
          <button type="button" onClick={onView} aria-label={`View ${medicine.name}`}><AppIcon name="eye" size={13} /></button>
          <button type="button" onClick={onEdit} aria-label={`Edit ${medicine.name}`}><AppIcon name="edit" size={13} /></button>
          <button type="button" className="is-danger" onClick={onDelete} aria-label={`Delete ${medicine.name}`}><AppIcon name="trash" size={13} /></button>
        </div>
      </td>
    </tr>
  );
}

export default function Medicines() {
  const [medicines, setMedicines] = useState(INITIAL_MEDICINES);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [manufacturer, setManufacturer] = useState("All");
  const [formFilter, setFormFilter] = useState("All");
  const [status, setStatus] = useState("All");
  const [modal, setModal] = useState(null);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({});

  const categories = useMemo(() => ["All", ...new Set(medicines.map((item) => item.category).sort())], [medicines]);
  const manufacturers = useMemo(() => ["All", ...new Set(medicines.map((item) => item.manufacturer).sort())], [medicines]);
  const dosageForms = useMemo(() => ["All", ...new Set(medicines.map((item) => item.form).sort())], [medicines]);

  const filtered = medicines.filter((medicine) => {
    const query = search.trim().toLowerCase();
    const queryMatches = !query || [medicine.name, medicine.generic, medicine.manufacturer].some((value) => value.toLowerCase().includes(query));
    const statusMatches = status === "All" || (status === "Active" && medicine.active) || (status === "Inactive" && !medicine.active) || (status === "Restricted" && medicine.restricted);
    return queryMatches
      && (category === "All" || medicine.category === category)
      && (manufacturer === "All" || medicine.manufacturer === manufacturer)
      && (formFilter === "All" || medicine.form === formFilter)
      && statusMatches;
  });

  const openAdd = () => {
    setForm({ category: "Analgesic", form: "Tablet", restricted: false, active: true });
    setSelected(null);
    setModal("add");
  };
  const openEdit = (medicine) => { setSelected(medicine); setForm({ ...medicine }); setModal("edit"); };
  const openView = (medicine) => { setSelected(medicine); setModal("view"); };
  const openDelete = (medicine) => { setSelected(medicine); setModal("delete"); };
  const closeModal = () => { setModal(null); };

  const saveMedicine = () => {
    if (!String(form.name || "").trim()) return;
    const normalized = {
      generic: "", manufacturer: "", strength: "", pcPrice: 0, stripPrice: 0, boxPrice: 0,
      stock: 0, minStock: 0, expiry: "", restricted: false, active: true,
      ...form,
      name: String(form.name).trim(),
    };
    if (modal === "add") {
      setMedicines((current) => [...current, { ...normalized, id: `m${Date.now()}` }]);
    } else if (modal === "edit" && selected) {
      setMedicines((current) => current.map((medicine) => medicine.id === selected.id ? { ...medicine, ...normalized } : medicine));
    }
    closeModal();
  };

  const deleteMedicine = () => {
    if (selected) setMedicines((current) => current.filter((medicine) => medicine.id !== selected.id));
    closeModal();
  };

  const outOfStock = medicines.filter((item) => item.stock === 0).length;
  const lowStock = medicines.filter((item) => item.stock > 0 && item.stock < item.minStock).length;
  const inactive = medicines.filter((item) => !item.active).length;

  return (
    <AppShell activePage="medicines" title="Medicines" subtitle="Medicine catalog and pricing management">
      <section className="medicines-page" aria-labelledby="medicines-table-title">
        <div className="medicines-toolbar">
          <label className="medicines-search">
            <span className="sr-only">Search medicines</span>
            <AppIcon name="search" size={14} />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by name, generic or manufacturer..." />
          </label>

          <div className="medicines-filter-grid">
            <label><span className="sr-only">Category</span><select value={category} onChange={(e) => setCategory(e.target.value)}>{categories.map((item) => <option key={item}>{item}</option>)}</select></label>
            <label><span className="sr-only">Manufacturer</span><select value={manufacturer} onChange={(e) => setManufacturer(e.target.value)}>{manufacturers.map((item) => <option key={item}>{item}</option>)}</select></label>
            <label><span className="sr-only">Dosage form</span><select value={formFilter} onChange={(e) => setFormFilter(e.target.value)}>{dosageForms.map((item) => <option key={item}>{item}</option>)}</select></label>
            <label><span className="sr-only">Status</span><select value={status} onChange={(e) => setStatus(e.target.value)}>{["All", "Active", "Inactive", "Restricted"].map((item) => <option key={item}>{item}</option>)}</select></label>
          </div>

          <button type="button" className="medicine-primary-button medicines-add-button" onClick={openAdd}><AppIcon name="plus" size={15} /> Add Medicine</button>
        </div>

        <div className="medicines-table-card">
          <div className="medicines-table-scroll" role="region" aria-label="Medicines table" tabIndex="0">
            <table>
              <thead>
                <tr>
                  {['Medicine', 'Generic', 'Manufacturer', 'Category', 'Strength', 'PC', 'Strip', 'Box', 'Stock', 'Expiry', 'Status', 'Actions'].map((heading) => <th key={heading} scope="col">{heading}</th>)}
                </tr>
              </thead>
              <tbody>
                {filtered.length ? filtered.map((medicine) => (
                  <MedicineRow
                    key={medicine.id}
                    medicine={medicine}
                    onView={() => openView(medicine)}
                    onEdit={() => openEdit(medicine)}
                    onDelete={() => openDelete(medicine)}
                  />
                )) : (
                  <tr><td className="medicines-empty" colSpan="12">No medicines found matching your filters</td></tr>
                )}
              </tbody>
            </table>
          </div>
          <footer className="medicines-table-footer">
            <span id="medicines-table-title">Showing {filtered.length} of {medicines.length} medicines</span>
            <span>{outOfStock} out of stock · {lowStock} low stock · {inactive} inactive</span>
          </footer>
        </div>
      </section>

      {(modal === "add" || modal === "edit") ? <MedicineFormModal mode={modal} form={form} setForm={setForm} onSave={saveMedicine} onClose={closeModal} /> : null}
      {modal === "view" && selected ? <MedicineViewModal medicine={selected} onClose={closeModal} onEdit={() => openEdit(selected)} /> : null}
      {modal === "delete" && selected ? <DeleteMedicineModal medicine={selected} onClose={closeModal} onConfirm={deleteMedicine} /> : null}
    </AppShell>
  );
}
